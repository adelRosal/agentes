import os
import dspy
import google.generativeai as genai
from flask import Flask, request, jsonify
from litellm import completion
from dotenv import load_dotenv
from typing import List, Optional
from pydantic import BaseModel, Field

load_dotenv()

app = Flask(__name__)

# Configurar Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-pro')

# Configurar DSPy
lm = dspy.LM('gemini/gemini-1.5-pro')
dspy.configure(lm=lm)

# Definir esquemas de respuesta
class ThoughtProcess(BaseModel):
    reasoning: str = Field(description="Razonamiento detrás de la respuesta")
    references: Optional[List[str]] = Field(default=None, description="Referencias o fuentes relevantes")

class ResponseContent(BaseModel):
    main_answer: str = Field(description="Respuesta principal a la pregunta")
    additional_info: Optional[str] = Field(default=None, description="Información adicional relevante")
    examples: Optional[List[str]] = Field(default=None, description="Ejemplos si son aplicables")
    thought_process: ThoughtProcess = Field(description="Proceso de pensamiento detrás de la respuesta")

class GeminiResponse(BaseModel):
    response: ResponseContent
    confidence_score: float = Field(ge=0, le=1, description="Nivel de confianza en la respuesta")
    topics: List[str] = Field(description="Temas principales abordados en la respuesta")

def structure_prompt(content: str) -> str:
    return f"""
    Por favor, proporciona una respuesta estructurada a la siguiente consulta:
    {content}
    
    Tu respuesta debe incluir:
    1. Una respuesta principal clara y concisa
    2. Información adicional relevante si es necesaria
    3. Ejemplos específicos cuando sea apropiado
    4. Tu proceso de razonamiento
    5. Referencias relevantes si aplican
    6. Un nivel de confianza en tu respuesta
    7. Los temas principales que abordaste
    """

@app.route('/chat/completions', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        # Obtener el último mensaje del usuario
        user_message = messages[-1]['content'] if messages else ""
        structured_prompt = structure_prompt(user_message)
        
        # Procesar mensajes usando LiteLLM con el prompt estructurado
        response = completion(
            model="gemini/gemini-1.5-pro",
            messages=[{"role": "user", "content": structured_prompt}]
        )
        
        # Procesar la respuesta para ajustarla al esquema
        content = response.choices[0].message.content
        
        # Usar Gemini para estructurar la respuesta según nuestro esquema
        schema_prompt = f"""
        Analiza la siguiente respuesta y estructúrala según el esquema definido:
        {content}
        
        Devuelve la respuesta en formato JSON siguiendo exactamente esta estructura:
        {{
            "response": {{
                "main_answer": "respuesta principal",
                "additional_info": "información adicional",
                "examples": ["ejemplo1", "ejemplo2"],
                "thought_process": {{
                    "reasoning": "razonamiento",
                    "references": ["referencia1", "referencia2"]
                }}
            }},
            "confidence_score": 0.95,
            "topics": ["tema1", "tema2"]
        }}
        """
        
        schema_response = model.generate_content(schema_prompt)
        structured_data = schema_response.text
        
        # Formatear la respuesta final
        formatted_response = {
            "id": response.id,
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": structured_data
                },
                "finish_reason": response.choices[0].finish_reason
            }],
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
        return jsonify(formatted_response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000) 