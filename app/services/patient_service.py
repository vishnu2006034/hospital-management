"""Patient service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app.models.patient import Patient
from app.models.visit import Visit
from app.repositories.patient_repository import PatientRepository
from app.utils import clean_input_data


class PatientService:
    """Service layer for Patient business operations."""
    _patient_repository:PatientRepository=PatientRepository()

    @staticmethod
    def get_all_patients(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> "Pagination[Patient]":
        """Get paginated list of patients."""
        return PatientService._patient_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_patient_by_id(patient_id: int) -> Patient:
        """Get a patient by ID."""
        return PatientService._patient_repository.get_by_id(patient_id)

    @staticmethod
    def generate_patient_number() -> str:
        return PatientService._patient_repository.get_next_patient_number()

    @staticmethod
    def create_patient(data: Dict[str, Any]) -> Patient:
        """Create a new patient."""
        cleaned = clean_input_data(data)

        patient: Patient = Patient()
        patient.patient_number=PatientService._patient_repository.get_next_patient_number(),
        patient.first_name=cleaned["first_name"]
        patient.last_name=cleaned.get("last_name")
        patient.gender=cleaned.get("gender")
        patient.dob=cleaned.get("dob")
        patient.blood_group=cleaned.get("blood_group")
        patient.phone=cleaned.get("phone")
        patient.email=cleaned.get("email")
        patient.address=cleaned.get("address")
        patient.emergency_contact_name=cleaned.get("emergency_contact_name")
        patient.emergency_contact_phone=cleaned.get("emergency_contact_phone")
        patient.allergies=cleaned.get("allergies")
        patient.medical_history=cleaned.get("medical_history")

        PatientService._patient_repository.add(patient)
        PatientService._patient_repository.commit()

        return patient

    @staticmethod
    def update_patient(patient: Patient, data: Dict[str, Any]) -> Patient:
        """Update an existing patient."""
        cleaned = clean_input_data(data)

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
                setattr(patient, field, cleaned[field])

        PatientService._patient_repository.commit()

        return patient

    @staticmethod
    def delete_patient(patient: Patient) -> None:
        """Delete a patient."""
        PatientService._patient_repository.delete(patient)
        PatientService._patient_repository.commit()

    @staticmethod
    def get_patient_visits(patient: Patient, limit: int = 20) -> List[Visit]:
        """Get recent visits for a patient."""
        return PatientService._patient_repository.get_patient_visits(patient, limit)