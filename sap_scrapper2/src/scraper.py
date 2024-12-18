import os
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Set
import argparse
import asyncio
import aiohttp

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from parser import parse_table_data
from generator import generate_contract
from agent import SAPAgent

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    filename=os.getenv('LOG_FILE', 'logs/scraper.log'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SAPTableScraper:
    def __init__(self):
        self.base_url = os.getenv('BASE_URL', 'https://www.sapdatasheet.org/abap/tabl/')
        self.delay = int(os.getenv('DELAY_BETWEEN_REQUESTS', 2))
        self.max_retries = int(os.getenv('MAX_RETRIES', 3))
        self.session = requests.Session()
        self.agent = SAPAgent()
        self.tables_to_scrape: Optional[Set[str]] = None

    def get_table_list(self) -> List[Dict]:
        """Obtiene la lista de tablas SAP disponibles"""
        try:
            logger.info(f"Obteniendo lista de tablas desde {self.base_url}")
            response = self.session.get(self.base_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'lxml')
            tables = []
            
            for row in soup.select("table.table tr")[2:]:  # Saltamos los encabezados
                cols = row.select("td")
                if len(cols) >= 3:
                    table_link = cols[1].select_one("a")
                    if table_link:
                        href = table_link.get("href", "")
                        # Corregir la construcción de la URL
                        if href.startswith("/"):
                            url = f"https://www.sapdatasheet.org{href}"
                        else:
                            url = href if href.startswith("http") else f"{self.base_url}{href}"
                        
                        table_name = table_link.text.strip()
                        tables.append({
                            "name": table_name,
                            "url": url,
                            "description": cols[2].text.strip()
                        })
                        
            total_tables = len(tables)
            logger.info(f"Se encontraron {total_tables} tablas")
            
            # Si hay un límite, aplicarlo
            if self.limit and self.limit < total_tables:
                tables = tables[:self.limit]
                logger.info(f"Limitando a {self.limit} tablas")
            
            return tables
            
        except Exception as e:
            logger.error(f"Error obteniendo lista de tablas: {e}")
            logger.exception(e)
            return []

    def load_tables_to_scrape(self, filename: str = "tables_to_scrape.txt") -> Set[str]:
        """Carga la lista de tablas específicas a scrapear"""
        tables = set()
        try:
            with open(filename, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        tables.add(line)
            logger.info(f"Cargadas {len(tables)} tablas del archivo {filename}")
            return tables
        except FileNotFoundError:
            logger.info(f"No se encontró {filename}, se procesarán todas las tablas")
            return set()

    async def scrape_table_async(self, session: aiohttp.ClientSession, table: Dict) -> Dict:
        """Versión asíncrona de scrape_table"""
        try:
            async with session.get(table['url']) as response:
                html = await response.text()
                
                # Extraer información adicional
                soup = BeautifulSoup(html, 'lxml')
                category_elem = soup.select_one(".table-category")
                source_info = {
                    "url": table['url'],
                    "category": category_elem.text.strip() if category_elem else "Unknown",
                    "scrape_timestamp": datetime.utcnow().isoformat()
                }
                
                # Usar el agente para interpretar
                table_info = self.agent.interpret_table_structure(html)
                if not table_info:
                    return {}
                    
                # Agregar información de fuente
                table_info["source"] = source_info
                
                return table_info
        except Exception as e:
            logger.error(f"Error scraping {table['name']}: {e}")
            return {}

    async def process_tables_async(self, tables: List[Dict]):
        """Procesa las tablas de forma asíncrona"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for table in tables:
                # Si hay lista específica y no está vacía, filtrar
                if self.tables_to_scrape and len(self.tables_to_scrape) > 0:
                    if table['name'] not in self.tables_to_scrape:
                        continue
                
                # Esperar entre requests para no sobrecargar el servidor
                await asyncio.sleep(self.delay)
                tasks.append(self.scrape_table_async(session, table))
                
            results = await asyncio.gather(*tasks)
            return results

    def save_contract(self, table_name: str, contract: Dict):
        """Guarda el contrato con información mejorada"""
        try:
            # Crear estructura de directorios basada en el nombre de la tabla
            namespace = table_name.split('/')[0] if '/' in table_name else table_name.split('_')[0]
            contract_dir = os.path.join(os.getcwd(), 'contracts', namespace)
            
            # Asegurar que el directorio existe y tiene permisos correctos
            os.makedirs(contract_dir, exist_ok=True)
            os.chmod(contract_dir, 0o755)
            
            # Construir path completo del archivo
            safe_name = table_name.replace('/', '_')
            filename = os.path.join(contract_dir, f"{safe_name}.json")
            
            # Cargar template
            template_path = os.path.join(os.getcwd(), 'templates', 'data_contract_template.json')
            with open(template_path, 'r', encoding='utf-8') as f:
                template = json.load(f)
                
            # Mejorar el contrato con más información
            source_info = contract.get("source", {})
            final_contract = template.copy()
            final_contract.update({
                "metadata": {
                    "contract_name": f"SAP_{safe_name}",
                    "version": os.getenv('CONTRACT_VERSION', '1.0.0'),
                    "last_updated": datetime.utcnow().isoformat(),
                    "source_system": "SAP",
                    "validation": contract.get("_metadata", {}),
                    "status": {
                        "is_complete": bool(contract.get("fields")),
                        "has_source": bool(source_info),
                        "has_category": bool(source_info.get("category"))
                    }
                },
                "source_information": {
                    "table_name": contract.get("name", ""),
                    "description": contract.get("description", ""),
                    "category": source_info.get("category", "Unknown"),
                    "source_url": source_info.get("url", ""),
                    "scrape_timestamp": source_info.get("scrape_timestamp"),
                    "fields": contract.get("fields", [])
                }
            })
            
            # Limpiar secciones vacías
            for section in list(final_contract.keys()):
                if not final_contract[section]:
                    del final_contract[section]
                    
            # Guardar contrato
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(final_contract, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Contrato guardado en {filename}")
            
            # Verificar que el archivo se creó correctamente
            if not os.path.exists(filename):
                raise Exception(f"El archivo {filename} no se creó correctamente")
                
        except Exception as e:
            logger.error(f"Error guardando contrato para {table_name}: {e}")
            logger.exception(e)

    async def run_async(self, limit: int = None):
        """Versión asíncrona del método run"""
        self.limit = limit
        logger.info("Iniciando proceso de scraping asíncrono")
        
        # Cargar tablas específicas si existe el archivo
        self.tables_to_scrape = self.load_tables_to_scrape()
        
        tables = self.get_table_list()
        if not tables:
            logger.error("No se encontraron tablas para procesar")
            return
            
        results = await self.process_tables_async(tables)
        
        for table, result in zip(tables, results):
            if result:
                self.save_contract(table['name'], result)

    def run(self, limit: int = None):
        """Ejecuta el proceso de scraping completo"""
        self.limit = limit
        logger.info("Iniciando proceso de scraping")
        
        tables = self.get_table_list()
        if not tables:
            logger.error("No se encontraron tablas para procesar")
            return
        
        logger.info(f"Comenzando procesamiento de {len(tables)} tablas")
        
        for i, table in enumerate(tables, 1):
            try:
                logger.info(f"Procesando tabla {i}/{len(tables)}: {table['name']}")
                
                table_data = self.scrape_table(table['url'])
                if not table_data:
                    logger.warning(f"No se pudo extraer información de la tabla {table['name']}")
                    continue
                
                contract = self.agent.generate_data_contract(table_data)
                if not contract:
                    logger.warning(f"No se pudo generar contrato para la tabla {table['name']}")
                    continue
                
                self.save_contract(table['name'], contract)
                time.sleep(self.delay)
                
            except Exception as e:
                logger.error(f"Error procesando tabla {table.get('name', 'unknown')}: {e}")
                continue

def main():
    parser = argparse.ArgumentParser(description='SAP Table Scraper')
    parser.add_argument('--limit', type=int, help='Límite de tablas a procesar')
    parser.add_argument('--tables-file', help='Archivo con lista de tablas a procesar')
    parser.add_argument('--async-mode', action='store_true', help='Usar modo asíncrono')
    args = parser.parse_args()

    scraper = SAPTableScraper()
    
    try:
        if args.async_mode:
            asyncio.run(scraper.run_async(limit=args.limit))
        else:
            scraper.run(limit=args.limit)
            
    except KeyboardInterrupt:
        logger.info("Scraper detenido por el usuario")
    except Exception as e:
        logger.error(f"Error en la ejecución principal: {e}")

if __name__ == "__main__":
    main()