from playwright.async_api import async_playwright, Browser, Page
from typing import Dict, List, Optional
import asyncio
from ..core.logging import logger
from ..core.config import settings
import backoff

class TableIndexScraper:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context = None
        self.base_url = "https://www.sapdatasheet.org/abap/tabl/"
        
    async def init(self):
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=True)
        self.context = await self.browser.new_context()
        
    async def get_index_pages(self) -> List[str]:
        """Obtiene todas las páginas índice (A-Z, CLUSTER, POOL, SLASH)"""
        page = await self.context.new_page()
        await page.goto(self.base_url)
        
        # Extraer links de índices
        index_links = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.index-links a')).map(a => a.href);
        }""")
        
        await page.close()
        return index_links
        
    async def get_tables_from_index(self, index_url: str) -> List[Dict]:
        """Extrae las tablas de una página de índice"""
        page = await self.context.new_page()
        await page.goto(index_url)
        
        # Extraer información de tablas
        tables = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('table tr')).slice(2).map(row => {
                const cells = row.querySelectorAll('td');
                return {
                    number: cells[0].textContent.trim(),
                    name: cells[1].querySelector('a')?.textContent.trim(),
                    description: cells[2].textContent.trim(),
                    category: cells[3].textContent.trim(),
                    delivery_class: cells[4].textContent.trim(),
                    url: cells[1].querySelector('a')?.href
                };
            });
        }""")
        
        # Obtener páginas adicionales del índice
        pagination_links = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('.pagination a')).map(a => a.href);
        }""")
        
        await page.close()
        return tables, pagination_links

    @backoff.on_exception(backoff.expo, Exception, max_tries=3)
    async def extract_table_details(self, table_url: str) -> Dict:
        """Extrae los detalles de una tabla específica"""
        page = await self.context.new_page()
        await page.goto(table_url)
        
        # Extraer detalles completos de la tabla
        details = await page.evaluate("""() => {
            return {
                name: document.querySelector('.table-name')?.textContent,
                description: document.querySelector('.table-description')?.textContent,
                fields: Array.from(document.querySelectorAll('.field-row')).map(row => ({
                    name: row.querySelector('.field-name')?.textContent,
                    type: row.querySelector('.field-type')?.textContent,
                    length: row.querySelector('.field-length')?.textContent,
                    description: row.querySelector('.field-description')?.textContent,
                    key: row.querySelector('.field-key')?.textContent === 'X'
                }))
            };
        }""")
        
        await page.close()
        return details