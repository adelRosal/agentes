# Agente Hola Mundo con Gemini, DSPy y LiteLLM

Este proyecto implementa un agente básico que utiliza Gemini API a través de DSPy y LiteLLM. El agente está containerizado usando Docker para facilitar su despliegue y ejecución.

## Estructura del Proyecto

hola_mundo/
  ├── Dockerfile
  ├── docker-compose.yaml  
  ├── requirements.txt
  ├── src/
  │   └── agent.py
  ├── config/
  │   └── config.yaml
  └── README.md

## Prerrequisitos

- Docker y Docker Compose instalados
- Una API key de Google AI (Gemini)
- Python 3.9+

## Configuración

1. Clona este repositorio:

git clone <repository-url>
cd hola_mundo

2. Crea un archivo .env en la raíz del proyecto con tu API key de Gemini:

GEMINI_API_KEY=your_api_key_here

## Instalación y Ejecución

1. Construye la imagen de Docker:

docker compose build

2. Inicia el contenedor:

docker compose up

El agente estará disponible en http://localhost:4000

## Uso del Agente

El agente expone un endpoint REST que puedes usar para interactuar con él:

curl -X POST http://localhost:4000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user", 
        "content": "Hola, ¿cómo estás?"
      }
    ]
  }'

## Uso del Agente con Esquema Estructurado

El agente ahora utiliza un esquema de respuesta estructurado que proporciona información más detallada y organizada. Ejemplo de uso:

```bash

## Archivos del Proyecto

### Dockerfile

FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "src/agent.py"]

### docker-compose.yaml

version: '3.8'
services:
  agent:
    build: .
    ports:
      - "4000:4000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    volumes:
      - ./config:/app/config

### requirements.txt

dspy-ai
litellm>=1.10.1
google-generativeai>=0.3.0
flask>=2.0.0
python-dotenv>=0.19.0

### src/agent.py

import os
import dspy
import google.generativeai as genai
from flask import Flask, request, jsonify
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Configurar Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-pro')

# Configurar DSPy
lm = dspy.LM('gemini/gemini-1.5-pro')
dspy.configure(lm=lm)

@app.route('/chat/completions', methods=['POST'])
def chat():
    try:
        data = request.json
        messages = data.get('messages', [])
        
        # Procesar mensajes usando LiteLLM
        response = completion(
            model="gemini/gemini-1.5-pro",
            messages=messages
        )
        
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)

### config/config.yaml

model_list:
  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-1.5-pro
      api_key: os.environ/GEMINI_API_KEY

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/amazing-feature`)
3. Commit tus cambios (`git commit -m 'Add some amazing feature'`)
4. Push a la rama (`git push origin feature/amazing-feature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo LICENSE para más detalles.