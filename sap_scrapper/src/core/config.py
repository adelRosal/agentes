from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "sap_tables")
    TEMPLATE_PATH: str = os.getenv("TEMPLATE_PATH", "./templates/data_contract_template.json")
    SCRAPER_RATE_LIMIT: int = int(os.getenv("SCRAPER_RATE_LIMIT", "2"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

settings = Settings() 