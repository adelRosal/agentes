# SAP Tables Web Scraper - Documentación de Implementación

## Arquitectura del Sistema

### 1. Componentes Principales

#### 1.1 Módulo de Scraping (src/scraper)
- **browser.py**: Gestiona la interacción con Playwright
- **extractor.py**: Lógica de extracción de datos
- **rate_limiter.py**: Control de velocidad de scraping

#### 1.2 Modelos de Datos (src/models)
- **table_schema.py**: Define la estructura de las tablas SAP
- **data_contract.py**: Implementa los contratos de datos usando Pydantic

#### 1.3 Almacenamiento (src/storage)
- **mongodb.py**: Gestión de conexiones y operaciones con MongoDB

#### 1.4 API REST (src/api)
- **routes.py**: Endpoints para consulta y búsqueda
- **middleware.py**: Manejo de autenticación y errores

### 2. Flujo de Datos
1. El scraper extrae datos de https://leanx.eu
2. Los datos se validan contra esquemas Pydantic
3. Se generan contratos de datos estandarizados
4. Se almacenan en MongoDB
5. Se exponen a través de API REST

## Estructura de Archivos Implementada

```
sap_scrapper/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── logging.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── table_schema.py
│   │   └── data_contract.py
│   ├── scraper/
│   │   ├── __init__.py
│   │   ├── browser.py
│   │   ├── extractor.py
│   │   └── rate_limiter.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── mongodb.py
│   └── api/
│       ├── __init__.py
│       ├── routes.py
│       └── middleware.py
├── tests/
│   ├── __init__.py
│   ├── test_scraper.py
│   ├── test_models.py
│   └── test_api.py
├── templates/
│   └── data_contract_template.json
├── requirements.txt
├── README.md
└── .env.example
```

## Detalles de Implementación

### 1. Modelos de Datos
Se implementaron usando Pydantic v2 para garantizar la validación de datos y la generación de esquemas JSON:
python:src/models/table_schema.py
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
class SAPField(BaseModel):
name: str
data_type: str
length: Optional[int]
description: Optional[str]
key_field: bool = False
class SAPTable(BaseModel):
table_name: str
description: str
fields: List[SAPField]
technical_settings: Dict[str, str]
last_updated: str

### 2. Scraper
Se implementó usando Playwright para manejar sitios dinámicos:

python:src/scraper/browser.py
from playwright.async_api import async_playwright
from typing import Dict, List
import asyncio
class TableScraper:
def init(self):
self.browser = None
self.context = None
async def init(self):
playwright = await async_playwright().start()
self.browser = await playwright.chromium.launch(headless=True)
self.context = await self.browser.new_context()
async def extract_table(self, table_name: str) -> Dict:
page = await self.context.new_page()
await page.goto(f"https://leanx.eu/en/sap/table/{table_name}")
# Implementación de la extracción...

### 3. Almacenamiento
Integración con MongoDB para almacenamiento flexible:

python:src/storage/mongodb.py
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict
import os
class MongoDBStorage:
def init(self):
self.client = AsyncIOMotorClient(os.getenv("MONGODB_URI"))
self.db = self.client[os.getenv("DATABASE_NAME")]
async def store_table(self, table_data: Dict):
collection = self.db.tables
await collection.update_one(
{"table_name": table_data["table_name"]},
{"$set": table_data},
upsert=True
)

### 4. API REST
Implementada con FastAPI para proporcionar acceso a los datos:

python:src/api/routes.py
from fastapi import FastAPI, HTTPException
from typing import List, Optional
from ..models.table_schema import SAPTable
from ..storage.mongodb import MongoDBStorage
app = FastAPI()
db = MongoDBStorage()
@app.get("/tables/{table_name}")
async def get_table(table_name: str) -> SAPTable:
table_data = await db.get_table(table_name)
if not table_data:
raise HTTPException(status_code=404, detail="Table not found")
return SAPTable(table_data)

## Configuración del Entorno

### Variables de Entorno (.env)
env:.env.example
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=sap_tables
TEMPLATE_PATH=./templates/data_contract_template.json
SCRAPER_RATE_LIMIT=2

### Docker
dockerfile:docker/Dockerfile
FROM python:3.11-slim
Instalar dependencias del sistema para Playwright
RUN apt-get update && apt-get install -y \
wget \
&& rm -rf /var/lib/apt/lists/
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
COPY . .
CMD ["uvicorn", "src.api.routes:app", "--host", "0.0.0.0", "--port", "8000"]

### Docker Compose
yaml:docker/docker-compose.yml
version: '3.8'
services:
app:
build:
context: .
dockerfile: docker/Dockerfile
ports:
"8000:8000"
environment:
MONGODB_URI=mongodb://mongo:27017
DATABASE_NAME=sap_tables
volumes:
./templates:/app/templates
depends_on:
mongo
mongo:
image: mongo:latest
ports:
"27017:27017"
volumes:
mongodb_data:/data/db
volumes:
mongodb_data:

## Características Implementadas

1. **Scraping Inteligente**
   - Sistema de caché para reducir peticiones
   - Reintentos automáticos con backoff exponencial
   - Rate limiting configurable

2. **Validación de Datos**
   - Esquemas Pydantic con validación estricta
   - Transformación automática de tipos
   - Manejo de valores nulos

3. **API REST**
   - Documentación automática con Swagger
   - Endpoints para búsqueda y consulta
   - Sistema de caché para respuestas frecuentes

4. **Almacenamiento**
   - Índices automáticos en MongoDB
   - Versionado de contratos
   - Búsqueda por múltiples criterios

## Próximos Pasos

1. Implementar sistema de monitoreo
2. Añadir más tests de integración
3. Mejorar el manejo de errores
4. Implementar sistema de notificaciones
5. Añadir más endpoints a la API

## Conclusión

Esta implementación proporciona una base sólida para un scraper de tablas SAP, con énfasis en la robustez, mantenibilidad y escalabilidad. La arquitectura modular permite fácil extensión y modificación de componentes según sea necesario.
 