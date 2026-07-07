from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.dtos.inventory import InventoryResponse
from app.dtos.user import UserResponse

class PrescriptionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    prescription_id: int
    visit_id: int
    inventory_id: int
    prescribed_by: int
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    quantity: Optional[int] = None
    instructions: Optional[str] = None
    created_at: datetime
    
    # Nested relationship representation
    inventory_batch: Optional[InventoryResponse] = None
    prescriber: Optional[UserResponse] = None

class PrescriptionCreateRequest(BaseModel):
    visit_id: int
    inventory_id: int
    dosage: Optional[str] = None
    frequency: Optional[str] = None
    duration: Optional[str] = None
    quantity: Optional[int] = None
    instructions: Optional[str] = None
    prescribed_by: Optional[int] = None
