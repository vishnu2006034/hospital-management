"""Prescription repository for database operations."""

from typing import List, Optional

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.prescription import Prescription
from app.models.visit import Visit
from app.models.inventory import Inventory
from app.models.medicine import Medicine
from app.repositories.base_repository import BaseRepository


class PrescriptionRepository(BaseRepository[Prescription]):
    """Repository for Prescription entity database operations."""

    def __init__(self) -> None:
        super().__init__(Prescription)

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
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_available_inventory(self) -> List[Inventory]:
        """Get all inventory items with stock greater than zero."""
        return Inventory.query.join(Medicine).filter(
            Inventory.quantity_in_stock > 0
        ).order_by(Medicine.medicine_name).all()



    def deduct_stock(self, inventory_id: int, quantity: int) -> None:
        """Deduct stock from an inventory item."""
        inv: Optional[Inventory] = Inventory.query.get(inventory_id)
        if inv:
            inv.quantity_in_stock = max(0, inv.quantity_in_stock - quantity)


prescription_repository: PrescriptionRepository = PrescriptionRepository()

