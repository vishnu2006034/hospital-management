"""Report service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app.models.doctor_report import DoctorReport
from app.models.visit import Visit
from app.models.patient import Patient
from app.repositories.report_repository import ReportRepository
from app.repositories.visit_repository import VisitRepository
from app.repositories.patient_repository import PatientRepository
from app.utils import clean_input_data


class ReportService:
    """Service layer for DoctorReport business operations."""
    _report_repository:ReportRepository=ReportRepository()
    _visit_repository:VisitRepository=VisitRepository()
    _patient_repository:PatientRepository=PatientRepository()
    @staticmethod
    def get_all_reports(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> "Pagination[DoctorReport]":
        """Get paginated list of doctor reports."""
        return ReportService._report_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_report_by_id(report_id: int) -> DoctorReport:
        """Get a doctor report by ID."""
        return ReportService._report_repository.get_by_id(report_id)

    @staticmethod
    def generate_report_number() -> str:
        """Generate a new doctor report number."""
        return ReportService._report_repository.generate_report_number()

    @staticmethod
    def create_report(data: Dict[str, Any], doctor_id: int) -> DoctorReport:
        """Create a new doctor report."""
        cleaned = clean_input_data(data)

        report_number: str = ReportService._report_repository.generate_report_number()
        report: DoctorReport = DoctorReport()
        report.visit_id=cleaned['visit_id']
        report.patient_id=cleaned['patient_id']
        report.doctor_id=doctor_id
        report.report_number=report_number
        report.chief_complaint=cleaned.get('chief_complaint')
        report.clinical_findings=cleaned.get('clinical_findings')
        report.diagnosis=cleaned.get('diagnosis')
        report.treatment_plan=cleaned.get('treatment_plan')
        report.prescribed_medicines=cleaned.get('prescribed_medicines')
        report.doctor_notes=cleaned.get('doctor_notes')
        report.follow_up_required=bool(cleaned.get('follow_up_required'))
        report.follow_up_date=cleaned.get('follow_up_date')
        report.next_visit_reason=cleaned.get('next_visit_reason')
        ReportService._report_repository.add(report)
        ReportService._report_repository.commit()
        return report

    @staticmethod
    def update_report(
        report: DoctorReport, data: Dict[str, Any]
    ) -> DoctorReport:
        """Update an existing doctor report."""
        cleaned = clean_input_data(data)

        report.chief_complaint = cleaned.get('chief_complaint')
        report.clinical_findings = cleaned.get('clinical_findings')
        report.diagnosis = cleaned.get('diagnosis')
        report.treatment_plan = cleaned.get('treatment_plan')
        report.prescribed_medicines = cleaned.get('prescribed_medicines')
        report.doctor_notes = cleaned.get('doctor_notes')
        report.follow_up_required = bool(cleaned.get('follow_up_required'))
        report.follow_up_date = cleaned.get('follow_up_date')
        report.next_visit_reason = cleaned.get('next_visit_reason')
        ReportService._report_repository.commit()
        return report

    @staticmethod
    def get_recent_visits(limit: int = 50) -> List[Visit]:
        """Get recent visits."""
        return ReportService._visit_repository.get_recent_visits(limit)

    @staticmethod
    def get_all_patients() -> List[Patient]:
        return ReportService._patient_repository.get_all_patients()
