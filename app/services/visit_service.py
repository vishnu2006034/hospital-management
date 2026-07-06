"""Visit service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app.models.visit import Visit
from app.models.patient import Patient
from app.models.user import User
from app.repositories.visit_repository import VisitRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.user_repository import UserRepository
from app.utils import clean_input_data


class VisitService:
    """Service layer for Visit business operations."""
    _visit_repository:VisitRepository=VisitRepository()
    _patient_repository:PatientRepository=PatientRepository()
    _user_repository:UserRepository=UserRepository()
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
    def get_visit_by_id(visit_id: int) -> Visit:
        """Get a visit by ID."""
        return VisitService._visit_repository.get_by_id(visit_id)

    @staticmethod
    def create_visit(
        data: Dict[str, Any], admission_date: Optional[str] = None
    ) -> Visit:
        """Create a new visit."""
        cleaned = clean_input_data(data)
        admission_date = admission_date if (admission_date and admission_date.strip()) else None

        visit: Visit = Visit()
        visit.patient_id=cleaned['patient_id']
        visit.doctor_id=cleaned['doctor_id']
        visit.visit_type=cleaned.get('visit_type') or 'OUTPATIENT'
        visit.visit_status='OPEN'
        visit.chief_complaint=cleaned.get('chief_complaint')
        visit.diagnosis=cleaned.get('diagnosis')
        visit.treatment_plan=cleaned.get('treatment_plan')
        visit.notes=cleaned.get('notes')
        visit.height=cleaned.get('height')
        visit.weight=cleaned.get('weight')
        visit.temperature=cleaned.get('temperature')
        visit.blood_pressure=cleaned.get('blood_pressure')
        visit.pulse_rate=cleaned.get('pulse_rate')
        visit.oxygen_level=cleaned.get('oxygen_level')
        if admission_date:
            visit.admission_date = admission_date
        VisitService._visit_repository.add(visit)
        VisitService._visit_repository.commit()
        return visit

    @staticmethod
    def update_visit(
        visit: Visit,
        data: Dict[str, Any],
        admission_date: Optional[str] = None,
        discharge_date: Optional[str] = None,
    ) -> Visit:
        """Update an existing visit."""
        cleaned = clean_input_data(data)
        admission_date = admission_date if (admission_date and admission_date.strip()) else None
        discharge_date = discharge_date if (discharge_date and discharge_date.strip()) else None

        visit.visit_type = cleaned.get('visit_type') or visit.visit_type
        visit.visit_status = cleaned.get('visit_status') or visit.visit_status
        visit.chief_complaint = cleaned.get('chief_complaint')
        visit.diagnosis = cleaned.get('diagnosis')
        visit.treatment_plan = cleaned.get('treatment_plan')
        visit.notes = cleaned.get('notes')
        visit.height = cleaned.get('height')
        visit.weight = cleaned.get('weight')
        visit.temperature = cleaned.get('temperature')
        visit.blood_pressure = cleaned.get('blood_pressure')
        visit.pulse_rate = cleaned.get('pulse_rate')
        visit.oxygen_level = cleaned.get('oxygen_level')
        
        # Update admission/discharge dates (even if None)
        visit.admission_date = admission_date
        visit.discharge_date = discharge_date

        VisitService._visit_repository.commit()
        return visit

    @staticmethod
    def delete_visit(visit: Visit) -> None:
        """Delete a visit."""
        VisitService._visit_repository.delete(visit)
        VisitService._visit_repository.commit()

    @staticmethod
    def get_all_patients() -> List[Patient]:
        return VisitService._patient_repository.get_all_patients()

    @staticmethod
    def get_all_doctors() -> List[User]:
        """Get all doctors."""
        return VisitService._user_repository.get_all_doctors()

    @staticmethod
    def get_visit_details(visit: Visit) -> Dict[str, List]:
        """Get all related entities for a visit."""
        return VisitService._visit_repository.get_visit_details(visit)
