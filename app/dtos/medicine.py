from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict

class MedicineResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    medicine_id: int
    medicine_name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    unit_price: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

class MedicineCreateRequest(BaseModel):
    medicine_name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    unit_price: Optional[Decimal] = None

class MedicineUpdateRequest(BaseModel):
    medicine_name: str
    generic_name: Optional[str] = None
    category: Optional[str] = None
    dosage_form: Optional[str] = None
    strength: Optional[str] = None
    manufacturer: Optional[str] = None
    unit_price: Optional[Decimal] = None
