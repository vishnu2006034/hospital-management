"""Inventory service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.inventory import Inventory
from app.repositories.inventory_repository import InventoryRepository
from app.services.interfaces.inventory_service_interface import IInventoryService
from app.dtos.inventory import InventoryResponse, InventoryCreateRequest, InventoryUpdateRequest, InventoryTransactionResponse
from app.dtos.medicine import MedicineResponse
from app.mappers.inventory_mapper import InventoryMapper
from app.utils import clean_input_data


class InventoryService(IInventoryService):
    """Service layer for Inventory business operations."""
    _inventory_repository: InventoryRepository = InventoryRepository()

    @staticmethod
    def get_all_inventory(
        page: int = 1,
        per_page: int = 15,
        search: Optional[str] = None,
        filter_type: Optional[str] = None,
    ) -> Pagination:
        """Get paginated list of inventory items."""
        return InventoryService._inventory_repository.search(
            search, filter_type=filter_type, page=page, per_page=per_page
        )

    @staticmethod
    def get_inventory_by_id(inventory_id: int) -> InventoryResponse:
        """Get an inventory item by ID."""
        return InventoryService._inventory_repository.get_by_id(inventory_id)

    @staticmethod
    def create_inventory(
        data: Dict[str, Any], performed_by: Optional[int] = None
    ) -> InventoryResponse:
        """Create a new inventory item."""
        cleaned = clean_input_data(data)

        qty_stock = cleaned.get('quantity_in_stock')
        min_stock = cleaned.get('minimum_stock')

        dto = InventoryCreateRequest(
            medicine_id=int(cleaned['medicine_id']),
            batch_number=cleaned['batch_number'],
            expiry_date=cleaned.get('expiry_date'),
            purchase_price=cleaned.get('purchase_price'),
            selling_price=cleaned.get('selling_price'),
            quantity_in_stock=int(qty_stock) if qty_stock is not None else 0,
            minimum_stock=int(min_stock) if min_stock is not None else 0,
            supplier=cleaned.get('supplier')
        )

        inventory_dto = InventoryService._inventory_repository.add(dto)

        if inventory_dto.quantity_in_stock > 0:
            InventoryService._inventory_repository.create_transaction(
                inventory_id=inventory_dto.inventory_id,
                transaction_type='IN',
                quantity=inventory_dto.quantity_in_stock,
                reference_type='PURCHASE',
                performed_by=performed_by,
                remarks='Initial stock entry',
            )

        InventoryService._inventory_repository.commit()
        return InventoryService._inventory_repository.get_by_id(inventory_dto.inventory_id)

    @staticmethod
    def update_inventory(inventory_id: int, data: Dict[str, Any]) -> InventoryResponse:
        """Update an existing inventory item."""
        cleaned = clean_input_data(data)
        inventory_model = db.session.get(Inventory, inventory_id)
        if not inventory_model:
            return None

        dto = InventoryUpdateRequest(
            batch_number=cleaned['batch_number'],
            expiry_date=cleaned.get('expiry_date'),
            purchase_price=cleaned.get('purchase_price'),
            selling_price=cleaned.get('selling_price'),
            minimum_stock=int(cleaned.get('minimum_stock')) if cleaned.get('minimum_stock') is not None else 0,
            supplier=cleaned.get('supplier')
        )

        InventoryMapper.update_model(inventory_model, dto)
        InventoryService._inventory_repository.commit()
        return InventoryMapper.to_dto(inventory_model)

    @staticmethod
    def add_transaction(
        inventory_id: int, data: Dict[str, Any], performed_by: int
    ) -> None:
        """Add a stock transaction."""
        cleaned = clean_input_data(data)

        txn_type: str = cleaned['transaction_type']
        qty: int = int(cleaned['quantity'])

        InventoryService._inventory_repository.create_transaction(
            inventory_id=inventory_id,
            transaction_type=txn_type,
            quantity=qty,
            reference_type=cleaned.get('reference_type'),
            reference_id=cleaned.get('reference_id'),
            performed_by=performed_by,
            remarks=cleaned.get('remarks'),
        )

        InventoryService._inventory_repository.update_stock(inventory_id, txn_type, qty)
        InventoryService._inventory_repository.commit()

    @staticmethod
    def get_recent_transactions(inventory_id: int, limit: int = 20) -> List[InventoryTransactionResponse]:
        """Get recent transactions for an inventory item."""
        return InventoryService._inventory_repository.get_recent_transactions(inventory_id, limit)

    @staticmethod
    def get_all_medicines() -> List[MedicineResponse]:
        return InventoryService._inventory_repository.get_medicines()
