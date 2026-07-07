from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.dtos.patient import PatientResponse
from app.dtos.user import UserResponse
from app.dtos.visit import VisitResponse

class LabTestCatalogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    test_id: int
    test_code: str
    test_name: str
    category: Optional[str] = None
    sample_type: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    normal_min: Optional[Decimal] = None
    normal_max: Optional[Decimal] = None
    default_price: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: bool
    created_at: datetime

class LabTestCatalogCreateRequest(BaseModel):
    test_code: str
    test_name: str
    category: Optional[str] = None
    sample_type: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    normal_min: Optional[Decimal] = None
    normal_max: Optional[Decimal] = None
    default_price: Optional[Decimal] = None
    description: Optional[str] = None

class LabTestCatalogUpdateRequest(BaseModel):
    test_code: str
    test_name: str
    category: Optional[str] = None
    sample_type: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    normal_min: Optional[Decimal] = None
    normal_max: Optional[Decimal] = None
    default_price: Optional[Decimal] = None
    description: Optional[str] = None
    is_active: bool

class LabReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lab_report_id: int
    lab_id: int
    test_id: int
    patient_id: int
    doctor_id: int
    verified_by: Optional[int] = None
    report_number: str
    result: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    is_abnormal: bool
    remarks: Optional[str] = None
    verified_at: Optional[datetime] = None
    report_file: Optional[str] = None
    created_at: datetime

    # Nested relationship representation
    test: Optional[LabTestCatalogResponse] = None
    patient: Optional[PatientResponse] = None
    doctor: Optional[UserResponse] = None
    verifier: Optional[UserResponse] = None

class LabReportCreateRequest(BaseModel):
    test_id: int
    result: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    is_abnormal: Optional[bool] = False
    remarks: Optional[str] = None
    lab_id: Optional[int] = None
    patient_id: Optional[int] = None
    doctor_id: Optional[int] = None
    report_number: Optional[str] = None

class LaboratoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    lab_id: int
    visit_id: int
    patient_id: int
    requested_by: int
    lab_technician_id: Optional[int] = None
    priority: str
    sample_type: Optional[str] = None
    sample_collected_at: Optional[datetime] = None
    test_status: str
    remarks: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    # Nested relationship representation
    visit: Optional[VisitResponse] = None
    patient: Optional[PatientResponse] = None
    requester: Optional[UserResponse] = None
    technician: Optional[UserResponse] = None
    reports: List[LabReportResponse] = []

class LaboratoryCreateRequest(BaseModel):
    visit_id: int
    patient_id: int
    lab_technician_id: Optional[int] = None
    priority: Optional[str] = "NORMAL"
    sample_type: Optional[str] = None
    remarks: Optional[str] = None

class LaboratoryUpdateRequest(BaseModel):
    test_status: Optional[str] = None
    priority: Optional[str] = None
    lab_technician_id: Optional[int] = None
    sample_type: Optional[str] = None
    remarks: Optional[str] = None
    sample_collected_at: Optional[datetime] = None
