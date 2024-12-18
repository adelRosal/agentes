from typing import Dict, List
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def parse_table_data(soup: BeautifulSoup) -> Dict:
    """
    Parsea el HTML de una tabla SAP y extrae la información relevante
    """
    try:
        # Obtener información básica de la tabla
        table_info = {
            "name": soup.select_one(".sapds-card-header").text.strip(),
            "description": soup.select_one(".sapds-card-body p").text.strip(),
            "fields": []
        }

        # Contar campos totales en la tabla
        table_rows = soup.select("table.table tr")
        total_fields = len(table_rows) - 2  # Restar encabezados
        processed_fields = 0

        for row in table_rows[2:]:  # Saltar encabezados
            cols = row.select("td")
            if len(cols) >= 5:
                field = {
                    "name": cols[1].text.strip(),
                    "description": cols[2].text.strip(),
                    "data_type": cols[3].text.strip(),
                    "is_key": "Key" in cols[0].text,
                    "is_nullable": "NULL" in cols[4].text
                }
                table_info["fields"].append(field)
                processed_fields += 1

        # Validar que se procesaron todos los campos
        if processed_fields != total_fields:
            logger.warning(f"Discrepancia en campos: {processed_fields} procesados de {total_fields} totales")
            
        # Agregar metadata de validación
        table_info["_metadata"] = {
            "total_fields": total_fields,
            "processed_fields": processed_fields,
            "is_complete": processed_fields == total_fields
        }

        return table_info
    except Exception as e:
        logger.error(f"Error parseando tabla: {e}")
        return {} 