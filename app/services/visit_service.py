"""Visit service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.visit import Visit
from app.repositories.visit_repository import VisitRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.user_repository import UserRepository
from app.services.interfaces.visit_service_interface import IVisitService
from app.dtos.visit import VisitResponse, VisitCreateRequest, VisitUpdateRequest
from app.dtos.patient import PatientResponse
from app.dtos.user import UserResponse
from app.mappers.visit_mapper import VisitMapper
from app.utils import clean_input_data


class VisitService(IVisitService):
    """Service layer for Visit business operations."""
    _visit_repository: VisitRepository = VisitRepository()
    _patient_repository: PatientRepository = PatientRepository()
    _user_repository: UserRepository = UserRepository()

    @staticmethod
    def get_all_visits(
        page: int = 1,
        per_page: int = 15,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Pagination:
        """Get paginated list of visits."""
        return VisitService._visit_repository.search(
            search, status=status, page=page, per_page=per_page
        )

    @staticmethod
    def get_visit_by_id(visit_id: int) -> VisitResponse:
        """Get a visit by ID."""
        return VisitService._visit_repository.get_by_id(visit_id)

    @staticmethod
    def create_visit(
        data: Dict[str, Any], admission_date: Optional[str] = None
    ) -> VisitResponse:
        """Create a new visit."""
        cleaned = clean_input_data(data)
        admission_date_val = admission_date if (admission_date and admission_date.strip()) else None

        dto = VisitCreateRequest(
            patient_id=int(cleaned['patient_id']),
            doctor_id=int(cleaned['doctor_id']),
            visit_type=cleaned.get('visit_type') or 'OUTPATIENT',
            visit_status='OPEN',
            chief_complaint=cleaned.get('chief_complaint'),
            diagnosis=cleaned.get('diagnosis'),
            treatment_plan=cleaned.get('treatment_plan'),
            notes=cleaned.get('notes'),
            height=cleaned.get('height'),
            weight=cleaned.get('weight'),
            temperature=cleaned.get('temperature'),
            blood_pressure=cleaned.get('blood_pressure'),
            pulse_rate=cleaned.get('pulse_rate'),
            oxygen_level=cleaned.get('oxygen_level')
        )
        if admission_date_val:
            dto.admission_date = admission_date_val

        visit_dto = VisitService._visit_repository.add(dto)
        VisitService._visit_repository.commit()
        return visit_dto

    @staticmethod
    def update_visit(
        visit_id: int,
        data: Dict[str, Any],
        admission_date: Optional[str] = None,
        discharge_date: Optional[str] = None,
    ) -> VisitResponse:
        """Update an existing visit."""
        cleaned = clean_input_data(data)
        visit_model = db.session.get(Visit, visit_id)
        if not visit_model:
            return None

        dto = VisitUpdateRequest(
            visit_type=cleaned.get('visit_type') or visit_model.visit_type,
            visit_status=cleaned.get('visit_status') or visit_model.visit_status,
            chief_complaint=cleaned.get('chief_complaint'),
            diagnosis=cleaned.get('diagnosis'),
            treatment_plan=cleaned.get('treatment_plan'),
            notes=cleaned.get('notes'),
            height=cleaned.get('height'),
            weight=cleaned.get('weight'),
            temperature=cleaned.get('temperature'),
            blood_pressure=cleaned.get('blood_pressure'),
            pulse_rate=cleaned.get('pulse_rate'),
            oxygen_level=cleaned.get('oxygen_level')
        )
        if admission_date and admission_date.strip():
            dto.admission_date = admission_date
        if discharge_date and discharge_date.strip():
            dto.discharge_date = discharge_date

        VisitMapper.update_model(visit_model, dto)
        VisitService._visit_repository.commit()
        return VisitMapper.to_dto(visit_model)

    @staticmethod
    def delete_visit(visit_id: int) -> None:
        """Delete a visit."""
        VisitService._visit_repository.delete(visit_id)
        VisitService._visit_repository.commit()

    @staticmethod
    def get_all_patients() -> List[PatientResponse]:
        return VisitService._patient_repository.get_all_patients()

    @staticmethod
    def get_all_doctors() -> List[UserResponse]:
        """Get all doctors."""
        return VisitService._user_repository.get_all_doctors()

    @staticmethod
    def get_visit_details(visit_id: int) -> Dict[str, List[Any]]:
        """Get all related entities for a visit."""
        return VisitService._visit_repository.get_visit_details(visit_id)

    @staticmethod
    def get_today_appointments_count() -> int:
        """Count today's appointments/visits."""
        return VisitService._visit_repository.get_today_appointments_count()

    @staticmethod
    def get_active_admissions_count() -> int:
        """Count active inpatient admissions."""
        return VisitService._visit_repository.get_active_admissions_count()
