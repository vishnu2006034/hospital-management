from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.dtos.patient import PatientResponse
from app.dtos.user import UserResponse

class VisitResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    visit_id: int
    patient_id: int
    doctor_id: int
    visit_type: str
    visit_status: str
    visit_date: datetime
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    height: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    temperature: Optional[Decimal] = None
    blood_pressure: Optional[str] = None
    pulse_rate: Optional[int] = None
    oxygen_level: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    # Nested DTOs for relationships
    patient: Optional[PatientResponse] = None
    doctor: Optional[UserResponse] = None

class VisitCreateRequest(BaseModel):
    patient_id: int
    doctor_id: int
    visit_type: Optional[str] = "OUTPATIENT"
    visit_status: Optional[str] = "OPEN"
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    height: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    temperature: Optional[Decimal] = None
    blood_pressure: Optional[str] = None
    pulse_rate: Optional[int] = None
    oxygen_level: Optional[int] = None
    admission_date: Optional[datetime] = None

class VisitUpdateRequest(BaseModel):
    visit_type: Optional[str] = None
    visit_status: Optional[str] = None
    chief_complaint: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    notes: Optional[str] = None
    height: Optional[Decimal] = None
    weight: Optional[Decimal] = None
    temperature: Optional[Decimal] = None
    blood_pressure: Optional[str] = None
    pulse_rate: Optional[int] = None
    oxygen_level: Optional[int] = None
    admission_date: Optional[datetime] = None
    discharge_date: Optional[datetime] = None
