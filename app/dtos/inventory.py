from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.dtos.medicine import MedicineResponse
from app.dtos.user import UserResponse

class InventoryTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    transaction_id: str
    inventory_id: str
    performed_by: Optional[str] = None
    transaction_type: str
    quantity: int
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    remarks: Optional[str] = None
    transaction_date: datetime
    
    performer: Optional[UserResponse] = None

class InventoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    inventory_id: str
    medicine_id: str
    batch_number: str
    expiry_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    quantity_in_stock: int
    minimum_stock: int
    supplier: Optional[str] = None
    last_updated: datetime
    
    # Extra properties to match SQLAlchemy model convenience properties
    is_low_stock: bool
    is_expired: bool

    # Nested DTOs for relationships
    medicine: Optional[MedicineResponse] = None

class InventoryCreateRequest(BaseModel):
    medicine_id: str
    batch_number: str
    expiry_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    quantity_in_stock: Optional[int] = 0
    minimum_stock: Optional[int] = 0
    supplier: Optional[str] = None

class InventoryUpdateRequest(BaseModel):
    batch_number: str
    expiry_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    selling_price: Optional[Decimal] = None
    minimum_stock: Optional[int] = 0
    supplier: Optional[str] = None

class StockTransactionRequest(BaseModel):
    transaction_type: str
    quantity: int
    reference_type: Optional[str] = None
    reference_id: Optional[str] = None
    remarks: Optional[str] = None
