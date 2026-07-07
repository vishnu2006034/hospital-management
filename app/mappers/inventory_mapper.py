from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.dtos.inventory import (
    InventoryResponse,
    InventoryCreateRequest,
    InventoryUpdateRequest,
    InventoryTransactionResponse,
)
from app.mappers.medicine_mapper import MedicineMapper
from app.mappers.user_mapper import UserMapper

class InventoryMapper:
    @staticmethod
    def to_dto(inventory: Inventory) -> InventoryResponse:
        if not inventory:
            return None
        return InventoryResponse(
            inventory_id=inventory.inventory_id,
            medicine_id=inventory.medicine_id,
            batch_number=inventory.batch_number,
            expiry_date=inventory.expiry_date,
            purchase_price=inventory.purchase_price,
            selling_price=inventory.selling_price,
            quantity_in_stock=inventory.quantity_in_stock,
            minimum_stock=inventory.minimum_stock,
            supplier=inventory.supplier,
            last_updated=inventory.last_updated,
            is_low_stock=inventory.is_low_stock,
            is_expired=inventory.is_expired,
            medicine=MedicineMapper.to_dto(inventory.medicine) if hasattr(inventory, 'medicine') and inventory.medicine else None
        )

    @staticmethod
    def to_model(dto: InventoryCreateRequest) -> Inventory:
        inventory = Inventory()
        inventory.medicine_id = dto.medicine_id
        inventory.batch_number = dto.batch_number
        inventory.expiry_date = dto.expiry_date
        inventory.purchase_price = dto.purchase_price
        inventory.selling_price = dto.selling_price
        inventory.quantity_in_stock = dto.quantity_in_stock or 0
        inventory.minimum_stock = dto.minimum_stock or 0
        inventory.supplier = dto.supplier
        return inventory

    @staticmethod
    def update_model(inventory: Inventory, dto: InventoryUpdateRequest) -> Inventory:
        inventory.batch_number = dto.batch_number
        inventory.expiry_date = dto.expiry_date
        inventory.purchase_price = dto.purchase_price
        inventory.selling_price = dto.selling_price
        inventory.minimum_stock = dto.minimum_stock or 0
        inventory.supplier = dto.supplier
        return inventory

    @staticmethod
    def to_transaction_dto(txn: InventoryTransaction) -> InventoryTransactionResponse:
        if not txn:
            return None
        return InventoryTransactionResponse(
            transaction_id=txn.transaction_id,
            inventory_id=txn.inventory_id,
            performed_by=txn.performed_by,
            transaction_type=txn.transaction_type,
            quantity=txn.quantity,
            reference_type=txn.reference_type,
            reference_id=txn.reference_id,
            remarks=txn.remarks,
            transaction_date=txn.transaction_date,
            performer=UserMapper.to_dto(txn.performer) if hasattr(txn, 'performer') and txn.performer else None
        )
