"""Patient service for business logic."""

from typing import Dict, List, Optional, Any

from app.models.patient import Patient
from app.repositories.patient_repository import patient_repository


class PatientService:
    """Service layer for Patient business operations."""

    @staticmethod
    def get_all_patients(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ):
        """Get paginated list of patients."""
        return patient_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_patient_by_id(patient_id: int) -> Patient:
        """Get a patient by ID."""
        return patient_repository.get_by_id(patient_id)

    @staticmethod
    def generate_patient_number() -> str:
        return patient_repository.get_next_patient_number()

    @staticmethod
    def create_patient(data: Dict[str, Any]) -> Patient:
        """Create a new patient."""
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        patient: Patient = Patient(
            patient_number=patient_repository.get_next_patient_number(),
            first_name=cleaned['first_name'],
            last_name=cleaned.get('last_name'),
            gender=cleaned.get('gender'),
            dob=cleaned.get('dob'),
            blood_group=cleaned.get('blood_group'),
            phone=cleaned.get('phone'),
            email=cleaned.get('email'),
            address=cleaned.get('address'),
            emergency_contact_name=cleaned.get('emergency_contact_name'),
            emergency_contact_phone=cleaned.get('emergency_contact_phone'),
            allergies=cleaned.get('allergies'),
            medical_history=cleaned.get('medical_history'),
        )
        patient_repository.add(patient)
        patient_repository.commit()
        return patient

    @staticmethod
    def update_patient(patient: Patient, data: Dict[str, Any]) -> Patient:
        """Update an existing patient."""
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        patient.first_name = cleaned['first_name']
        patient.last_name = cleaned.get('last_name')
        patient.gender = cleaned.get('gender')
        patient.dob = cleaned.get('dob')
        patient.blood_group = cleaned.get('blood_group')
        patient.phone = cleaned.get('phone')
        patient.email = cleaned.get('email')
        patient.address = cleaned.get('address')
        patient.emergency_contact_name = cleaned.get('emergency_contact_name')
        patient.emergency_contact_phone = cleaned.get('emergency_contact_phone')
        patient.allergies = cleaned.get('allergies')
        patient.medical_history = cleaned.get('medical_history')
        patient_repository.commit()
        return patient

    @staticmethod
    def delete_patient(patient: Patient) -> None:
        """Delete a patient."""
        patient_repository.delete(patient)
        patient_repository.commit()

    @staticmethod
    def get_patient_visits(patient: Patient, limit: int = 20) -> List:
        """Get recent visits for a patient."""
        return patient_repository.get_patient_visits(patient, limit)
