"""Inventory service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.medicine import Medicine
from app.repositories.inventory_repository import InventoryRepository
from app.utils import clean_input_data


class InventoryService:
    """Service layer for Inventory business operations."""
    _inventory_repository:InventoryRepository=InventoryRepository()

    @staticmethod
    def get_all_inventory(
        page: int = 1,
        per_page: int = 15,
        search: Optional[str] = None,
        filter_type: Optional[str] = None,
    ) -> "Pagination[Inventory]":
        """Get paginated list of inventory items."""
        return InventoryService._inventory_repository.search(
            search, filter_type=filter_type, page=page, per_page=per_page
        )

    @staticmethod
    def get_inventory_by_id(inventory_id: int) -> Inventory:
        """Get an inventory item by ID."""
        return InventoryService._inventory_repository.get_by_id(inventory_id)

    @staticmethod
    def create_inventory(
        data: Dict[str, Any], performed_by: Optional[int] = None
    ) -> Inventory:
        """Create a new inventory item."""
        cleaned = clean_input_data(data)

        qty_stock = cleaned.get('quantity_in_stock')
        min_stock = cleaned.get('minimum_stock')

        inv: Inventory = Inventory()
        inv.medicine_id=cleaned['medicine_id']
        inv.batch_number=cleaned['batch_number']
        inv.expiry_date=cleaned.get('expiry_date')
        inv.purchase_price=cleaned.get('purchase_price')
        inv.selling_price=cleaned.get('selling_price')
        inv.quantity_in_stock=int(qty_stock) if qty_stock is not None else 0
        inv.minimum_stock=int(min_stock) if min_stock is not None else 0
        inv.supplier=cleaned.get('supplier')
        InventoryService._inventory_repository.add(inv)

        if inv.quantity_in_stock > 0:
            InventoryService._inventory_repository.create_transaction(
                inventory_id=inv.inventory_id,
                transaction_type='IN',
                quantity=inv.quantity_in_stock,
                reference_type='PURCHASE',
                performed_by=performed_by,
                remarks='Initial stock entry',
            )

        InventoryService._inventory_repository.commit()
        return inv

    @staticmethod
    def update_inventory(inv: Inventory, data: Dict[str, Any]) -> Inventory:
        """Update an existing inventory item."""
        cleaned = clean_input_data(data)

        min_stock = cleaned.get('minimum_stock')

        inv.batch_number = cleaned['batch_number']
        inv.expiry_date = cleaned.get('expiry_date')
        inv.purchase_price = cleaned.get('purchase_price')
        inv.selling_price = cleaned.get('selling_price')
        inv.minimum_stock = int(min_stock) if min_stock is not None else 0
        inv.supplier = cleaned.get('supplier')
        InventoryService._inventory_repository.commit()
        return inv

    @staticmethod
    def add_transaction(
        inv: Inventory, data: Dict[str, Any], performed_by: int
    ) -> None:
        """Add a stock transaction."""
        cleaned = clean_input_data(data)

        txn_type: str = cleaned['transaction_type']
        qty: int = int(cleaned['quantity'])

        InventoryService._inventory_repository.create_transaction(
            inventory_id=inv.inventory_id,
            transaction_type=txn_type,
            quantity=qty,
            reference_type=cleaned.get('reference_type'),
            reference_id=cleaned.get('reference_id'),
            performed_by=performed_by,
            remarks=cleaned.get('remarks'),
        )

        InventoryService._inventory_repository.update_stock(inv.inventory_id, txn_type, qty)
        InventoryService._inventory_repository.commit()

    @staticmethod
    def get_recent_transactions(inv: Inventory, limit: int = 20) -> List[InventoryTransaction]:
        """Get recent transactions for an inventory item."""
        return InventoryService._inventory_repository.get_recent_transactions(inv.inventory_id, limit)

    @staticmethod
    def get_all_medicines() -> List[Medicine]:
        return InventoryService._inventory_repository.get_medicines()
