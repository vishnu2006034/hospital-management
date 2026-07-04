"""Medicine service for business logic."""

from typing import Dict, List, Optional, Any

from app.models.medicine import Medicine
from app.repositories.medicine_repository import medicine_repository


class MedicineService:
    """Service layer for Medicine business operations."""

    @staticmethod
    def get_all_medicines(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ):
        """Get paginated list of medicines.

        Args:
            page: Page number.
            per_page: Items per page.
            search: Optional search term.

        Returns:
            Paginated medicine results.
        """
        return medicine_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_medicine_by_id(medicine_id: int) -> Medicine:
        """Get a medicine by ID.

        Args:
            medicine_id: The medicine's ID.

        Returns:
            The medicine entity.

        Raises:
            404: If medicine not found.
        """
        return medicine_repository.get_by_id(medicine_id)

    @staticmethod
    def create_medicine(data: Dict[str, Any]) -> Medicine:
        """Create a new medicine.

        Args:
            data: Medicine data dictionary.

        Returns:
            The created medicine entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        medicine: Medicine = Medicine(
            medicine_name=cleaned['medicine_name'],
            generic_name=cleaned.get('generic_name'),
            category=cleaned.get('category'),
            dosage_form=cleaned.get('dosage_form'),
            strength=cleaned.get('strength'),
            manufacturer=cleaned.get('manufacturer'),
            unit_price=cleaned.get('unit_price'),
        )
        medicine_repository.add(medicine)
        medicine_repository.commit()
        return medicine

    @staticmethod
    def update_medicine(medicine: Medicine, data: Dict[str, Any]) -> Medicine:
        """Update an existing medicine.

        Args:
            medicine: The medicine entity to update.
            data: Updated medicine data.

        Returns:
            The updated medicine entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        medicine.medicine_name = cleaned['medicine_name']
        medicine.generic_name = cleaned.get('generic_name')
        medicine.category = cleaned.get('category')
        medicine.dosage_form = cleaned.get('dosage_form')
        medicine.strength = cleaned.get('strength')
        medicine.manufacturer = cleaned.get('manufacturer')
        medicine.unit_price = cleaned.get('unit_price')
        medicine_repository.commit()
        return medicine

    @staticmethod
    def delete_medicine(medicine: Medicine) -> None:
        """Delete a medicine.

        Args:
            medicine: The medicine entity to delete.
        """
        medicine_repository.delete(medicine)
        medicine_repository.commit()
