"""Patient repository for database operations."""

from typing import List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.patient import Patient
from app.models.visit import Visit
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.patient_repository_interface import IPatientRepository
from app.mappers.patient_mapper import PatientMapper
from app.mappers.visit_mapper import VisitMapper
from app.dtos.patient import PatientResponse, PatientCreateRequest
from app.dtos.visit import VisitResponse
from app.utils import generate_sequential_code


class PatientRepository(BaseRepository[Patient], IPatientRepository):
    """Repository for Patient entity database operations."""

    def __init__(self) -> None:
        super().__init__(Patient)

    def get_by_id(self, id_value: int) -> Optional[PatientResponse]:
        model = db.session.get(Patient, id_value)
        return PatientMapper.to_dto(model) if model else None

    def add(self, entity_dto: PatientCreateRequest) -> PatientResponse:
        model = PatientMapper.to_model(entity_dto)
        # Ensure it gets the patient number
        model.patient_number = self.get_next_patient_number()
        db.session.add(model)
        db.session.flush()
        return PatientMapper.to_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(Patient, entity_id)
        if model:
            db.session.delete(model)

    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ) -> Pagination:
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
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        pagination.items = [PatientMapper.to_dto(p) for p in pagination.items]
        return pagination

    def get_next_patient_number(self) -> str:
        """Generate the next available patient number."""
        return generate_sequential_code(Patient, 'patient_id', 'PAT')

    def get_patient_visits(self, patient_id: int, limit: int = 20) -> List[VisitResponse]:
        """Get recent visits for a patient."""
        patient = db.session.get(Patient, patient_id)
        if patient:
            models = patient.visits.order_by(Visit.visit_date.desc()).limit(limit).all()
            return [VisitMapper.to_dto(v) for v in models]
        return []

    def get_all_patients(self) -> List[PatientResponse]:
        """Get all patients ordered by first name."""
        models = Patient.query.order_by(Patient.first_name).all()
        return [PatientMapper.to_dto(p) for p in models]

    def get_total_patients_count(self) -> int:
        """Count total patients."""
        return Patient.query.count()


patient_repository: PatientRepository = PatientRepository()
