"""Prescription service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app.models.prescription import Prescription
from app.models.inventory import Inventory
from app.models.visit import Visit
from app.repositories.prescription_repository import prescription_repository
from app.repositories.visit_repository import visit_repository
from app.utils import clean_input_data


class PrescriptionService:
    """Service layer for Prescription business operations."""

    @staticmethod
    def get_all_prescriptions(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> "Pagination[Prescription]":
        """Get paginated list of prescriptions."""
        return prescription_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_prescription_by_id(prescription_id: int) -> Prescription:
        """Get a prescription by ID."""
        return prescription_repository.get_by_id(prescription_id)

    @staticmethod
    def create_prescription(data: Dict[str, Any], prescribed_by: int) -> Prescription:
        """Create a new prescription."""
        cleaned = clean_input_data(data)

        qty_val = cleaned.get('quantity')
        qty: Optional[int] = int(qty_val) if qty_val is not None else None

        prescription: Prescription = Prescription(
            visit_id=cleaned['visit_id'],
            inventory_id=cleaned['inventory_id'],
            prescribed_by=prescribed_by,
            dosage=cleaned.get('dosage'),
            frequency=cleaned.get('frequency'),
            duration=cleaned.get('duration'),
            quantity=qty,
            instructions=cleaned.get('instructions'),
        )
        prescription_repository.add(prescription)

        if qty:
            prescription_repository.deduct_stock(
                int(cleaned['inventory_id']),
                qty
            )

        prescription_repository.commit()
        return prescription

    @staticmethod
    def delete_prescription(prescription: Prescription) -> None:
        """Delete a prescription."""
        prescription_repository.delete(prescription)
        prescription_repository.commit()

    @staticmethod
    def get_available_inventory() -> List[Inventory]:
        """Get all available inventory items."""
        return prescription_repository.get_available_inventory()

    @staticmethod
    def get_recent_visits(limit: int = 50) -> List[Visit]:
        """Get recent visits."""
        return visit_repository.get_recent_visits(limit)
