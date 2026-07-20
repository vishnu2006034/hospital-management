"""Patient service for business logic using hogc-crud-engine."""

import random
from datetime import datetime, date
from typing import Dict, List, Optional, Any

from app.dtos.patient import PatientResponse
from app.dtos.visit import VisitResponse
from app.extensions import crud_provider
from app.services.interfaces.patient_service_interface import IPatientService
from app.services.crud_helper import run_in_context, query_records, EAVPagination
from hogc.lib.contracts.crud.requests import CreateRecordRequest, GetRecordRequest, UpdateRecordRequest, DeleteRecordRequest, ListRecordsRequest
from app.utils import clean_input_data

class PatientService(IPatientService):
    """Service layer for Patient business operations using hogc-crud-engine."""

    @staticmethod
    def map_to_patient(rec) -> PatientResponse:
        dob = None
        dob_str = rec.data.get("dob")
        if dob_str:
            try:
                dob = datetime.strptime(dob_str[:10], "%Y-%m-%d").date()
            except Exception:
                pass
        return PatientResponse(
            patient_id=rec.id,
            patient_number=rec.data.get("patient_number", ""),
            first_name=rec.data.get("first_name", ""),
            last_name=rec.data.get("last_name"),
            gender=rec.data.get("gender"),
            dob=dob,
            blood_group=rec.data.get("blood_group"),
            phone=rec.data.get("phone"),
            email=rec.data.get("email"),
            address=rec.data.get("address"),
            emergency_contact_name=rec.data.get("emergency_contact_name"),
            emergency_contact_phone=rec.data.get("emergency_contact_phone"),
            allergies=rec.data.get("allergies"),
            medical_history=rec.data.get("medical_history"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            full_name=f"{rec.data.get('first_name', '')} {rec.data.get('last_name', '')}".strip()
        )

    @staticmethod
    def get_all_patients(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> EAVPagination:
        """Get paginated list of patients."""
        def action(ctx) -> EAVPagination:
            if search:
                req = ListRecordsRequest(context=ctx, module_id="patient", page=1, page_size=1000)
                resp = crud_provider.records.list_records(req)
                all_items = [PatientService.map_to_patient(r) for r in resp.items]
                s = search.lower().strip()
                filtered = [
                    p for p in all_items
                    if s in p.first_name.lower()
                    or (p.last_name and s in p.last_name.lower())
                    or (p.patient_number and s in p.patient_number.lower())
                    or (p.phone and s in p.phone)
                ]
                total = len(filtered)
                start = (page - 1) * per_page
                end = start + per_page
                items = filtered[start:end]
                return EAVPagination(items, page, per_page, total)
            else:
                req = ListRecordsRequest(context=ctx, module_id="patient", page=page, page_size=per_page)
                resp = crud_provider.records.list_records(req)
                items = [PatientService.map_to_patient(r) for r in resp.items]
                return EAVPagination(items, page, per_page, resp.total)
        return run_in_context(action)

    @staticmethod
    def get_patient_by_id(patient_id: str) -> Optional[PatientResponse]:
        """Get a patient by ID."""
        def action(ctx) -> PatientResponse:
            req = GetRecordRequest(context=ctx, module_id="patient", record_id=patient_id)
            resp = crud_provider.records.get_record(req)
            return PatientService.map_to_patient(resp.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def generate_patient_number() -> str:
        return f"PAT-{random.randint(100000, 999999)}"

    @staticmethod
    def create_patient(data: Dict[str, Any]) -> PatientResponse:
        """Create a new patient."""
        cleaned = clean_input_data(data)
        patient_num = PatientService.generate_patient_number()

        dob_val = cleaned.get("dob")
        if isinstance(dob_val, (date, datetime)):
            dob_val = dob_val.strftime("%Y-%m-%d")

        record_data = {
            "patient_number": patient_num,
            "first_name": cleaned["first_name"],
            "last_name": cleaned.get("last_name"),
            "gender": cleaned.get("gender"),
            "dob": dob_val,
            "blood_group": cleaned.get("blood_group"),
            "phone": cleaned.get("phone"),
            "email": cleaned.get("email"),
            "address": cleaned.get("address"),
            "emergency_contact_name": cleaned.get("emergency_contact_name"),
            "emergency_contact_phone": cleaned.get("emergency_contact_phone"),
            "allergies": cleaned.get("allergies"),
            "medical_history": cleaned.get("medical_history")
        }

        def action(ctx) -> PatientResponse:
            req = CreateRecordRequest(context=ctx, module_id="patient", data=record_data)
            resp = crud_provider.records.create_record(req)
            return PatientService.map_to_patient(resp.data)
        return run_in_context(action)

    @staticmethod
    def update_patient(patient_id: str, data: Dict[str, Any]) -> Optional[PatientResponse]:
        """Update an existing patient."""
        cleaned = clean_input_data(data)
        dob_val = cleaned.get("dob")
        if isinstance(dob_val, (date, datetime)):
            dob_val = dob_val.strftime("%Y-%m-%d")

        editable_fields = (
            "first_name",
            "last_name",
            "gender",
            "dob",
            "blood_group",
            "phone",
            "email",
            "address",
            "emergency_contact_name",
            "emergency_contact_phone",
            "allergies",
            "medical_history",
        )
        
        def action(ctx) -> PatientResponse:
            req_get = GetRecordRequest(context=ctx, module_id="patient", record_id=patient_id)
            resp_get = crud_provider.records.get_record(req_get)
            current_data = resp_get.data.data
            
            for field in editable_fields:
                if field in cleaned:
                    current_data[field] = cleaned[field]
            if "dob" in cleaned:
                current_data["dob"] = dob_val

            req_up = UpdateRecordRequest(context=ctx, record_id=patient_id, module_id="patient", data=current_data)
            resp_up = crud_provider.records.update_record(req_up)
            return PatientService.map_to_patient(resp_up.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def delete_patient(patient_id: str) -> None:
        """Delete a patient."""
        def action(ctx) -> None:
            req = DeleteRecordRequest(context=ctx, record_id=patient_id, module_id="patient")
            crud_provider.records.delete_record(req)
        run_in_context(action)

    @staticmethod
    def get_patient_visits(patient_id: str, limit: int = 20) -> List[VisitResponse]:
        """Get recent visits for a patient."""
        from app.services.visit_service import VisitService
        def action(ctx) -> List[VisitResponse]:
            resp = query_records(ctx, "visit", {"patient_id": patient_id}, page=1, page_size=limit)
            return [VisitService.map_to_visit(r) for r in resp.items]
        return run_in_context(action)

    @staticmethod
    def get_total_patients_count() -> int:
        """Count total patients."""
        def action(ctx) -> int:
            req = ListRecordsRequest(context=ctx, module_id="patient", page=1, page_size=1)
            resp = crud_provider.records.list_records(req)
            return resp.total
        return run_in_context(action)