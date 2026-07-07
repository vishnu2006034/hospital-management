"""Patient service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.patient import Patient
from app.repositories.patient_repository import PatientRepository
from app.services.interfaces.patient_service_interface import IPatientService
from app.dtos.patient import PatientResponse, PatientCreateRequest, PatientUpdateRequest
from app.dtos.visit import VisitResponse
from app.mappers.patient_mapper import PatientMapper
from app.utils import clean_input_data


class PatientService(IPatientService):
    """Service layer for Patient business operations."""
    _patient_repository: PatientRepository = PatientRepository()

    @staticmethod
    def get_all_patients(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        """Get paginated list of patients."""
        return PatientService._patient_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_patient_by_id(patient_id: int) -> PatientResponse:
        """Get a patient by ID."""
        return PatientService._patient_repository.get_by_id(patient_id)

    @staticmethod
    def generate_patient_number() -> str:
        return PatientService._patient_repository.get_next_patient_number()

    @staticmethod
    def create_patient(data: Dict[str, Any]) -> PatientResponse:
        """Create a new patient."""
        cleaned = clean_input_data(data)

        dto = PatientCreateRequest(
            first_name=cleaned["first_name"],
            last_name=cleaned.get("last_name"),
            gender=cleaned.get("gender"),
            dob=cleaned.get("dob"),
            blood_group=cleaned.get("blood_group"),
            phone=cleaned.get("phone"),
            email=cleaned.get("email"),
            address=cleaned.get("address"),
            emergency_contact_name=cleaned.get("emergency_contact_name"),
            emergency_contact_phone=cleaned.get("emergency_contact_phone"),
            allergies=cleaned.get("allergies"),
            medical_history=cleaned.get("medical_history")
        )

        patient_dto = PatientService._patient_repository.add(dto)
        PatientService._patient_repository.commit()
        return patient_dto

    @staticmethod
    def update_patient(patient_id: int, data: Dict[str, Any]) -> PatientResponse:
        """Update an existing patient."""
        cleaned = clean_input_data(data)
        patient_model = db.session.get(Patient, patient_id)
        if not patient_model:
            return None

        editable_fields = (
            "first_name",
            "last_name",
            "gender",
            "dob",
            "blood_group",
            "phone",
            "email",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "allergies",
            "medical_history",
        )

        for field in editable_fields:
            if field in cleaned:
                setattr(patient_model, field, cleaned[field])

        PatientService._patient_repository.commit()
        return PatientMapper.to_dto(patient_model)

    @staticmethod
    def delete_patient(patient_id: int) -> None:
        """Delete a patient."""
        PatientService._patient_repository.delete(patient_id)
        PatientService._patient_repository.commit()

    @staticmethod
    def get_patient_visits(patient_id: int, limit: int = 20) -> List[VisitResponse]:
        """Get recent visits for a patient."""
        return PatientService._patient_repository.get_patient_visits(patient_id, limit)

    @staticmethod
    def get_total_patients_count() -> int:
        """Count total patients."""
        return PatientService._patient_repository.get_total_patients_count()