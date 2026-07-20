"""Report service for business logic using hogc-crud-engine."""

from datetime import datetime, date
from typing import Dict, List, Optional, Any

from app.dtos.report import ReportResponse
from app.dtos.visit import VisitResponse
from app.dtos.patient import PatientResponse
from app.extensions import crud_provider
from app.services.interfaces.report_service_interface import IReportService
from app.services.crud_helper import run_in_context, query_records, EAVPagination
from hogc.lib.contracts.crud.requests import CreateRecordRequest, GetRecordRequest, UpdateRecordRequest, ListRecordsRequest
from app.utils import clean_input_data

class ReportService(IReportService):
    """Service layer for DoctorReport business operations using hogc-crud-engine."""

    @staticmethod
    def map_to_report(rec) -> ReportResponse:
        f_date = None
        f_str = rec.data.get("follow_up_date")
        if f_str:
            try:
                f_date = datetime.strptime(f_str[:10], "%Y-%m-%d").date()
            except Exception:
                pass

        visit_id = rec.data.get("visit_id")
        patient_id = rec.data.get("patient_id")
        doctor_id = rec.data.get("doctor_id")

        from app.services.visit_service import VisitService
        visit = VisitService.get_visit_by_id(visit_id) if visit_id else None
        
        from app.services.patient_service import PatientService
        patient = PatientService.get_patient_by_id(patient_id) if patient_id else None
        
        from app.services.staff_service import StaffService
        doctor = StaffService.get_staff_by_id(doctor_id) if doctor_id else None

        return ReportResponse(
            doctor_report_id=rec.id,
            visit_id=visit_id or "",
            patient_id=patient_id or "",
            doctor_id=doctor_id or "",
            report_number=rec.data.get("report_number", ""),
            chief_complaint=rec.data.get("chief_complaint"),
            clinical_findings=rec.data.get("clinical_findings"),
            diagnosis=rec.data.get("diagnosis"),
            treatment_plan=rec.data.get("treatment_plan"),
            prescribed_medicines=rec.data.get("prescribed_medicines"),
            doctor_notes=rec.data.get("doctor_notes"),
            follow_up_required=rec.data.get("follow_up_required", "False") == "True",
            follow_up_date=f_date,
            next_visit_reason=rec.data.get("next_visit_reason"),
            report_file=rec.data.get("report_file"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            visit=visit,
            patient=patient,
            doctor=doctor
        )

    @staticmethod
    def get_all_reports(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> EAVPagination:
        """Get paginated list of doctor reports."""
        def action(ctx) -> EAVPagination:
            if search:
                req = ListRecordsRequest(context=ctx, module_id="report", page=1, page_size=1000)
                resp = crud_provider.records.list_records(req)
                all_items = [ReportService.map_to_report(r) for r in resp.items]
                s = search.lower().strip()
                filtered = [
                    r for r in all_items
                    if (r.patient and s in r.patient.first_name.lower())
                    or (r.patient and r.patient.last_name and s in r.patient.last_name.lower())
                    or (r.doctor and s in r.doctor.first_name.lower())
                    or (r.diagnosis and s in r.diagnosis.lower())
                    or s in r.report_number.lower()
                ]
                total = len(filtered)
                start = (page - 1) * per_page
                end = start + per_page
                items = filtered[start:end]
                return EAVPagination(items, page, per_page, total)
            else:
                req = ListRecordsRequest(context=ctx, module_id="report", page=page, page_size=per_page)
                resp = crud_provider.records.list_records(req)
                items = [ReportService.map_to_report(r) for r in resp.items]
                return EAVPagination(items, page, per_page, resp.total)
        return run_in_context(action)

    @staticmethod
    def get_report_by_id(report_id: str) -> Optional[ReportResponse]:
        """Get a doctor report by ID."""
        def action(ctx) -> ReportResponse:
            req = GetRecordRequest(context=ctx, module_id="report", record_id=report_id)
            resp = crud_provider.records.get_record(req)
            return ReportService.map_to_report(resp.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def generate_report_number() -> str:
        """Generate a new doctor report number."""
        import random
        return f"DR-{random.randint(100000, 999999)}"

    @staticmethod
    def create_report(data: Dict[str, Any], doctor_id: str) -> ReportResponse:
        """Create a new doctor report."""
        cleaned = clean_input_data(data)
        report_number = ReportService.generate_report_number()

        f_date = cleaned.get("follow_up_date")
        if isinstance(f_date, (date, datetime)):
            f_date = f_date.strftime("%Y-%m-%d")

        record_data = {
            "visit_id": cleaned['visit_id'],
            "patient_id": cleaned['patient_id'],
            "doctor_id": doctor_id,
            "report_number": report_number,
            "chief_complaint": cleaned.get('chief_complaint'),
            "clinical_findings": cleaned.get('clinical_findings'),
            "diagnosis": cleaned.get('diagnosis'),
            "treatment_plan": cleaned.get('treatment_plan'),
            "prescribed_medicines": cleaned.get('prescribed_medicines'),
            "doctor_notes": cleaned.get('doctor_notes'),
            "follow_up_required": "True" if cleaned.get('follow_up_required') else "False",
            "follow_up_date": f_date,
            "next_visit_reason": cleaned.get('next_visit_reason')
        }

        def action(ctx) -> ReportResponse:
            req = CreateRecordRequest(context=ctx, module_id="report", data=record_data)
            resp = crud_provider.records.create_record(req)
            return ReportService.map_to_report(resp.data)
        return run_in_context(action)

    @staticmethod
    def update_report(
        report_id: str, data: Dict[str, Any]
    ) -> Optional[ReportResponse]:
        """Update an existing doctor report."""
        cleaned = clean_input_data(data)
        f_date = cleaned.get("follow_up_date")
        if isinstance(f_date, (date, datetime)):
            f_date = f_date.strftime("%Y-%m-%d")

        def action(ctx) -> ReportResponse:
            req_get = GetRecordRequest(context=ctx, module_id="report", record_id=report_id)
            resp_get = crud_provider.records.get_record(req_get)
            current_data = resp_get.data.data
            
            editable_fields = (
                "chief_complaint",
                "clinical_findings",
                "diagnosis",
                "treatment_plan",
                "prescribed_medicines",
                "doctor_notes",
                "next_visit_reason",
            )
            for field in editable_fields:
                if field in cleaned:
                    current_data[field] = str(cleaned[field]) if cleaned[field] is not None else None
            
            if "follow_up_required" in cleaned:
                current_data["follow_up_required"] = "True" if cleaned["follow_up_required"] else "False"
            if "follow_up_date" in cleaned:
                current_data["follow_up_date"] = f_date

            req_up = UpdateRecordRequest(context=ctx, record_id=report_id, module_id="report", data=current_data)
            resp_up = crud_provider.records.update_record(req_up)
            return ReportService.map_to_report(resp_up.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def get_recent_visits(limit: int = 50) -> List[VisitResponse]:
        """Get recent visits."""
        from app.services.visit_service import VisitService
        def action(ctx) -> List[VisitResponse]:
            req = ListRecordsRequest(context=ctx, module_id="visit", page=1, page_size=limit)
            resp = crud_provider.records.list_records(req)
            return [VisitService.map_to_visit(r) for r in resp.items]
        return run_in_context(action)

    @staticmethod
    def get_all_patients() -> List[PatientResponse]:
        from app.services.patient_service import PatientService
        def action(ctx) -> List[PatientResponse]:
            req = ListRecordsRequest(context=ctx, module_id="patient", page=1, page_size=1000)
            resp = crud_provider.records.list_records(req)
            return [PatientService.map_to_patient(r) for r in resp.items]
        return run_in_context(action)
