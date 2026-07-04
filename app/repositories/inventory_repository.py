"""Inventory repository for database operations."""

from datetime import date
from typing import List, Optional

from app import db
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.medicine import Medicine
from app.repositories.base_repository import BaseRepository


class InventoryRepository(BaseRepository[Inventory]):
    """Repository for Inventory entity database operations."""

    def __init__(self) -> None:
        super().__init__(Inventory)

    def search(
        self,
        search: Optional[str] = None,
        filter_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ):
        """Search inventory with optional filters and pagination.

        Args:
            search: Search term for medicine name, batch, or supplier.
            filter_type: Filter type ('low' for low stock, 'expired').
            page: Page number.
            per_page: Items per page.

        Returns:
            Paginated inventory results.
        """
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
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_low_stock_items(self) -> List[Inventory]:
        """Get all inventory items at or below minimum stock level.

        Returns:
            List of low-stock inventory items.
        """
        return Inventory.query.filter(
            Inventory.quantity_in_stock <= Inventory.minimum_stock
        ).all()

    def get_expired_items(self) -> List[Inventory]:
        """Get all expired inventory items.

        Returns:
            List of expired inventory items.
        """
        return Inventory.query.filter(
            Inventory.expiry_date < date.today()
        ).all()

    def get_available_inventory(self) -> List[Inventory]:
        """Get all inventory with stock greater than zero.

        Returns:
            List of available inventory items.
        """
        return Inventory.query.join(Medicine).filter(
            Inventory.quantity_in_stock > 0
        ).order_by(Medicine.medicine_name).all()

    def get_medicines(self) -> List[Medicine]:
        """Get all medicines ordered by name.

        Returns:
            List of all medicines.
        """
        return Medicine.query.order_by(Medicine.medicine_name).all()

    def get_recent_transactions(
        self, inventory_id: int, limit: int = 20
    ) -> List[InventoryTransaction]:
        """Get recent transactions for an inventory item.

        Args:
            inventory_id: The inventory item's ID.
            limit: Maximum number of transactions.

        Returns:
            List of recent transactions ordered by date descending.
        """
        inv: Optional[Inventory] = self.get_by_id(inventory_id)
        if inv:
            return inv.transactions.order_by(
                InventoryTransaction.transaction_date.desc()
            ).limit(limit).all()
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
    ) -> InventoryTransaction:
        """Create a new inventory transaction.

        Args:
            inventory_id: The inventory item's ID.
            transaction_type: Type of transaction (IN/OUT/ADJUSTMENT).
            quantity: Quantity for this transaction.
            reference_type: Reference type (PRESCRIPTION/PURCHASE).
            reference_id: Reference entity ID.
            performed_by: User who performed the transaction.
            remarks: Additional notes.

        Returns:
            The created transaction entity.
        """
        txn: InventoryTransaction = InventoryTransaction(
            inventory_id=inventory_id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            performed_by=performed_by,
            remarks=remarks,
        )
        db.session.add(txn)
        return txn

    def update_stock(
        self, inventory_id: int, transaction_type: str, quantity: int
    ) -> Optional[Inventory]:
        """Update stock level for an inventory item.

        Args:
            inventory_id: The inventory item's ID.
            transaction_type: Type of transaction (IN/OUT/ADJUSTMENT).
            quantity: Quantity to adjust.

        Returns:
            The updated inventory item, or None if not found.
        """
        inv: Optional[Inventory] = self.get_by_id(inventory_id)
        if inv:
            if transaction_type == 'IN':
                inv.quantity_in_stock += quantity
            elif transaction_type == 'OUT':
                inv.quantity_in_stock = max(0, inv.quantity_in_stock - quantity)
            elif transaction_type == 'ADJUSTMENT':
                inv.quantity_in_stock = quantity
        return inv


inventory_repository: InventoryRepository = InventoryRepository()

