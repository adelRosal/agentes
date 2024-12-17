from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime

class SAPField(BaseModel):
    name: str = Field(..., description="Nombre del campo")
    data_type: str = Field(..., description="Tipo de dato SAP")
    length: Optional[int] = Field(None, description="Longitud del campo")
    description: Optional[str] = Field(None, description="Descripción del campo")
    key_field: bool = Field(False, description="Indica si es campo clave")

class SAPTable(BaseModel):
    table_name: str = Field(..., description="Nombre de la tabla SAP")
    description: str = Field(..., description="Descripción de la tabla")
    fields: List[SAPField] = Field(..., description="Campos de la tabla")
    technical_settings: Dict[str, str] = Field(default_factory=dict, description="Configuraciones técnicas")
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Última actualización") 