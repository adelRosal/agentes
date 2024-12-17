import json
import os
from pathlib import Path
from typing import Dict
from ..models.data_contract import TableContract
from ..core.logging import logger

class ContractHandler:
    def __init__(self, contracts_dir: str = "contracts"):
        self.contracts_dir = Path(contracts_dir)
        self._ensure_contracts_directory()
        
    def _ensure_contracts_directory(self):
        """Asegura que exista el directorio de contratos"""
        self.contracts_dir.mkdir(parents=True, exist_ok=True)
        
    async def save_contract(self, contract: TableContract):
        """Guarda un contrato como archivo JSON"""
        try:
            file_path = self.contracts_dir / f"{contract.table_name.lower()}.json"
            
            # Convertir el contrato a diccionario y formatear
            contract_dict = contract.dict(exclude_none=True)
            
            # Guardar el archivo JSON con formato legible
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(contract_dict, f, indent=2, ensure_ascii=False)
                
            logger.info(f"Contract saved: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving contract for {contract.table_name}: {str(e)}")
            raise
            
    async def load_contract(self, table_name: str) -> Dict:
        """Carga un contrato desde archivo JSON"""
        file_path = self.contracts_dir / f"{table_name.lower()}.json"
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Contract not found: {table_name}")
            return None
        except Exception as e:
            logger.error(f"Error loading contract {table_name}: {str(e)}")
            raise 