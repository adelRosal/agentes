import os
import json
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
import re

class SAPAgent:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY no encontrada en variables de entorno")
            
        # Configurar Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')

    def _clean_json_response(self, text: str) -> str:
        """Limpia la respuesta para obtener solo el JSON válido"""
        # Eliminar los delimitadores de código markdown
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'\s*```', '', text)
        return text.strip()

    def _make_completion(self, prompt: str) -> Dict:
        """Método helper para hacer completions con manejo de errores"""
        try:
            print(f"Usando API key: {self.api_key[:10]}...")
            
            # Agregar instrucción explícita para JSON
            prompt_with_json = f"""
            Analiza la siguiente información y devuelve un JSON válido.
            No incluyas bloques de código markdown.

            {prompt}

            La respuesta DEBE ser un JSON válido y bien formateado.
            """
            
            response = self.model.generate_content(prompt_with_json)
            
            print("\nRespuesta completa:", response.text)
            
            try:
                clean_response = self._clean_json_response(response.text)
                print("\nRespuesta limpia:", clean_response)
                return json.loads(clean_response)
            except json.JSONDecodeError as e:
                print(f"Error decodificando JSON: {e}")
                print("Contenido recibido:", response.text)
                return {}
            
        except Exception as e:
            print(f"Error en completion: {str(e)}")
            print(f"Tipo de error: {type(e)}")
            return {}

    def interpret_table_structure(self, html_content: str) -> Dict[str, Any]:
        """Interpreta la estructura de una tabla SAP desde el HTML usando Gemini"""
        prompt = f"""
        Analiza el siguiente HTML de una tabla SAP y extrae su estructura.
        Identifica:
        1. Nombre de la tabla
        2. Descripción
        3. Categoría
        4. Campos y sus propiedades
        
        HTML:
        {html_content}
        
        Responde en formato JSON siguiendo esta estructura:
        {{
            "table_name": str,
            "description": str,
            "category": str,
            "fields": [
                {{
                    "name": str,
                    "description": str,
                    "data_type": str,
                    "is_key": bool,
                    "is_nullable": bool
                }}
            ]
        }}
        """
        return self._make_completion(prompt)

    def generate_data_contract(self, table_info: Dict[str, Any]) -> Dict[str, Any]:
        """Genera un contrato de datos basado en la información de la tabla"""
        prompt = f"""
        Genera un contrato de datos para una tabla SAP con la siguiente información:
        {json.dumps(table_info, indent=2)}
        
        El contrato debe seguir exactamente la estructura del template y mapear los campos 
        de la tabla SAP a los campos correspondientes del contrato.
        """
        return self._make_completion(prompt)

    def validate_contract(self, contract: Dict[str, Any]) -> bool:
        """Valida que el contrato generado cumpla con el esquema requerido"""
        prompt = f"""
        Valida que el siguiente contrato de datos cumpla con todos los requisitos del esquema:
        {json.dumps(contract, indent=2)}
        
        Responde con un JSON simple:
        {{
            "is_valid": bool,
            "errors": [str] // lista de errores si los hay
        }}
        """
        validation = self._make_completion(prompt)
        return validation["is_valid"]