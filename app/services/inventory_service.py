"""Inventory service for business logic using hogc-crud-engine."""

from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any

from app.dtos.inventory import InventoryResponse, InventoryTransactionResponse
from app.dtos.medicine import MedicineResponse
from app.extensions import crud_provider
from app.services.interfaces.inventory_service_interface import IInventoryService
from app.services.crud_helper import run_in_context, query_records, EAVPagination
from hogc.lib.contracts.crud.requests import CreateRecordRequest, GetRecordRequest, UpdateRecordRequest, DeleteRecordRequest, ListRecordsRequest
from app.utils import clean_input_data

class InventoryService(IInventoryService):
    """Service layer for Inventory business operations using hogc-crud-engine."""

    @staticmethod
    def map_to_inventory(rec) -> InventoryResponse:
        expiry_date = None
        exp_str = rec.data.get("expiry_date")
        if exp_str:
            try:
                expiry_date = datetime.strptime(exp_str[:10], "%Y-%m-%d").date()
            except Exception:
                pass
                
        qty = int(rec.data.get("quantity_in_stock", 0))
        min_stock = int(rec.data.get("minimum_stock", 0))
        
        is_low_stock = qty <= min_stock
        is_expired = expiry_date < date.today() if expiry_date else False

        medicine_id = rec.data.get("medicine_id")
        
        from app.services.medicine_service import MedicineService
        medicine = MedicineService.get_medicine_by_id(medicine_id) if medicine_id else None

        return InventoryResponse(
            inventory_id=rec.id,
            medicine_id=medicine_id,
            batch_number=rec.data.get("batch_number", ""),
            expiry_date=expiry_date,
            purchase_price=Decimal(str(rec.data["purchase_price"])) if rec.data.get("purchase_price") else None,
            selling_price=Decimal(str(rec.data["selling_price"])) if rec.data.get("selling_price") else None,
            quantity_in_stock=qty,
            minimum_stock=min_stock,
            supplier=rec.data.get("supplier"),
            last_updated=datetime.utcnow(),
            is_low_stock=is_low_stock,
            is_expired=is_expired,
            medicine=medicine
        )

    @staticmethod
    def map_to_transaction(rec) -> InventoryTransactionResponse:
        txn_date = datetime.utcnow()
        date_str = rec.data.get("transaction_date")
        if date_str:
            try:
                txn_date = datetime.fromisoformat(date_str)
            except Exception:
                pass
                
        perf_id = rec.data.get("performed_by")
        performer = None
        if perf_id:
            from app.services.staff_service import StaffService
            performer = StaffService.get_staff_by_id(perf_id)
            
        return InventoryTransactionResponse(
            transaction_id=rec.id,
            inventory_id=rec.data.get("inventory_id", ""),
            performed_by=perf_id,
            transaction_type=rec.data.get("transaction_type", ""),
            quantity=int(rec.data.get("quantity", 0)),
            reference_type=rec.data.get("reference_type"),
            reference_id=rec.data.get("reference_id"),
            remarks=rec.data.get("remarks"),
            transaction_date=txn_date,
            performer=performer
        )

    @staticmethod
    def get_all_inventory(
        page: int = 1,
        per_page: int = 15,
        search: Optional[str] = None,
        filter_type: Optional[str] = None,
    ) -> EAVPagination:
        """Get paginated list of inventory items."""
        def action(ctx) -> EAVPagination:
            # Fetch all items to filter in memory due to complex joint search/EAV operator constraints
            req = ListRecordsRequest(context=ctx, module_id="inventory", page=1, page_size=1000)
            resp = crud_provider.records.list_records(req)
            all_items = [InventoryService.map_to_inventory(r) for r in resp.items]

            filtered = all_items
            if search:
                s = search.lower().strip()
                filtered = [
                    inv for inv in filtered
                    if (inv.medicine and s in inv.medicine.medicine_name.lower())
                    or s in inv.batch_number.lower()
                    or (inv.supplier and s in inv.supplier.lower())
                ]
            
            if filter_type == 'low':
                filtered = [inv for inv in filtered if inv.is_low_stock]
            elif filter_type == 'expired':
                filtered = [inv for inv in filtered if inv.is_expired]

            total = len(filtered)
            start = (page - 1) * per_page
            end = start + per_page
            items = filtered[start:end]
            return EAVPagination(items, page, per_page, total)
        return run_in_context(action)

    @staticmethod
    def get_inventory_by_id(inventory_id: str) -> Optional[InventoryResponse]:
        """Get an inventory item by ID."""
        def action(ctx) -> InventoryResponse:
            req = GetRecordRequest(context=ctx, module_id="inventory", record_id=inventory_id)
            resp = crud_provider.records.get_record(req)
            return InventoryService.map_to_inventory(resp.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def create_inventory(
        data: Dict[str, Any], performed_by: Optional[str] = None
    ) -> InventoryResponse:
        """Create a new inventory item."""
        cleaned = clean_input_data(data)
        qty_stock = int(cleaned.get('quantity_in_stock', 0))
        min_stock = int(cleaned.get('minimum_stock', 0))

        exp_date = cleaned.get('expiry_date')
        if isinstance(exp_date, (date, datetime)):
            exp_date = exp_date.strftime("%Y-%m-%d")

        record_data = {
            "medicine_id": cleaned['medicine_id'],
            "batch_number": cleaned['batch_number'],
            "expiry_date": exp_date,
            "purchase_price": str(cleaned.get('purchase_price')) if cleaned.get('purchase_price') else None,
            "selling_price": str(cleaned.get('selling_price')) if cleaned.get('selling_price') else None,
            "quantity_in_stock": str(qty_stock),
            "minimum_stock": str(min_stock),
            "supplier": cleaned.get('supplier'),
            "last_updated": datetime.utcnow().isoformat()
        }

        def action(ctx) -> InventoryResponse:
            req = CreateRecordRequest(context=ctx, module_id="inventory", data=record_data)
            resp = crud_provider.records.create_record(req)
            inv_rec = resp.data

            if qty_stock > 0:
                txn_data = {
                    "inventory_id": inv_rec.id,
                    "transaction_type": "IN",
                    "quantity": str(qty_stock),
                    "reference_type": "PURCHASE",
                    "performed_by": performed_by,
                    "remarks": "Initial stock entry",
                    "transaction_date": datetime.utcnow().isoformat()
                }
                req_txn = CreateRecordRequest(context=ctx, module_id="inventory_transaction", data=txn_data)
                crud_provider.records.create_record(req_txn)

            return InventoryService.map_to_inventory(inv_rec)
        return run_in_context(action)

    @staticmethod
    def update_inventory(inventory_id: str, data: Dict[str, Any]) -> Optional[InventoryResponse]:
        """Update an existing inventory item."""
        cleaned = clean_input_data(data)
        exp_date = cleaned.get('expiry_date')
        if isinstance(exp_date, (date, datetime)):
            exp_date = exp_date.strftime("%Y-%m-%d")
        
        def action(ctx) -> InventoryResponse:
            req_get = GetRecordRequest(context=ctx, module_id="inventory", record_id=inventory_id)
            resp_get = crud_provider.records.get_record(req_get)
            current_data = resp_get.data.data
            
            editable_fields = (
                "batch_number",
                "purchase_price",
                "selling_price",
                "minimum_stock",
                "supplier"
            )
            for field in editable_fields:
                if field in cleaned:
                    current_data[field] = str(cleaned[field]) if cleaned[field] is not None else None
            
            if "expiry_date" in cleaned:
                current_data["expiry_date"] = exp_date
            current_data["last_updated"] = datetime.utcnow().isoformat()

            req_up = UpdateRecordRequest(context=ctx, record_id=inventory_id, module_id="inventory", data=current_data)
            resp_up = crud_provider.records.update_record(req_up)
            return InventoryService.map_to_inventory(resp_up.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def add_transaction(
        inventory_id: str, data: Dict[str, Any], performed_by: str
    ) -> None:
        """Add a stock transaction."""
        cleaned = clean_input_data(data)
        txn_type: str = cleaned['transaction_type']
        qty: int = int(cleaned['quantity'])

        def action(ctx) -> None:
            # 1. Fetch current inventory stock
            req_get = GetRecordRequest(context=ctx, module_id="inventory", record_id=inventory_id)
            resp_get = crud_provider.records.get_record(req_get)
            inv_data = resp_get.data.data

            # 2. Update stock level
            current_stock = int(inv_data.get("quantity_in_stock", 0))
            if txn_type == "IN":
                current_stock += qty
            else:
                current_stock -= qty
            inv_data["quantity_in_stock"] = str(current_stock)
            inv_data["last_updated"] = datetime.utcnow().isoformat()

            # Save inventory stock
            req_up = UpdateRecordRequest(context=ctx, record_id=inventory_id, module_id="inventory", data=inv_data)
            crud_provider.records.update_record(req_up)

            # 3. Write transaction log
            txn_data = {
                "inventory_id": inventory_id,
                "transaction_type": txn_type,
                "quantity": str(qty),
                "reference_type": cleaned.get('reference_type'),
                "reference_id": str(cleaned.get('reference_id')) if cleaned.get('reference_id') else None,
                "performed_by": performed_by,
                "remarks": cleaned.get('remarks'),
                "transaction_date": datetime.utcnow().isoformat()
            }
            req_txn = CreateRecordRequest(context=ctx, module_id="inventory_transaction", data=txn_data)
            crud_provider.records.create_record(req_txn)
        run_in_context(action)

    @staticmethod
    def get_recent_transactions(inventory_id: str, limit: int = 20) -> List[InventoryTransactionResponse]:
        """Get recent transactions for an inventory item."""
        def action(ctx) -> List[InventoryTransactionResponse]:
            resp = query_records(ctx, "inventory_transaction", {"inventory_id": inventory_id}, page=1, page_size=limit)
            return [InventoryService.map_to_transaction(r) for r in resp.items]
        return run_in_context(action)

    @staticmethod
    def get_all_medicines() -> List[MedicineResponse]:
        def action(ctx) -> List[MedicineResponse]:
            req = ListRecordsRequest(context=ctx, module_id="medicine", page=1, page_size=1000)
            resp = crud_provider.records.list_records(req)
            from app.services.medicine_service import MedicineService
            return [MedicineService.map_to_medicine(r) for r in resp.items]
        return run_in_context(action)
