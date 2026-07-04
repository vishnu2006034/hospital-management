"""Patient repository for database operations."""

from typing import List, Optional

from app import db
from app.models.patient import Patient
from app.models.visit import Visit
from app.repositories.base_repository import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Repository for Patient entity database operations."""

    def __init__(self) -> None:
        super().__init__(Patient)

    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ):
        """Search patients with pagination."""
        query = Patient.query
        if search:
            query = query.filter(
                db.or_(
                    Patient.first_name.ilike(f'%{search}%'),
                    Patient.last_name.ilike(f'%{search}%'),
                    Patient.patient_number.ilike(f'%{search}%'),
                    Patient.phone.ilike(f'%{search}%'),
                )
            )
        query = query.order_by(Patient.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_next_patient_number(self) -> str:
        """Generate the next available patient number."""
        last: Optional[Patient] = Patient.query.order_by(
            Patient.patient_id.desc()
        ).first()
        next_num: int = (last.patient_id + 1) if last else 1
        return f'PAT{next_num}'

    def get_patient_visits(self, patient: Patient, limit: int = 20) -> List[Visit]:
        """Get recent visits for a patient."""
        return patient.visits.order_by(Visit.visit_date.desc()).limit(limit).all()


patient_repository: PatientRepository = PatientRepository()

