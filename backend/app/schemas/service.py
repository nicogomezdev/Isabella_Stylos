from pydantic import BaseModel, field_validator, ConfigDict
from uuid import UUID
from datetime import datetime
from decimal import Decimal

class ServiceCreate(BaseModel):
    name : str
    description: str | None = None
    duration_minutes : int
    price : Decimal

    @field_validator("duration_minutes")
    @classmethod
    def duration_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("La duración debe ser mayor a 0 minutos")
        return v
    
    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v
    
class ServiceUpdate(BaseModel):
    name : str | None = None
    description : str | None = None
    duration_minutes :int | None = None
    price : Decimal | None = None
    is_active : bool | None = None

class ServiceResponse(BaseModel):
    id : UUID
    name : str
    description : str | None 
    duration_minutes : int
    price : Decimal
    is_active : bool
    created_at : datetime

    model_config = ConfigDict(from_attributes=True)