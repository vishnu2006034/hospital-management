"""Patient repository for database operations."""

from typing import List, Optional

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.patient import Patient
from app.models.visit import Visit
from app.repositories.base_repository import BaseRepository
from app.utils import generate_sequential_code


class PatientRepository(BaseRepository[Patient]):
    """Repository for Patient entity database operations."""

    def __init__(self) -> None:
        super().__init__(Patient)

    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ) -> "Pagination[Patient]":
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
        return generate_sequential_code(Patient, 'patient_id', 'PAT')

    def get_patient_visits(self, patient: Patient, limit: int = 20) -> List[Visit]:
        """Get recent visits for a patient."""
        return patient.visits.order_by(Visit.visit_date.desc()).limit(limit).all()

    def get_all_patients(self) -> List[Patient]:
        """Get all patients ordered by first name."""
        return Patient.query.order_by(Patient.first_name).all()


patient_repository: PatientRepository = PatientRepository()

