import asyncio
from core.orchestrator import SAPTableOrchestrator
from core.logging import logger

async def main():
    orchestrator = SAPTableOrchestrator()
    await orchestrator.init()
    
    try:
        await orchestrator.process_all_tables()
    except Exception as e:
        logger.error(f"Error en el proceso principal: {str(e)}")
    finally:
        await orchestrator.scraper.browser.close()

if __name__ == "__main__":
    asyncio.run(main()) 