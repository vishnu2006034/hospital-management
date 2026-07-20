"""Visit service for business logic using hogc-crud-engine."""

from datetime import datetime, date
import random
from decimal import Decimal
from typing import Dict, List, Optional, Any

from app.dtos.visit import VisitResponse
from app.dtos.patient import PatientResponse
from app.dtos.user import UserResponse
from app.extensions import crud_provider
from app.services.interfaces.visit_service_interface import IVisitService
from app.services.crud_helper import run_in_context, query_records, EAVPagination
from hogc.lib.contracts.crud.requests import CreateRecordRequest, GetRecordRequest, UpdateRecordRequest, DeleteRecordRequest, ListRecordsRequest
from app.utils import clean_input_data

class VisitService(IVisitService):
    """Service layer for Visit business operations using hogc-crud-engine."""

    @staticmethod
    def map_to_visit(rec) -> VisitResponse:
        visit_date = datetime.utcnow()
        v_date_str = rec.data.get("visit_date")
        if v_date_str:
            try:
                visit_date = datetime.fromisoformat(v_date_str)
            except Exception:
                pass
                
        adm_date = None
        adm_str = rec.data.get("admission_date")
        if adm_str:
            try:
                adm_date = datetime.fromisoformat(adm_str)
            except Exception:
                pass
                
        dis_date = None
        dis_str = rec.data.get("discharge_date")
        if dis_str:
            try:
                dis_date = datetime.fromisoformat(dis_str)
            except Exception:
                pass

        patient_id = rec.data.get("patient_id")
        doctor_id = rec.data.get("doctor_id")

        # Resolve nested patient
        from app.services.patient_service import PatientService
        patient = PatientService.get_patient_by_id(patient_id) if patient_id else None
        
        # Resolve nested doctor
        doctor = None
        if doctor_id:
            from app.services.staff_service import StaffService
            doctor = StaffService.get_staff_by_id(doctor_id)

        return VisitResponse(
            visit_id=rec.id,
            patient_id=patient_id,
            doctor_id=doctor_id,
            visit_type=rec.data.get("visit_type", "OUTPATIENT"),
            visit_status=rec.data.get("visit_status", "OPEN"),
            visit_date=visit_date,
            admission_date=adm_date,
            discharge_date=dis_date,
            chief_complaint=rec.data.get("chief_complaint"),
            diagnosis=rec.data.get("diagnosis"),
            treatment_plan=rec.data.get("treatment_plan"),
            notes=rec.data.get("notes"),
            height=Decimal(str(rec.data["height"])) if rec.data.get("height") else None,
            weight=Decimal(str(rec.data["weight"])) if rec.data.get("weight") else None,
            temperature=Decimal(str(rec.data["temperature"])) if rec.data.get("temperature") else None,
            blood_pressure=rec.data.get("blood_pressure"),
            pulse_rate=int(rec.data["pulse_rate"]) if rec.data.get("pulse_rate") else None,
            oxygen_level=int(rec.data["oxygen_level"]) if rec.data.get("oxygen_level") else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            patient=patient,
            doctor=doctor
        )

    @staticmethod
    def get_all_visits(
        page: int = 1,
        per_page: int = 15,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> EAVPagination:
        """Get paginated list of visits."""
        def action(ctx) -> EAVPagination:
            filters = {}
            if status:
                filters["visit_status"] = status
                
            if search:
                # EAV limitation fallback search in-memory
                req = ListRecordsRequest(context=ctx, module_id="visit", page=1, page_size=1000)
                resp = crud_provider.records.list_records(req)
                all_items = [VisitService.map_to_visit(r) for r in resp.items]
                s = search.lower().strip()
                filtered = [
                    v for v in all_items
                    if (v.patient and s in v.patient.first_name.lower())
                    or (v.patient and v.patient.last_name and s in v.patient.last_name.lower())
                    or (v.doctor and s in v.doctor.first_name.lower())
                    or (v.chief_complaint and s in v.chief_complaint.lower())
                    or (v.diagnosis and s in v.diagnosis.lower())
                ]
                # Filter by status if needed
                if status:
                    filtered = [v for v in filtered if v.visit_status == status]
                total = len(filtered)
                start = (page - 1) * per_page
                end = start + per_page
                items = filtered[start:end]
                return EAVPagination(items, page, per_page, total)
            else:
                resp = query_records(ctx, "visit", filters, page=page, page_size=per_page, sort_field="visit_date")
                items = [VisitService.map_to_visit(r) for r in resp.items]
                return EAVPagination(items, page, per_page, resp.total)
        return run_in_context(action)

    @staticmethod
    def get_visit_by_id(visit_id: str) -> Optional[VisitResponse]:
        """Get a visit by ID."""
        def action(ctx) -> VisitResponse:
            req = GetRecordRequest(context=ctx, module_id="visit", record_id=visit_id)
            resp = crud_provider.records.get_record(req)
            return VisitService.map_to_visit(resp.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def create_visit(
        data: Dict[str, Any], admission_date: Optional[str] = None
    ) -> VisitResponse:
        """Create a new visit."""
        cleaned = clean_input_data(data)
        
        adm_date = admission_date if (admission_date and admission_date.strip()) else None
        if isinstance(adm_date, (date, datetime)):
            adm_date = adm_date.isoformat()
            
        visit_number = f"VIS-{random.randint(10000, 99999)}"

        record_data = {
            "visit_number": visit_number,
            "patient_id": cleaned['patient_id'],
            "doctor_id": cleaned['doctor_id'],
            "visit_type": cleaned.get('visit_type') or 'OUTPATIENT',
            "visit_status": 'OPEN',
            "visit_date": datetime.utcnow().isoformat(),
            "chief_complaint": cleaned.get('chief_complaint'),
            "diagnosis": cleaned.get('diagnosis'),
            "treatment_plan": cleaned.get('treatment_plan'),
            "notes": cleaned.get('notes'),
            "height": str(cleaned['height']) if cleaned.get('height') else None,
            "weight": str(cleaned['weight']) if cleaned.get('weight') else None,
            "temperature": str(cleaned['temperature']) if cleaned.get('temperature') else None,
            "blood_pressure": cleaned.get('blood_pressure'),
            "pulse_rate": cleaned.get('pulse_rate'),
            "oxygen_level": cleaned.get('oxygen_level'),
            "admission_date": adm_date
        }

        def action(ctx) -> VisitResponse:
            req = CreateRecordRequest(context=ctx, module_id="visit", data=record_data)
            resp = crud_provider.records.create_record(req)
            return VisitService.map_to_visit(resp.data)
        return run_in_context(action)

    @staticmethod
    def update_visit(
        visit_id: str,
        data: Dict[str, Any],
        admission_date: Optional[str] = None,
        discharge_date: Optional[str] = None,
    ) -> Optional[VisitResponse]:
        """Update an existing visit."""
        cleaned = clean_input_data(data)
        
        def action(ctx) -> VisitResponse:
            req_get = GetRecordRequest(context=ctx, module_id="visit", record_id=visit_id)
            resp_get = crud_provider.records.get_record(req_get)
            current_data = resp_get.data.data
            
            editable_fields = (
                "visit_type",
                "visit_status",
                "chief_complaint",
                "diagnosis",
                "treatment_plan",
                "notes",
                "height",
                "weight",
                "temperature",
                "blood_pressure",
                "pulse_rate",
                "oxygen_level",
            )
            for field in editable_fields:
                if field in cleaned:
                    current_data[field] = str(cleaned[field]) if cleaned[field] is not None else None
            
            if admission_date and admission_date.strip():
                current_data["admission_date"] = admission_date
            if discharge_date and discharge_date.strip():
                current_data["discharge_date"] = discharge_date

            req_up = UpdateRecordRequest(context=ctx, record_id=visit_id, module_id="visit", data=current_data)
            resp_up = crud_provider.records.update_record(req_up)
            return VisitService.map_to_visit(resp_up.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def delete_visit(visit_id: str) -> None:
        """Delete a visit."""
        def action(ctx) -> None:
            req = DeleteRecordRequest(context=ctx, record_id=visit_id, module_id="visit")
            crud_provider.records.delete_record(req)
        run_in_context(action)

    @staticmethod
    def get_all_patients() -> List[PatientResponse]:
        def action(ctx) -> List[PatientResponse]:
            req = ListRecordsRequest(context=ctx, module_id="patient", page=1, page_size=1000)
            resp = crud_provider.records.list_records(req)
            from app.services.patient_service import PatientService
            return [PatientService.map_to_patient(r) for r in resp.items]
        return run_in_context(action)

    @staticmethod
    def get_all_doctors() -> List[UserResponse]:
        """Get all doctors."""
        def action(ctx) -> List[UserResponse]:
            resp = query_records(ctx, "user", {"role": "DOCTOR"}, page=1, page_size=1000)
            from app.services.staff_service import StaffService
            return [StaffService.map_to_staff(r) for r in resp.items]
        return run_in_context(action)

    @staticmethod
    def get_visit_details(visit_id: str) -> Dict[str, List[Any]]:
        """Get all related entities for a visit."""
        def action(ctx) -> Dict[str, List[Any]]:
            # Prescriptions
            from app.services.prescription_service import PrescriptionService
            presc_resp = query_records(ctx, "prescription", {"visit_id": visit_id}, page=1, page_size=100)
            prescriptions = [PrescriptionService.map_to_prescription(r) for r in presc_resp.items]
            
            # Lab requests
            from app.services.laboratory_service import LaboratoryService
            lab_resp = query_records(ctx, "laboratory", {"visit_id": visit_id}, page=1, page_size=100)
            lab_requests = [LaboratoryService.map_to_laboratory(r) for r in lab_resp.items]
            
            # Doctor reports
            from app.services.report_service import ReportService
            rep_resp = query_records(ctx, "report", {"visit_id": visit_id}, page=1, page_size=100)
            doctor_reports = [ReportService.map_to_report(r) for r in rep_resp.items]
            
            return {
                'prescriptions': prescriptions,
                'lab_requests': lab_requests,
                'doctor_reports': doctor_reports
            }
        return run_in_context(action)

    @staticmethod
    def get_today_appointments_count() -> int:
        """Count today's visits/appointments."""
        def action(ctx) -> int:
            resp = query_records(ctx, "visit", {}, page=1, page_size=1000)
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            return sum(1 for r in resp.items if r.data.get("visit_date", "")[:10] == today_str)
        return run_in_context(action)

    @staticmethod
    def get_active_admissions_count() -> int:
        """Count active inpatient admissions."""
        def action(ctx) -> int:
            resp = query_records(ctx, "visit", {"visit_status": "OPEN", "visit_type": "INPATIENT"}, page=1, page_size=1)
            return resp.total
        return run_in_context(action)
