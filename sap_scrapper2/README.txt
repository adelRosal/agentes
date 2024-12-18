SAP Table Scraper
================

Este proyecto permite extraer información de tablas SAP desde www.sapdatasheet.org/abap/tabl/ y generar contratos de datos estructurados.

Estructura del Proyecto
----------------------
/sap_scrapper2
  /src
    __init__.py
    scraper.py      # Lógica principal de scraping
    parser.py       # Parseo de HTML a estructura de datos
    generator.py    # Generación de contratos JSON
  /contracts        # Directorio donde se guardan los contratos generados
  /templates        # Templates para generar contratos
  requirements.txt  # Dependencias del proyecto

Dependencias Requeridas
----------------------
- requests>=2.31.0
- beautifulsoup4>=4.12.2
- python-dotenv>=1.0.0
- pandas>=2.1.1

Instalación
-----------
1. Crear un entorno virtual:
   python -m venv venv

2. Activar el entorno virtual:
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

3. Instalar dependencias:
   pip install -r requirements.txt

Uso Básico
----------
1. Ejecutar el scraper:
   python src/scraper.py

El scraper realizará las siguientes operaciones:

1. Navegación y Extracción:
   - Accede a la página principal de tablas SAP
   - Extrae la lista de tablas disponibles
   - Para cada tabla:
     * Obtiene nombre, descripción, categoría y clase de entrega
     * Navega a la página de detalle si está disponible
     * Extrae información adicional de campos y relaciones

2. Generación de Contratos:
   - Por cada tabla crea un contrato JSON siguiendo el template
   - Mapea la información extraída al formato del contrato
   - Guarda los contratos en /contracts/<tabla>.json

Estructura del Contrato Generado
-------------------------------
Los contratos generados seguirán esta estructura básica:

{
  "metadata": {
    "contract_name": "SAP_<tabla>",
    "version": "1.0.0",
    "last_updated": "<timestamp>"
  },
  "source_information": {
    "source_id": "<tabla>",
    "name": "<descripción>",
    "source_type": "Master Data",
    "operational_system": "SAP"
  },
  "technical_specifications": {
    "source_details": {
      "database": "SAP",
      "schema": "ABAP",
      "table": "<tabla>",
      "type": "TABLE"
    }
  },
  "field_specifications": {
    "attributes": {
      // Campos extraídos de la tabla
    }
  }
}

Consideraciones
--------------
1. Manejo de Errores:
   - El scraper implementa reintentos para p��ginas fallidas
   - Registra errores en un archivo de log
   - Continúa con la siguiente tabla si hay fallos

2. Rate Limiting:
   - Implementa delays entre requests para no sobrecargar el servidor
   - Respeta robots.txt del sitio

3. Almacenamiento:
   - Los contratos se guardan en formato JSON
   - Usa nombres de archivo seguros basados en el nombre de tabla
   - Implementa versionamiento básico de contratos

4. Escalabilidad:
   - Diseño modular para facilitar mantenimiento
   - Configuración via variables de entorno
   - Procesamiento en lotes configurable

Notas de Implementación
----------------------
1. El scraper usa BeautifulSoup para parsear HTML
2. Implementa un sistema de caché para evitar requests repetidos
3. Permite configurar el nivel de detalle de la extracción
4. Incluye validación básica de los datos extraídos
5. Genera logs detallados del proceso

Limitaciones Conocidas
---------------------
1. Depende de la estructura actual del sitio
2. No maneja autenticación
3. Limitado a la información públicamente disponible
4. Puede requerir ajustes si cambia la estructura del sitio

Próximos Pasos
-------------
1. Implementar extracción de relaciones entre tablas
2. Mejorar el manejo de caracteres especiales
3. Añadir más validaciones de datos
4. Implementar extracción paralela para mejor rendimiento
5. Añadir tests automatizados 