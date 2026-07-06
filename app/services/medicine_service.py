"""Medicine service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app.models.medicine import Medicine
#from app.repositories.medicine_repository import medicine_repository
from app.repositories.medicine_repository import MedicineRepository
from app.utils import clean_input_data



class MedicineService:
    """Service layer for Medicine business operations."""
    _medicine_repository:MedicineRepository=MedicineRepository()
    @staticmethod
    def get_all_medicines(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        """Get paginated list of medicines."""
        return MedicineService._medicine_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_medicine_by_id(medicine_id: int) -> Medicine:
        """Get a medicine by ID."""
        return MedicineService._medicine_repository.get_by_id(medicine_id)

    @staticmethod
    def create_medicine(data: Dict[str, Any]) -> Medicine:
        """Create a new medicine."""
        cleaned = clean_input_data(data)

        medicine: Medicine = Medicine()
        medicine.medicine_name=cleaned['medicine_name']
        medicine.generic_name=cleaned.get('generic_name')
        medicine.category=cleaned.get('category')
        medicine.dosage_form=cleaned.get('dosage_form')
        medicine.strength=cleaned.get('strength')
        medicine.manufacturer=cleaned.get('manufacturer')
        medicine.unit_price=cleaned.get('unit_price')
        MedicineService._medicine_repository.add(medicine)
        MedicineService._medicine_repository.commit()
        return medicine

    @staticmethod
    def update_medicine(medicine: Medicine, data: Dict[str, Any]) -> Medicine:
        """Update an existing medicine."""
        cleaned = clean_input_data(data)

        medicine.medicine_name = cleaned['medicine_name']
        medicine.generic_name = cleaned.get('generic_name')
        medicine.category = cleaned.get('category')
        medicine.dosage_form = cleaned.get('dosage_form')
        medicine.strength = cleaned.get('strength')
        medicine.manufacturer = cleaned.get('manufacturer')
        medicine.unit_price = cleaned.get('unit_price')
        MedicineService._medicine_repository.commit()
        return medicine

    @staticmethod
    def delete_medicine(medicine: Medicine) -> None:
        """Delete a medicine."""
        MedicineService._medicine_repository.delete(medicine)
        MedicineService._medicine_repository.commit()
