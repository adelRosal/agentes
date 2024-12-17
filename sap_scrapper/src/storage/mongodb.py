from motor.motor_asyncio import AsyncIOMotorClient
from typing import Dict, List, Optional
from ..core.config import settings
from ..models.data_contract import TableContract

class TableStorage:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db.sap_tables
        
    async def init_indexes(self):
        """Crear índices necesarios"""
        await self.collection.create_index("table_name", unique=True)
        await self.collection.create_index("category")
        await self.collection.create_index("delivery_class")
        
    async def store_table(self, table: TableContract) -> str:
        """Almacena o actualiza una tabla"""
        result = await self.collection.update_one(
            {"table_name": table.table_name},
            {"$set": table.dict()},
            upsert=True
        )
        return str(result.upserted_id or result.modified_count)
        
    async def get_table(self, table_name: str) -> Optional[Dict]:
        """Obtiene una tabla por nombre"""
        return await self.collection.find_one({"table_name": table_name})
        
    async def list_tables(self, skip: int = 0, limit: int = 100) -> List[Dict]:
        collection = self.db.tables
        cursor = collection.find().skip(skip).limit(limit)
        return await cursor.to_list(length=limit) 