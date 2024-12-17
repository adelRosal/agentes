from ..scraper.browser import TableIndexScraper
from ..storage.mongodb import TableStorage
from ..models.data_contract import TableContract
from ..contracts.contract_handler import ContractHandler
from typing import List
import asyncio
from .logging import logger

class SAPTableOrchestrator:
    def __init__(self):
        self.scraper = TableIndexScraper()
        self.storage = TableStorage()
        self.contract_handler = ContractHandler()
        
    async def init(self):
        await self.scraper.init()
        await self.storage.init_indexes()
        
    async def process_all_tables(self):
        """Procesa todas las tablas disponibles"""
        # Obtener índices
        index_pages = await self.scraper.get_index_pages()
        
        for index_url in index_pages:
            try:
                # Procesar cada página del índice
                tables, pagination = await self.scraper.get_tables_from_index(index_url)
                
                # Procesar tablas encontradas
                for table_info in tables:
                    try:
                        # Obtener detalles y crear contrato
                        details = await self.scraper.extract_table_details(table_info["url"])
                        contract = TableContract(
                            table_name=table_info["name"],
                            description=table_info["description"],
                            category=table_info["category"],
                            delivery_class=table_info["delivery_class"],
                            fields=details["fields"]
                        )
                        
                        # Almacenar en MongoDB
                        await self.storage.store_table(contract)
                        
                        # Guardar contrato como archivo JSON
                        await self.contract_handler.save_contract(contract)
                        
                        logger.info(f"Processed table: {table_info['name']}")
                        
                    except Exception as e:
                        logger.error(f"Error processing table {table_info['name']}: {str(e)}")
                        
                # Procesar páginas adicionales
                for page_url in pagination:
                    await self.process_index_page(page_url)
                    
            except Exception as e:
                logger.error(f"Error processing index {index_url}: {str(e)}") 