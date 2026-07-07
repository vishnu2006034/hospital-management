"""Inventory repository for database operations."""

from datetime import date
from typing import List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.medicine import Medicine
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.inventory_repository_interface import IInventoryRepository
from app.mappers.inventory_mapper import InventoryMapper
from app.mappers.medicine_mapper import MedicineMapper
from app.dtos.inventory import InventoryResponse, InventoryCreateRequest, InventoryTransactionResponse
from app.dtos.medicine import MedicineResponse


class InventoryRepository(BaseRepository[Inventory], IInventoryRepository):
    """Repository for Inventory entity database operations."""

    def __init__(self) -> None:
        super().__init__(Inventory)

    def get_by_id(self, id_value: int) -> Optional[InventoryResponse]:
        model = db.session.get(Inventory, id_value)
        return InventoryMapper.to_dto(model) if model else None

    def add(self, entity_dto: InventoryCreateRequest) -> InventoryResponse:
        model = InventoryMapper.to_model(entity_dto)
        db.session.add(model)
        db.session.flush()
        return InventoryMapper.to_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(Inventory, entity_id)
        if model:
            db.session.delete(model)

    def search(
        self,
        search: Optional[str] = None,
        filter_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> Pagination:
        """Search inventory with optional filters and pagination."""
        query = Inventory.query.join(Medicine)
        if search:
            query = query.filter(
                db.or_(
                    Medicine.medicine_name.ilike(f'%{search}%'),
                    Inventory.batch_number.ilike(f'%{search}%'),
                    Inventory.supplier.ilike(f'%{search}%'),
                )
            )
        if filter_type == 'low':
            query = query.filter(Inventory.quantity_in_stock <= Inventory.minimum_stock)
        elif filter_type == 'expired':
            query = query.filter(Inventory.expiry_date < date.today())
        query = query.order_by(Medicine.medicine_name, Inventory.batch_number)
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        pagination.items = [InventoryMapper.to_dto(inv) for inv in pagination.items]
        return pagination

    def get_medicines(self) -> List[MedicineResponse]:
        """Get all medicines ordered by name."""
        models = Medicine.query.order_by(Medicine.medicine_name).all()
        return [MedicineMapper.to_dto(m) for m in models]

    def get_recent_transactions(
        self, inventory_id: int, limit: int = 20
    ) -> List[InventoryTransactionResponse]:
        """Get recent transactions for an inventory item."""
        inv = db.session.get(Inventory, inventory_id)
        if inv:
            models = inv.transactions.order_by(
                InventoryTransaction.transaction_date.desc()
            ).limit(limit).all()
            return [InventoryMapper.to_transaction_dto(txn) for txn in models]
        return []

    def create_transaction(
        self,
        inventory_id: int,
        transaction_type: str,
        quantity: int,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        performed_by: Optional[int] = None,
        remarks: Optional[str] = None,
    ) -> InventoryTransactionResponse:
        """Create a new inventory transaction."""
        txn = InventoryTransaction()
        txn.inventory_id = inventory_id
        txn.transaction_type = transaction_type
        txn.quantity = quantity
        txn.reference_type = reference_type
        txn.reference_id = reference_id
        txn.performed_by = performed_by
        txn.remarks = remarks        
        db.session.add(txn)
        db.session.flush()
        return InventoryMapper.to_transaction_dto(txn)

    def update_stock(
        self, inventory_id: int, transaction_type: str, quantity: int
    ) -> Optional[InventoryResponse]:
        """Update stock level for an inventory item."""
        inv = db.session.get(Inventory, inventory_id)
        if inv:
            if transaction_type == 'IN':
                inv.quantity_in_stock += quantity
            elif transaction_type == 'OUT':
                inv.quantity_in_stock = max(0, inv.quantity_in_stock - quantity)
            elif transaction_type == 'ADJUSTMENT':
                inv.quantity_in_stock = quantity
            db.session.flush()
            return InventoryMapper.to_dto(inv)
        return None


inventory_repository: InventoryRepository = InventoryRepository()
