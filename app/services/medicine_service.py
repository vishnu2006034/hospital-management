"""Medicine service for business logic using hogc-crud-engine."""

from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Any

from app.dtos.medicine import MedicineResponse
from app.extensions import crud_provider
from app.services.interfaces.medicine_service_interface import IMedicineService
from app.services.crud_helper import run_in_context, query_records, EAVPagination
from hogc.lib.contracts.crud.requests import CreateRecordRequest, GetRecordRequest, UpdateRecordRequest, DeleteRecordRequest, ListRecordsRequest
from app.utils import clean_input_data

class MedicineService(IMedicineService):
    """Service layer for Medicine business operations using hogc-crud-engine."""

    @staticmethod
    def map_to_medicine(rec) -> MedicineResponse:
        return MedicineResponse(
            medicine_id=rec.id,
            medicine_name=rec.data.get("medicine_name", ""),
            generic_name=rec.data.get("generic_name"),
            category=rec.data.get("category"),
            dosage_form=rec.data.get("dosage_form"),
            strength=rec.data.get("strength"),
            manufacturer=rec.data.get("manufacturer"),
            unit_price=Decimal(str(rec.data["unit_price"])) if rec.data.get("unit_price") else None,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def get_all_medicines(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> EAVPagination:
        """Get paginated list of medicines."""
        def action(ctx) -> EAVPagination:
            if search:
                req = ListRecordsRequest(context=ctx, module_id="medicine", page=1, page_size=1000)
                resp = crud_provider.records.list_records(req)
                all_items = [MedicineService.map_to_medicine(r) for r in resp.items]
                s = search.lower().strip()
                filtered = [
                    m for m in all_items
                    if s in m.medicine_name.lower()
                    or (m.generic_name and s in m.generic_name.lower())
                    or (m.manufacturer and s in m.manufacturer.lower())
                ]
                total = len(filtered)
                start = (page - 1) * per_page
                end = start + per_page
                items = filtered[start:end]
                return EAVPagination(items, page, per_page, total)
            else:
                req = ListRecordsRequest(context=ctx, module_id="medicine", page=page, page_size=per_page)
                resp = crud_provider.records.list_records(req)
                items = [MedicineService.map_to_medicine(r) for r in resp.items]
                return EAVPagination(items, page, per_page, resp.total)
        return run_in_context(action)

    @staticmethod
    def get_medicine_by_id(medicine_id: str) -> Optional[MedicineResponse]:
        """Get a medicine by ID."""
        def action(ctx) -> MedicineResponse:
            req = GetRecordRequest(context=ctx, module_id="medicine", record_id=medicine_id)
            resp = crud_provider.records.get_record(req)
            return MedicineService.map_to_medicine(resp.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def create_medicine(data: Dict[str, Any]) -> MedicineResponse:
        """Create a new medicine."""
        cleaned = clean_input_data(data)
        record_data = {
            "medicine_name": cleaned['medicine_name'],
            "generic_name": cleaned.get('generic_name'),
            "category": cleaned.get('category'),
            "dosage_form": cleaned.get('dosage_form'),
            "strength": cleaned.get('strength'),
            "manufacturer": cleaned.get('manufacturer'),
            "unit_price": str(cleaned['unit_price']) if cleaned.get('unit_price') else "0.0"
        }

        def action(ctx) -> MedicineResponse:
            req = CreateRecordRequest(context=ctx, module_id="medicine", data=record_data)
            resp = crud_provider.records.create_record(req)
            return MedicineService.map_to_medicine(resp.data)
        return run_in_context(action)

    @staticmethod
    def update_medicine(medicine_id: str, data: Dict[str, Any]) -> Optional[MedicineResponse]:
        """Update an existing medicine."""
        cleaned = clean_input_data(data)
        
        def action(ctx) -> MedicineResponse:
            req_get = GetRecordRequest(context=ctx, module_id="medicine", record_id=medicine_id)
            resp_get = crud_provider.records.get_record(req_get)
            current_data = resp_get.data.data
            
            editable_fields = (
                "medicine_name",
                "generic_name",
                "category",
                "dosage_form",
                "strength",
                "manufacturer",
                "unit_price",
            )
            for field in editable_fields:
                if field in cleaned:
                    current_data[field] = str(cleaned[field]) if cleaned[field] is not None else None

            req_up = UpdateRecordRequest(context=ctx, record_id=medicine_id, module_id="medicine", data=current_data)
            resp_up = crud_provider.records.update_record(req_up)
            return MedicineService.map_to_medicine(resp_up.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def delete_medicine(medicine_id: str) -> None:
        """Delete a medicine."""
        def action(ctx) -> None:
            req = DeleteRecordRequest(context=ctx, record_id=medicine_id, module_id="medicine")
            crud_provider.records.delete_record(req)
        run_in_context(action)
