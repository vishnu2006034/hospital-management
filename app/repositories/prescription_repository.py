"""Prescription repository for database operations."""

from typing import List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.prescription import Prescription
from app.models.visit import Visit
from app.models.inventory import Inventory
from app.models.medicine import Medicine
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.prescription_repository_interface import IPrescriptionRepository
from app.mappers.prescription_mapper import PrescriptionMapper
from app.mappers.inventory_mapper import InventoryMapper
from app.dtos.prescription import PrescriptionResponse, PrescriptionCreateRequest
from app.dtos.inventory import InventoryResponse


class PrescriptionRepository(BaseRepository[Prescription], IPrescriptionRepository):
    """Repository for Prescription entity database operations."""

    def __init__(self) -> None:
        super().__init__(Prescription)

    def get_by_id(self, id_value: int) -> Optional[PrescriptionResponse]:
        model = db.session.get(Prescription, id_value)
        return PrescriptionMapper.to_dto(model) if model else None

    def add(self, entity_dto: PrescriptionCreateRequest) -> PrescriptionResponse:
        model = PrescriptionMapper.to_model(entity_dto)
        db.session.add(model)
        db.session.flush()
        return PrescriptionMapper.to_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(Prescription, entity_id)
        if model:
            db.session.delete(model)

    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ) -> Pagination:
        """Search prescriptions with pagination."""
        query = Prescription.query.join(Visit).join(
            Inventory, Prescription.inventory_id == Inventory.inventory_id
        ).join(Medicine, Inventory.medicine_id == Medicine.medicine_id)
        if search:
            query = query.filter(
                db.or_(
                    Medicine.medicine_name.ilike(f'%{search}%'),
                    Medicine.generic_name.ilike(f'%{search}%'),
                )
            )
        query = query.order_by(Prescription.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        pagination.items = [PrescriptionMapper.to_dto(p) for p in pagination.items]
        return pagination

    def get_available_inventory(self) -> List[InventoryResponse]:
        """Get all inventory items with stock greater than zero."""
        models = Inventory.query.join(Medicine).filter(
            Inventory.quantity_in_stock > 0
        ).order_by(Medicine.medicine_name).all()
        return [InventoryMapper.to_dto(inv) for inv in models]

    def deduct_stock(self, inventory_id: int, quantity: int) -> None:
        """Deduct stock from an inventory item."""
        inv = db.session.get(Inventory, inventory_id)
        if inv:
            inv.quantity_in_stock = max(0, inv.quantity_in_stock - quantity)


prescription_repository: PrescriptionRepository = PrescriptionRepository()
