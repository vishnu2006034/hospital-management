"""Medicine service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.medicine import Medicine
from app.repositories.medicine_repository import MedicineRepository
from app.services.interfaces.medicine_service_interface import IMedicineService
from app.dtos.medicine import MedicineResponse, MedicineCreateRequest, MedicineUpdateRequest
from app.mappers.medicine_mapper import MedicineMapper
from app.utils import clean_input_data


class MedicineService(IMedicineService):
    """Service layer for Medicine business operations."""
    _medicine_repository: MedicineRepository = MedicineRepository()

    @staticmethod
    def get_all_medicines(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        """Get paginated list of medicines."""
        return MedicineService._medicine_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_medicine_by_id(medicine_id: int) -> MedicineResponse:
        """Get a medicine by ID."""
        return MedicineService._medicine_repository.get_by_id(medicine_id)

    @staticmethod
    def create_medicine(data: Dict[str, Any]) -> MedicineResponse:
        """Create a new medicine."""
        cleaned = clean_input_data(data)

        dto = MedicineCreateRequest(
            medicine_name=cleaned['medicine_name'],
            generic_name=cleaned.get('generic_name'),
            category=cleaned.get('category'),
            dosage_form=cleaned.get('dosage_form'),
            strength=cleaned.get('strength'),
            manufacturer=cleaned.get('manufacturer'),
            unit_price=cleaned.get('unit_price')
        )
        medicine_dto = MedicineService._medicine_repository.add(dto)
        MedicineService._medicine_repository.commit()
        return medicine_dto

    @staticmethod
    def update_medicine(medicine_id: int, data: Dict[str, Any]) -> MedicineResponse:
        """Update an existing medicine."""
        cleaned = clean_input_data(data)
        medicine_model = db.session.get(Medicine, medicine_id)
        if not medicine_model:
            return None

        dto = MedicineUpdateRequest(
            medicine_name=cleaned['medicine_name'],
            generic_name=cleaned.get('generic_name'),
            category=cleaned.get('category'),
            dosage_form=cleaned.get('dosage_form'),
            strength=cleaned.get('strength'),
            manufacturer=cleaned.get('manufacturer'),
            unit_price=cleaned.get('unit_price')
        )
        MedicineMapper.update_model(medicine_model, dto)
        MedicineService._medicine_repository.commit()
        return MedicineMapper.to_dto(medicine_model)

    @staticmethod
    def delete_medicine(medicine_id: int) -> None:
        """Delete a medicine."""
        MedicineService._medicine_repository.delete(medicine_id)
        MedicineService._medicine_repository.commit()
