"""Laboratory service for business logic using hogc-crud-engine."""

import random
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, List, Optional, Any

from app.dtos.laboratory import (
    LaboratoryResponse,
    LaboratoryCreateRequest,
    LaboratoryUpdateRequest,
    LabReportResponse,
    LabReportCreateRequest,
    LabTestCatalogResponse,
    LabTestCatalogCreateRequest,
    LabTestCatalogUpdateRequest,
)
from app.dtos.visit import VisitResponse
from app.dtos.patient import PatientResponse
from app.dtos.user import UserResponse
from app.extensions import crud_provider
from app.services.interfaces.laboratory_service_interface import ILaboratoryService
from app.services.crud_helper import run_in_context, query_records, EAVPagination
from hogc.lib.contracts.crud.requests import CreateRecordRequest, GetRecordRequest, UpdateRecordRequest, DeleteRecordRequest, ListRecordsRequest
from app.utils import clean_input_data

class LaboratoryService(ILaboratoryService):
    """Service layer for Laboratory business operations using hogc-crud-engine."""

    @staticmethod
    def map_to_catalog(rec) -> LabTestCatalogResponse:
        return LabTestCatalogResponse(
            test_id=rec.id,
            test_code=rec.data.get("test_code", ""),
            test_name=rec.data.get("test_name", ""),
            category=rec.data.get("category"),
            sample_type=rec.data.get("sample_type"),
            unit=rec.data.get("unit"),
            reference_range=rec.data.get("reference_range"),
            normal_min=Decimal(str(rec.data["normal_min"])) if rec.data.get("normal_min") else None,
            normal_max=Decimal(str(rec.data["normal_max"])) if rec.data.get("normal_max") else None,
            default_price=Decimal(str(rec.data["default_price"])) if rec.data.get("default_price") else None,
            description=rec.data.get("description"),
            is_active=rec.data.get("is_active", "True") == "True",
            created_at=datetime.utcnow()
        )

    @staticmethod
    def map_to_report(rec) -> LabReportResponse:
        v_date = None
        v_str = rec.data.get("verified_at")
        if v_str:
            try:
                v_date = datetime.fromisoformat(v_str)
            except Exception:
                pass
                
        test_id = rec.data.get("test_id")
        patient_id = rec.data.get("patient_id")
        doctor_id = rec.data.get("doctor_id")
        verified_by = rec.data.get("verified_by")

        # Resolve nested objects
        test = LaboratoryService.get_catalog_test_by_id(test_id) if test_id else None
        
        from app.services.patient_service import PatientService
        patient = PatientService.get_patient_by_id(patient_id) if patient_id else None
        
        from app.services.staff_service import StaffService
        doctor = StaffService.get_staff_by_id(doctor_id) if doctor_id else None
        verifier = StaffService.get_staff_by_id(verified_by) if verified_by else None

        return LabReportResponse(
            lab_report_id=rec.id,
            lab_id=rec.data.get("lab_id", ""),
            test_id=test_id or "",
            patient_id=patient_id or "",
            doctor_id=doctor_id or "",
            verified_by=verified_by,
            report_number=rec.data.get("report_number", ""),
            result=rec.data.get("result", ""),
            unit=rec.data.get("unit"),
            reference_range=rec.data.get("reference_range"),
            is_abnormal=rec.data.get("is_abnormal", "False") == "True",
            remarks=rec.data.get("remarks"),
            verified_at=v_date,
            report_file=rec.data.get("report_file"),
            created_at=datetime.utcnow(),
            test=test,
            patient=patient,
            doctor=doctor,
            verifier=verifier
        )

    @staticmethod
    def map_to_laboratory(rec) -> LaboratoryResponse:
        collected_at = None
        col_str = rec.data.get("sample_collected_at")
        if col_str:
            try:
                collected_at = datetime.fromisoformat(col_str)
            except Exception:
                pass
                
        completed_at = None
        comp_str = rec.data.get("completed_at")
        if comp_str:
            try:
                completed_at = datetime.fromisoformat(comp_str)
            except Exception:
                pass

        visit_id = rec.data.get("visit_id")
        patient_id = rec.data.get("patient_id")
        req_by = rec.data.get("requested_by")
        tech_id = rec.data.get("lab_technician_id")

        from app.services.visit_service import VisitService
        visit = VisitService.get_visit_by_id(visit_id) if visit_id else None
        
        from app.services.patient_service import PatientService
        patient = PatientService.get_patient_by_id(patient_id) if patient_id else None
        
        from app.services.staff_service import StaffService
        requester = StaffService.get_staff_by_id(req_by) if req_by else None
        technician = StaffService.get_staff_by_id(tech_id) if tech_id else None

        reports = LaboratoryService.get_lab_reports(rec.id)

        return LaboratoryResponse(
            lab_id=rec.id,
            visit_id=visit_id or "",
            patient_id=patient_id or "",
            requested_by=req_by or "",
            lab_technician_id=tech_id,
            priority=rec.data.get("priority", "NORMAL"),
            sample_type=rec.data.get("sample_type"),
            sample_collected_at=collected_at,
            test_status=rec.data.get("test_status", "PENDING"),
            remarks=rec.data.get("remarks"),
            created_at=datetime.utcnow(),
            completed_at=completed_at,
            visit=visit,
            patient=patient,
            requester=requester,
            technician=technician,
            reports=reports
        )

    @staticmethod
    def get_all_lab_requests(
        page: int = 1,
        per_page: int = 15,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> EAVPagination:
        """Get paginated list of lab requests."""
        def action(ctx) -> EAVPagination:
            filters = {}
            if status:
                filters["test_status"] = status
            
            if search:
                req = ListRecordsRequest(context=ctx, module_id="laboratory", page=1, page_size=1000)
                resp = crud_provider.records.list_records(req)
                all_items = [LaboratoryService.map_to_laboratory(r) for r in resp.items]
                s = search.lower().strip()
                filtered = [
                    l for l in all_items
                    if (l.patient and s in l.patient.first_name.lower())
                    or (l.patient and l.patient.last_name and s in l.patient.last_name.lower())
                    or (l.patient and s in l.patient.patient_number.lower())
                    or (l.requester and s in l.requester.first_name.lower())
                ]
                if status:
                    filtered = [l for l in filtered if l.test_status == status]
                total = len(filtered)
                start = (page - 1) * per_page
                end = start + per_page
                items = filtered[start:end]
                return EAVPagination(items, page, per_page, total)
            else:
                resp = query_records(ctx, "laboratory", filters, page=page, page_size=per_page, sort_field="created_at")
                items = [LaboratoryService.map_to_laboratory(r) for r in resp.items]
                return EAVPagination(items, page, per_page, resp.total)
        return run_in_context(action)

    @staticmethod
    def get_lab_by_id(lab_id: str) -> Optional[LaboratoryResponse]:
        """Get a lab request by ID."""
        def action(ctx) -> LaboratoryResponse:
            req = GetRecordRequest(context=ctx, module_id="laboratory", record_id=lab_id)
            resp = crud_provider.records.get_record(req)
            return LaboratoryService.map_to_laboratory(resp.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def create_lab_request(data: Dict[str, Any], requested_by: str) -> LaboratoryResponse:
        """Create a new lab request."""
        cleaned = clean_input_data(data)
        record_data = {
            "visit_id": cleaned['visit_id'],
            "patient_id": cleaned['patient_id'],
            "lab_technician_id": cleaned.get('lab_technician_id'),
            "priority": cleaned.get('priority') or 'NORMAL',
            "sample_type": cleaned.get('sample_type'),
            "remarks": cleaned.get('remarks'),
            "requested_by": requested_by,
            "test_status": "PENDING"
        }

        def action(ctx) -> LaboratoryResponse:
            req = CreateRecordRequest(context=ctx, module_id="laboratory", data=record_data)
            resp = crud_provider.records.create_record(req)
            return LaboratoryService.map_to_laboratory(resp.data)
        return run_in_context(action)

    @staticmethod
    def update_lab_request(lab_id: str, data: Dict[str, Any]) -> Optional[LaboratoryResponse]:
        """Update an existing lab request."""
        cleaned = clean_input_data(data)
        
        def action(ctx) -> LaboratoryResponse:
            req_get = GetRecordRequest(context=ctx, module_id="laboratory", record_id=lab_id)
            resp_get = crud_provider.records.get_record(req_get)
            current_data = resp_get.data.data
            
            editable_fields = (
                "test_status",
                "priority",
                "lab_technician_id",
                "sample_type",
                "remarks",
                "sample_collected_at",
            )
            for field in editable_fields:
                if field in cleaned:
                    current_data[field] = str(cleaned[field]) if cleaned[field] is not None else None
            
            if current_data.get("test_status") == "COMPLETED" and not current_data.get("completed_at"):
                current_data["completed_at"] = datetime.utcnow().isoformat()

            req_up = UpdateRecordRequest(context=ctx, record_id=lab_id, module_id="laboratory", data=current_data)
            resp_up = crud_provider.records.update_record(req_up)
            return LaboratoryService.map_to_laboratory(resp_up.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def generate_report_number() -> str:
        """Generate a new lab report number."""
        return f"REP-{random.randint(100000, 999999)}"

    @staticmethod
    def add_report(lab_id: str, data: Dict[str, Any]) -> Optional[LabReportResponse]:
        """Add a report to a lab request."""
        cleaned = clean_input_data(data)
        report_number = LaboratoryService.generate_report_number()
        
        def action(ctx) -> LabReportResponse:
            # Fetch lab request details
            req_lab = GetRecordRequest(context=ctx, module_id="laboratory", record_id=lab_id)
            resp_lab = crud_provider.records.get_record(req_lab)
            lab_rec = resp_lab.data
            
            record_data = {
                "lab_id": lab_id,
                "test_id": cleaned['test_id'],
                "patient_id": lab_rec.data.get("patient_id"),
                "doctor_id": lab_rec.data.get("requested_by"),
                "verified_by": cleaned.get("verified_by"),
                "report_number": report_number,
                "result": cleaned['result'],
                "unit": cleaned.get('unit'),
                "reference_range": cleaned.get('reference_range'),
                "is_abnormal": "True" if cleaned.get('is_abnormal') else "False",
                "remarks": cleaned.get('remarks'),
                "verified_at": datetime.utcnow().isoformat()
            }
            req_rep = CreateRecordRequest(context=ctx, module_id="lab_report", data=record_data)
            resp_rep = crud_provider.records.create_record(req_rep)
            return LaboratoryService.map_to_report(resp_rep.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def get_lab_reports(lab_id: str) -> List[LabReportResponse]:
        """Get all reports for a lab request."""
        def action(ctx) -> List[LabReportResponse]:
            resp = query_records(ctx, "lab_report", {"lab_id": lab_id}, page=1, page_size=100)
            # Prevent circular dependency recursion during resolution
            # We map to report, but set nested resolves to None to prevent infinite loop
            reports = []
            for r in resp.items:
                test_id = r.data.get("test_id")
                patient_id = r.data.get("patient_id")
                doctor_id = r.data.get("doctor_id")
                
                test = LaboratoryService.get_catalog_test_by_id(test_id) if test_id else None
                
                reports.append(LabReportResponse(
                    lab_report_id=r.id,
                    lab_id=lab_id,
                    test_id=test_id or "",
                    patient_id=patient_id or "",
                    doctor_id=doctor_id or "",
                    report_number=r.data.get("report_number", ""),
                    result=r.data.get("result", ""),
                    unit=r.data.get("unit"),
                    reference_range=r.data.get("reference_range"),
                    is_abnormal=r.data.get("is_abnormal") == "True",
                    remarks=r.data.get("remarks"),
                    created_at=datetime.utcnow(),
                    test=test
                ))
            return reports
        return run_in_context(action)

    @staticmethod
    def get_all_catalog_tests(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> EAVPagination:
        """Get paginated list of catalog tests."""
        def action(ctx) -> EAVPagination:
            if search:
                req = ListRecordsRequest(context=ctx, module_id="lab_test_catalog", page=1, page_size=1000)
                resp = crud_provider.records.list_records(req)
                all_items = [LaboratoryService.map_to_catalog(r) for r in resp.items]
                s = search.lower().strip()
                filtered = [
                    t for t in all_items
                    if s in t.test_name.lower() or s in t.test_code.lower()
                ]
                total = len(filtered)
                start = (page - 1) * per_page
                end = start + per_page
                items = filtered[start:end]
                return EAVPagination(items, page, per_page, total)
            else:
                req = ListRecordsRequest(context=ctx, module_id="lab_test_catalog", page=page, page_size=per_page)
                resp = crud_provider.records.list_records(req)
                items = [LaboratoryService.map_to_catalog(r) for r in resp.items]
                return EAVPagination(items, page, per_page, resp.total)
        return run_in_context(action)

    @staticmethod
    def get_catalog_test_by_id(test_id: str) -> Optional[LabTestCatalogResponse]:
        """Get a catalog test by ID."""
        def action(ctx) -> LabTestCatalogResponse:
            req = GetRecordRequest(context=ctx, module_id="lab_test_catalog", record_id=test_id)
            resp = crud_provider.records.get_record(req)
            return LaboratoryService.map_to_catalog(resp.data)
        try:
            return run_in_context(action)
        except Exception:
            return None

    @staticmethod
    def create_catalog_test(data: Dict[str, Any]) -> LabTestCatalogResponse:
        """Create a new catalog test."""
        cleaned = clean_input_data(data)
        record_data = {
            "test_code": cleaned['test_code'],
            "test_name": cleaned['test_name'],
            "category": cleaned.get('category'),
            "sample_type": cleaned.get('sample_type'),
            "unit": cleaned.get('unit'),
            "reference_range": cleaned.get('reference_range'),
            "normal_min": str(cleaned['normal_min']) if cleaned.get('normal_min') else None,
            "normal_max": str(cleaned['normal_max']) if cleaned.get('normal_max') else None,
            "default_price": str(cleaned['default_price']) if cleaned.get('default_price') else None,
            "description": cleaned.get('description'),
            "is_active": "True"
        }

        def action(ctx) -> LabTestCatalogResponse:
            req = CreateRecordRequest(context=ctx, module_id="lab_test_catalog", data=record_data)
            resp = crud_provider.records.create_record(req)
            return LaboratoryService.map_to_catalog(resp.data)
        return run_in_context(action)

    @staticmethod
    def update_catalog_test(
        test_id: str, data: Dict[str, Any]
    ) -> Optional[LabTestCatalogResponse]:
        """Update an existing catalog test."""
        cleaned = clean_input_data(data)
        
        def action(ctx) -> LabTestCatalogResponse:
            req_get = GetRecordRequest(context=ctx, module_id="lab_test_catalog", record_id=test_id)
            resp_get = crud_provider.records.get_record(req_get)
            current_data = resp_get.data.data
            
            editable_fields = (
                "test_code",
                "test_name",
                "category",
                "sample_type",
                "unit",
                "reference_range",
                "normal_min",
                "normal_max",
                "default_price",
                "description",
            )
            for field in editable_fields:
                if field in cleaned:
                    current_data[field] = str(cleaned[field]) if cleaned[field] is not None else None
            
            if "is_active" in cleaned:
                current_data["is_active"] = "True" if cleaned["is_active"] else "False"

            req_up = UpdateRecordRequest(context=ctx, record_id=test_id, module_id="lab_test_catalog", data=current_data)
            resp_up = crud_provider.records.update_record(req_up)
            return LaboratoryService.map_to_catalog(resp_up.data)
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

    @staticmethod
    def get_all_technicians() -> List[UserResponse]:
        """Get all active technicians."""
        def action(ctx) -> List[UserResponse]:
            resp = query_records(ctx, "user", {"role": "LAB_TECHNICIAN"}, page=1, page_size=1000)
            from app.services.staff_service import StaffService
            return [StaffService.map_to_staff(r) for r in resp.items]
        return run_in_context(action)

    @staticmethod
    def get_active_catalog_tests() -> List[LabTestCatalogResponse]:
        """Get all active catalog tests."""
        def action(ctx) -> List[LabTestCatalogResponse]:
            resp = query_records(ctx, "lab_test_catalog", {"is_active": "True"}, page=1, page_size=1000)
            return [LaboratoryService.map_to_catalog(r) for r in resp.items]
        return run_in_context(action)
