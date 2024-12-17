from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TableField(BaseModel):
    name: str
    type: str
    length: Optional[int]
    description: Optional[str]
    key: bool = False

class TableContract(BaseModel):
    table_name: str
    description: str
    category: str
    delivery_class: str
    fields: List[TableField]
    metadata: dict = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "table_name": "MARC",
                "description": "Plant Data for Material",
                "category": "TRANSP",
                "delivery_class": "A",
                "fields": [
                    {
                        "name": "MATNR",
                        "type": "CHAR",
                        "length": 18,
                        "description": "Material Number",
                        "key": True
                    }
                ]
            }
        } 