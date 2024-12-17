# SAP Tables Web Scraper

## Descripción del Proyecto
Herramienta automatizada para extraer diccionarios de datos de tablas SAP desde https://leanx.eu/en/sap/table/marc.html, generando contratos de datos estandarizados en formato JSON.

## Tecnologías Recomendadas

### Core
- **Python 3.11+**
  - Lenguaje principal por su robustez en web scraping y procesamiento de datos
  - Excelente soporte para async/await
  - Amplia biblioteca de paquetes

### Web Scraping
- **Playwright**
  - Mejor opción para sitios dinámicos con JavaScript
  - Soporte para navegación headless
  - Manejo automático de esperas y estados de carga
  - Mejor rendimiento que Selenium
  - Más moderno y mantenible

### Procesamiento de Datos
- **Pydantic v2**
  - Validación de datos y serialización
  - Generación de esquemas JSON
  - Excelente para contratos de datos tipados

### Almacenamiento
- **MongoDB**
  - Ideal para datos semi-estructurados
  - Esquema flexible para diferentes estructuras de tablas
  - Buen rendimiento en consultas

### API (Opcional)
- **FastAPI**
  - Framework moderno y rápido
  - Documentación automática con OpenAPI
  - Integración nativa con Pydantic

### Contenedorización
- **Docker + Docker Compose**
  - Contenedor para la aplicación Python
  - Contenedor para MongoDB
  - Volúmenes para persistencia de datos

## Estructura Propuesta del Proyecto
sap_scrapper/
|-- docker/
| |-- Dockerfile
| -- docker-compose.yml|-- src/| |-- core/| | |-- __init__.py| | |-- config.py| | -- logging.py
| |-- models/
| | |-- init.py
| | |-- table_schema.py
| | -- data_contract.py| |-- scraper/| | |-- __init__.py| | |-- browser.py| | -- extractor.py
| |-- storage/
| | |-- init.py
| | -- mongodb.py| -- api/
| |-- init.py
| -- routes.py|-- tests/| -- ...
|-- templates/
| -- data_contract_template.json|-- requirements.txt|-- README.md-- .env.example

## Configuración y Uso

### Variables de Entorno
env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=sap_tables
TEMPLATE_PATH=./templates/data_contract_template.json

### Docker Compose
yaml
version: '3.8'
services:
app:
build:
context: .
dockerfile: docker/Dockerfile
volumes:
./templates:/app/templates
environment:
MONGODB_URI=mongodb://mongo:27017
depends_on:
mongo
mongo:
image: mongo:latest
volumes:
mongodb_data:/data/db
volumes:
mongodb_data:

## Ejemplo de Uso
python
from src.scraper import TableScraper
from src.models import DataContract
Iniciar el scraper
scraper = TableScraper()
Extraer datos de una tabla específica
table_data = await scraper.extract_table("MARC")
Generar contrato de datos
contract = DataContract.from_table(table_data)
Guardar en MongoDB
await contract.save()

## Características Principales

1. **Scraping Inteligente**
   - Manejo de paginación
   - Caché de resultados
   - Reintentos automáticos
   - Rate limiting configurable

2. **Validación de Datos**
   - Esquemas Pydantic para validación
   - Transformación automática de tipos
   - Manejo de valores nulos y defaults

3. **Almacenamiento Flexible**
   - Índices automáticos en MongoDB
   - Versionado de contratos
   - Búsqueda por múltiples criterios

4. **API REST (Opcional)**
   - Endpoints para búsqueda y consulta
   - Documentación automática con Swagger
   - Autenticación configurable

## Desarrollo

1. Clonar el repositorio
2. Crear y activar entorno virtual
3. Instalar dependencias: `pip install -r requirements.txt`
4. Copiar `.env.example` a `.env` y configurar
5. Ejecutar tests: `pytest`

## Despliegue con Docker

bash
Construir y levantar contenedores
docker-compose up -d
Ver logs
docker-compose logs -f
Detener servicios
docker-compose down
## Licencia

## Contribución
1. Fork del repositorio
2. Crear rama feature: `git checkout -b feature/nueva-caracteristica`
3. Commit cambios: `git commit -am 'Añadir nueva característica'`
4. Push a la rama: `git push origin feature/nueva-caracteristica`
5. Crear Pull Request

## Licencia
MIT
Los cambios principales son:
Utilicé caracteres ASCII simples (|, -, ) para la estructura del árbol2. Añadí identificadores de lenguaje específicos a los bloques de código (env, yaml, python, bash)3. Mejoré el espaciado y la indentación4. Aseguré que todos los bloques de código estén correctamente cerrados
