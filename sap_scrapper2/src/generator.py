from typing import Dict
import json
from datetime import datetime

def generate_contract(table_data: Dict) -> Dict:
    """
    Genera un contrato de datos a partir de la información de la tabla
    """
    contract = {
        "metadata": {
            "contract_name": f"SAP_{table_data.get('name', 'unknown')}",
            "version": "1.0.0",
            "last_updated": datetime.utcnow().isoformat()
        },
        "source_information": {
            "source_id": table_data.get('name'),
            "name": table_data.get('description'),
            "source_type": "Master Data",
            "operational_system": "SAP"
        },
        "technical_specifications": {
            "source_details": {
                "database": "SAP",
                "schema": "ABAP",
                "table": table_data.get('name'),
                "type": "TABLE"
            }
        },
        "field_specifications": {
            "attributes": {}
        }
    }

    # Agregar campos al contrato
    for field in table_data.get('fields', []):
        contract["field_specifications"]["attributes"][field["name"]] = {
            "data_type": field["data_type"],
            "description": field["description"],
            "is_pk": field["is_key"],
            "nullable": not field["is_key"],
            "example": ""
        }

    return contract 