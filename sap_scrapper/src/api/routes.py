from fastapi import FastAPI, HTTPException, Query
from typing import List, Optional
from ..models.table_schema import SAPTable
from ..storage.mongodb import MongoDBStorage
from ..scraper.browser import TableScraper
from ..core.logging import logger

app = FastAPI(title="SAP Tables API")
db = MongoDBStorage()
scraper = TableScraper()

@app.get("/tables/{table_name}")
async def get_table(table_name: str) -> SAPTable:
    table_data = await db.get_table(table_name)
    if not table_data:
        raise HTTPException(status_code=404, detail="Table not found")
    return SAPTable(**table_data)

@app.post("/tables/{table_name}/refresh")
async def refresh_table(table_name: str) -> SAPTable:
    try:
        table_data = await scraper.extract_table(table_name)
        await db.store_table(table_data)
        return SAPTable(**table_data)
    except Exception as e:
        logger.error(f"Error refreshing table {table_name}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error refreshing table")

@app.get("/tables")
async def list_tables(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
) -> List[SAPTable]:
    tables = await db.list_tables(skip, limit)
    return [SAPTable(**table) for table in tables] 