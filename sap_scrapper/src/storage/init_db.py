from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from ..core.config import settings
from ..core.logging import logger

async def init_mongodb():
    try:
        # Conectar a MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URI)
        db = client[settings.DATABASE_NAME]
        
        # Verificar conexión
        await client.admin.command('ping')
        logger.info("Conexión a MongoDB establecida")
        
        # Crear colecciones e índices
        await db.tables.create_index("table_name", unique=True)
        await db.tables.create_index("category")
        await db.tables.create_index("delivery_class")
        
        logger.info("Índices de MongoDB creados correctamente")
        
    except Exception as e:
        logger.error(f"Error inicializando MongoDB: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(init_mongodb()) 