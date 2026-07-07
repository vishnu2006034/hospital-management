from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.dtos.patient import PatientResponse
from app.dtos.user import UserResponse
from app.dtos.visit import VisitResponse

class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    doctor_report_id: int
    visit_id: int
    patient_id: int
    doctor_id: int
    report_number: str
    chief_complaint: Optional[str] = None
    clinical_findings: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescribed_medicines: Optional[str] = None
    doctor_notes: Optional[str] = None
    follow_up_required: bool
    follow_up_date: Optional[date] = None
    next_visit_reason: Optional[str] = None
    report_file: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Nested relationship representation
    visit: Optional[VisitResponse] = None
    patient: Optional[PatientResponse] = None
    doctor: Optional[UserResponse] = None

class ReportCreateRequest(BaseModel):
    visit_id: int
    patient_id: int
    chief_complaint: Optional[str] = None
    clinical_findings: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescribed_medicines: Optional[str] = None
    doctor_notes: Optional[str] = None
    follow_up_required: Optional[bool] = False
    follow_up_date: Optional[date] = None
    next_visit_reason: Optional[str] = None
    doctor_id: Optional[int] = None
    report_number: Optional[str] = None

class ReportUpdateRequest(BaseModel):
    chief_complaint: Optional[str] = None
    clinical_findings: Optional[str] = None
    diagnosis: Optional[str] = None
    treatment_plan: Optional[str] = None
    prescribed_medicines: Optional[str] = None
    doctor_notes: Optional[str] = None
    follow_up_required: Optional[bool] = False
    follow_up_date: Optional[date] = None
    next_visit_reason: Optional[str] = None
