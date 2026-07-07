"""Prescription service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.repositories.prescription_repository import PrescriptionRepository
from app.repositories.visit_repository import VisitRepository
from app.services.interfaces.prescription_service_interface import IPrescriptionService
from app.dtos.prescription import PrescriptionResponse, PrescriptionCreateRequest
from app.dtos.inventory import InventoryResponse
from app.dtos.visit import VisitResponse
from app.utils import clean_input_data


class PrescriptionService(IPrescriptionService):
    """Service layer for Prescription business operations."""
    _prescription_repository: PrescriptionRepository = PrescriptionRepository()
    _visit_repository: VisitRepository = VisitRepository()

    @staticmethod
    def get_all_prescriptions(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        """Get paginated list of prescriptions."""
        return PrescriptionService._prescription_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_prescription_by_id(prescription_id: int) -> PrescriptionResponse:
        """Get a prescription by ID."""
        return PrescriptionService._prescription_repository.get_by_id(prescription_id)

    @staticmethod
    def create_prescription(data: Dict[str, Any], prescribed_by: int) -> PrescriptionResponse:
        """Create a new prescription."""
        cleaned = clean_input_data(data)

        qty_val = cleaned.get('quantity')
        qty: Optional[int] = int(qty_val) if qty_val is not None else None

        dto = PrescriptionCreateRequest(
            visit_id=int(cleaned['visit_id']),
            inventory_id=int(cleaned['inventory_id']),
            dosage=cleaned.get('dosage'),
            frequency=cleaned.get('frequency'),
            duration=cleaned.get('duration'),
            quantity=qty,
            instructions=cleaned.get('instructions'),
            prescribed_by=prescribed_by
        )

        prescription_dto = PrescriptionService._prescription_repository.add(dto)

        if qty:
            PrescriptionService._prescription_repository.deduct_stock(
                int(cleaned['inventory_id']),
                qty
            )

        PrescriptionService._prescription_repository.commit()
        return prescription_dto

    @staticmethod
    def delete_prescription(prescription_id: int) -> None:
        """Delete a prescription."""
        PrescriptionService._prescription_repository.delete(prescription_id)
        PrescriptionService._prescription_repository.commit()

    @staticmethod
    def get_available_inventory() -> List[InventoryResponse]:
        """Get all available inventory items."""
        return PrescriptionService._prescription_repository.get_available_inventory()

    @staticmethod
    def get_recent_visits(limit: int = 50) -> List[VisitResponse]:
        """Get recent visits."""
        return PrescriptionService._visit_repository.get_recent_visits(limit)
