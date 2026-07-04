"""Report service for business logic."""

from typing import Dict, List, Optional, Any

from app.models.doctor_report import DoctorReport
from app.repositories.report_repository import report_repository


class ReportService:
    """Service layer for DoctorReport business operations."""

    @staticmethod
    def get_all_reports(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ):
        """Get paginated list of doctor reports.

        Args:
            page: Page number.
            per_page: Items per page.
            search: Optional search term.

        Returns:
            Paginated report results.
        """
        return report_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_report_by_id(report_id: int) -> DoctorReport:
        """Get a doctor report by ID.

        Args:
            report_id: The report's ID.

        Returns:
            The doctor report entity.

        Raises:
            404: If report not found.
        """
        return report_repository.get_by_id(report_id)

    @staticmethod
    def generate_report_number() -> str:
        """Generate a new doctor report number.

        Returns:
            A unique report number.
        """
        return report_repository.generate_report_number()

    @staticmethod
    def create_report(data: Dict[str, Any], doctor_id: int) -> DoctorReport:
        """Create a new doctor report.

        Args:
            data: Report data dictionary.
            doctor_id: ID of the doctor creating the report.

        Returns:
            The created doctor report entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        report_number: str = report_repository.generate_report_number()
        report: DoctorReport = DoctorReport(
            visit_id=cleaned['visit_id'],
            patient_id=cleaned['patient_id'],
            doctor_id=doctor_id,
            report_number=report_number,
            chief_complaint=cleaned.get('chief_complaint'),
            clinical_findings=cleaned.get('clinical_findings'),
            diagnosis=cleaned.get('diagnosis'),
            treatment_plan=cleaned.get('treatment_plan'),
            prescribed_medicines=cleaned.get('prescribed_medicines'),
            doctor_notes=cleaned.get('doctor_notes'),
            follow_up_required=bool(cleaned.get('follow_up_required')),
            follow_up_date=cleaned.get('follow_up_date'),
            next_visit_reason=cleaned.get('next_visit_reason'),
        )
        report_repository.add(report)
        report_repository.commit()
        return report

    @staticmethod
    def update_report(
        report: DoctorReport, data: Dict[str, Any]
    ) -> DoctorReport:
        """Update an existing doctor report.

        Args:
            report: The doctor report entity to update.
            data: Updated report data.

        Returns:
            The updated doctor report entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        report.chief_complaint = cleaned.get('chief_complaint')
        report.clinical_findings = cleaned.get('clinical_findings')
        report.diagnosis = cleaned.get('diagnosis')
        report.treatment_plan = cleaned.get('treatment_plan')
        report.prescribed_medicines = cleaned.get('prescribed_medicines')
        report.doctor_notes = cleaned.get('doctor_notes')
        report.follow_up_required = bool(cleaned.get('follow_up_required'))
        report.follow_up_date = cleaned.get('follow_up_date')
        report.next_visit_reason = cleaned.get('next_visit_reason')
        report_repository.commit()
        return report

    @staticmethod
    def get_recent_visits(limit: int = 50) -> List:
        """Get recent visits.

        Args:
            limit: Maximum number of visits.

        Returns:
            List of recent visits.
        """
        return report_repository.get_recent_visits(limit)

    @staticmethod
    def get_all_patients() -> List:
        """Get all patients.

        Returns:
            List of all patients.
        """
        return report_repository.get_all_patients()
