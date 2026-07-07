"""Report service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.doctor_report import DoctorReport
from app.repositories.report_repository import ReportRepository
from app.repositories.visit_repository import VisitRepository
from app.repositories.patient_repository import PatientRepository
from app.services.interfaces.report_service_interface import IReportService
from app.dtos.report import ReportResponse, ReportCreateRequest, ReportUpdateRequest
from app.dtos.visit import VisitResponse
from app.dtos.patient import PatientResponse
from app.mappers.report_mapper import ReportMapper
from app.utils import clean_input_data


class ReportService(IReportService):
    """Service layer for DoctorReport business operations."""
    _report_repository: ReportRepository = ReportRepository()
    _visit_repository: VisitRepository = VisitRepository()
    _patient_repository: PatientRepository = PatientRepository()

    @staticmethod
    def get_all_reports(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        """Get paginated list of doctor reports."""
        return ReportService._report_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_report_by_id(report_id: int) -> ReportResponse:
        """Get a doctor report by ID."""
        return ReportService._report_repository.get_by_id(report_id)

    @staticmethod
    def generate_report_number() -> str:
        """Generate a new doctor report number."""
        return ReportService._report_repository.generate_report_number()

    @staticmethod
    def create_report(data: Dict[str, Any], doctor_id: int) -> ReportResponse:
        """Create a new doctor report."""
        cleaned = clean_input_data(data)

        dto = ReportCreateRequest(
            visit_id=int(cleaned['visit_id']),
            patient_id=int(cleaned['patient_id']),
            chief_complaint=cleaned.get('chief_complaint'),
            clinical_findings=cleaned.get('clinical_findings'),
            diagnosis=cleaned.get('diagnosis'),
            treatment_plan=cleaned.get('treatment_plan'),
            prescribed_medicines=cleaned.get('prescribed_medicines'),
            doctor_notes=cleaned.get('doctor_notes'),
            follow_up_required=bool(cleaned.get('follow_up_required')),
            follow_up_date=cleaned.get('follow_up_date'),
            next_visit_reason=cleaned.get('next_visit_reason')
        )

        report_dto = ReportService._report_repository.add(dto)

        # Retrieve model to set doctor_id and generate report number
        report_model = db.session.get(DoctorReport, report_dto.doctor_report_id)
        if report_model:
            report_model.doctor_id = doctor_id
            report_model.report_number = ReportService._report_repository.generate_report_number()

        ReportService._report_repository.commit()
        return ReportService._report_repository.get_by_id(report_dto.doctor_report_id)

    @staticmethod
    def update_report(
        report_id: int, data: Dict[str, Any]
    ) -> ReportResponse:
        """Update an existing doctor report."""
        cleaned = clean_input_data(data)
        report_model = db.session.get(DoctorReport, report_id)
        if not report_model:
            return None

        dto = ReportUpdateRequest(
            chief_complaint=cleaned.get('chief_complaint'),
            clinical_findings=cleaned.get('clinical_findings'),
            diagnosis=cleaned.get('diagnosis'),
            treatment_plan=cleaned.get('treatment_plan'),
            prescribed_medicines=cleaned.get('prescribed_medicines'),
            doctor_notes=cleaned.get('doctor_notes'),
            follow_up_required=bool(cleaned.get('follow_up_required')),
            follow_up_date=cleaned.get('follow_up_date'),
            next_visit_reason=cleaned.get('next_visit_reason')
        )

        ReportMapper.update_model(report_model, dto)
        ReportService._report_repository.commit()
        return ReportMapper.to_dto(report_model)

    @staticmethod
    def get_recent_visits(limit: int = 50) -> List[VisitResponse]:
        """Get recent visits."""
        return ReportService._visit_repository.get_recent_visits(limit)

    @staticmethod
    def get_all_patients() -> List[PatientResponse]:
        return ReportService._patient_repository.get_all_patients()
