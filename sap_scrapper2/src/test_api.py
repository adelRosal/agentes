from dotenv import load_dotenv
import os
import google.generativeai as genai
import json
import re

def clean_json_response(text: str) -> str:
    """Limpia la respuesta para obtener solo el JSON válido"""
    # Eliminar los delimitadores de código markdown
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'\s*```', '', text)
    return text.strip()

def test_api_key():
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("Error: GOOGLE_API_KEY no encontrada en variables de entorno")
        return
        
    try:
        print("\nProbando con Gemini API:")
        
        # Configurar el modelo
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Crear el prompt
        prompt = """
        Return a JSON response with the following structure:
        {
            "test": "successful",
            "timestamp": "current_time"
        }
        
        The response must be valid JSON. Do not include markdown code blocks.
        """
        
        # Generar respuesta
        response = model.generate_content(prompt)
        
        print("\nRespuesta completa:", response.text)
        
        try:
            # Limpiar y parsear la respuesta
            clean_response = clean_json_response(response.text)
            print("\nRespuesta limpia:", clean_response)
            
            json_response = json.loads(clean_response)
            print("✓ Test exitoso!")
            print("JSON parseado:", json.dumps(json_response, indent=2))
        except json.JSONDecodeError as e:
            print("❌ Error: La respuesta no es un JSON válido")
            print("Error:", str(e))
            print("Respuesta recibida:", response.text)
        
    except Exception as e:
        print("❌ Error al probar API key:", str(e))
        print("Tipo de error:", type(e))

if __name__ == "__main__":
    test_api_key() 