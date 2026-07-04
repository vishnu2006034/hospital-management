"""Report repository for database operations."""

from typing import List, Optional

from app import db
from app.models.doctor_report import DoctorReport
from app.models.visit import Visit
from app.models.patient import Patient
from app.repositories.base_repository import BaseRepository


class ReportRepository(BaseRepository[DoctorReport]):
    """Repository for DoctorReport entity database operations."""

    def __init__(self) -> None:
        super().__init__(DoctorReport)

    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ):
        """Search doctor reports with pagination.

        Args:
            search: Search term for patient name, report number, or diagnosis.
            page: Page number.
            per_page: Items per page.

        Returns:
            Paginated report results.
        """
        query = DoctorReport.query.join(Patient)
        if search:
            query = query.filter(
                db.or_(
                    Patient.first_name.ilike(f'%{search}%'),
                    Patient.last_name.ilike(f'%{search}%'),
                    DoctorReport.report_number.ilike(f'%{search}%'),
                    DoctorReport.diagnosis.ilike(f'%{search}%'),
                )
            )
        query = query.order_by(DoctorReport.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def generate_report_number(self) -> str:
        """Generate the next doctor report number.

        Returns:
            A new report number in format DR000001.
        """
        last: Optional[DoctorReport] = DoctorReport.query.order_by(
            DoctorReport.doctor_report_id.desc()
        ).first()
        next_num: int = (last.doctor_report_id + 1) if last else 1
        return f'DR{next_num}'

    def get_recent_visits(self, limit: int = 50) -> List[Visit]:
        """Get recent visits.

        Args:
            limit: Maximum number of visits.

        Returns:
            List of recent visits.
        """
        return Visit.query.order_by(Visit.visit_date.desc()).limit(limit).all()

    def get_all_patients(self) -> List[Patient]:
        """Get all patients ordered by first name.

        Returns:
            List of all patients.
        """
        return Patient.query.order_by(Patient.first_name).all()


report_repository: ReportRepository = ReportRepository()

