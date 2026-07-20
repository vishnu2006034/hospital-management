"""Prescription service for business logic using hogc-crud-engine."""

from datetime import datetime
from typing import Dict, List, Optional, Any

from app.dtos.prescription import PrescriptionResponse
from app.dtos.inventory import InventoryResponse
from app.dtos.visit import VisitResponse
from app.extensions import crud_provider
from app.services.interfaces.prescription_service_interface import IPrescriptionService
from app.services.crud_helper import run_in_context, query_records, EAVPagination
from hogc.lib.contracts.crud.requests import CreateRecordRequest, GetRecordRequest, DeleteRecordRequest, ListRecordsRequest
from app.utils import clean_input_data

class PrescriptionService(IPrescriptionService):
    """Service layer for Prescription business operations using hogc-crud-engine."""

    @staticmethod
    def map_to_prescription(rec) -> PrescriptionResponse:
        inv_id = rec.data.get("inventory_id")
        pres_by = rec.data.get("prescribed_by")

        # Resolve inventory
        from app.services.inventory_service import InventoryService
        inventory_batch = InventoryService.get_inventory_by_id(inv_id) if inv_id else None
        
        # Resolve prescriber
        from app.services.staff_service import StaffService
        prescriber = StaffService.get_staff_by_id(pres_by) if pres_by else None

        qty = rec.data.get("quantity")
        
        return PrescriptionResponse(
            prescription_id=rec.id,
            visit_id=rec.data.get("visit_id", ""),
            inventory_id=inv_id or "",
            prescribed_by=pres_by or "",
            dosage=rec.data.get("dosage"),
            frequency=rec.data.get("frequency"),
            duration=rec.data.get("duration"),
            quantity=int(qty) if qty else None,
            instructions=rec.data.get("instructions"),
            created_at=datetime.utcnow(),
            inventory_batch=inventory_batch,
            prescriber=prescriber
        )

    @staticmethod
    def get_all_prescriptions(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> EAVPagination:
        """Get paginated list of prescriptions."""
        def action(ctx) -> EAVPagination:
            if search:
                req = ListRecordsRequest(context=ctx, module_id="prescription", page=1, page_size=1000)
                resp = crud_provider.records.list_records(req)
                all_items = [PrescriptionService.map_to_prescription(r) for r in resp.items]
                s = search.lower().strip()
                filtered = [
                    p for p in all_items
                    if (p.inventory_batch and p.inventory_batch.medicine and s in p.inventory_batch.medicine.medicine_name.lower())
                    or (p.prescriber and s in p.prescriber.first_name.lower())
                    or (p.instructions and s in p.instructions.lower())
                ]
                total = len(filtered)
                start = (page - 1) * per_page
                end = start + per_page
                items = filtered[start:end]
                return EAVPagination(items, page, per_page, total)
            else:
                req = ListRecordsRequest(context=ctx, module_id="prescription", page=page, page_size=per_page)
                resp = crud_provider.records.list_records(req)
                items = [PrescriptionService.map_to_prescription(r) for r in resp.items]
                return EAVPagination(items, page, per_page, resp.total)
        return run_in_context(action)

    @staticmethod
    def get_prescription_by_id(prescription_id: str) -> Optional[PrescriptionResponse]:
        """Get a prescription by ID."""
        def action(ctx) -> PrescriptionResponse:
            req = GetRecordRequest(context=ctx, module_id="prescription", record_id=prescription_id)
            resp = crud_provider.records.get_record(req)
            return PrescriptionService.map_to_prescription(resp.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def create_prescription(data: Dict[str, Any], prescribed_by: str) -> PrescriptionResponse:
        """Create a new prescription."""
        cleaned = clean_input_data(data)
        qty_val = cleaned.get('quantity')
        qty = int(qty_val) if qty_val is not None else None

        record_data = {
            "visit_id": cleaned['visit_id'],
            "inventory_id": cleaned['inventory_id'],
            "dosage": cleaned.get('dosage'),
            "frequency": cleaned.get('frequency'),
            "duration": cleaned.get('duration'),
            "quantity": str(qty) if qty is not None else None,
            "instructions": cleaned.get('instructions'),
            "prescribed_by": prescribed_by
        }

        def action(ctx) -> PrescriptionResponse:
            req = CreateRecordRequest(context=ctx, module_id="prescription", data=record_data)
            resp = crud_provider.records.create_record(req)
            presc_rec = resp.data

            if qty:
                from app.services.inventory_service import InventoryService
                InventoryService.add_transaction(
                    inventory_id=cleaned['inventory_id'],
                    data={
                        "transaction_type": "OUT",
                        "quantity": qty,
                        "reference_type": "PRESCRIPTION",
                        "reference_id": presc_rec.id,
                        "remarks": f"Deducted for prescription {presc_rec.id}"
                    },
                    performed_by=prescribed_by
                )

            return PrescriptionService.map_to_prescription(presc_rec)
        return run_in_context(action)

    @staticmethod
    def delete_prescription(prescription_id: str) -> None:
        """Delete a prescription."""
        def action(ctx) -> None:
            req = DeleteRecordRequest(context=ctx, record_id=prescription_id, module_id="prescription")
            crud_provider.records.delete_record(req)
        run_in_context(action)

    @staticmethod
    def get_available_inventory() -> List[InventoryResponse]:
        """Get all available inventory items."""
        from app.services.inventory_service import InventoryService
        def action(ctx) -> List[InventoryResponse]:
            req = ListRecordsRequest(context=ctx, module_id="inventory", page=1, page_size=1000)
            resp = crud_provider.records.list_records(req)
            all_items = [InventoryService.map_to_inventory(r) for r in resp.items]
            return [inv for inv in all_items if inv.quantity_in_stock > 0 and not inv.is_expired]
        return run_in_context(action)

    @staticmethod
    def get_recent_visits(limit: int = 50) -> List[VisitResponse]:
        """Get recent visits."""
        from app.services.visit_service import VisitService
        def action(ctx) -> List[VisitResponse]:
            req = ListRecordsRequest(context=ctx, module_id="visit", page=1, page_size=limit)
            resp = crud_provider.records.list_records(req)
            return [VisitService.map_to_visit(r) for r in resp.items]
        return run_in_context(action)
