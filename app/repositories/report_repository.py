"""Report repository for database operations."""

from typing import List, Optional

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.doctor_report import DoctorReport
from app.models.visit import Visit
from app.models.patient import Patient
from app.repositories.base_repository import BaseRepository
from app.utils import generate_sequential_code


class ReportRepository(BaseRepository[DoctorReport]):
    """Repository for DoctorReport entity database operations."""

    def __init__(self) -> None:
        super().__init__(DoctorReport)

    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ) -> "Pagination[DoctorReport]":
        """Search doctor reports with pagination."""
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
        """Generate the next doctor report number."""
        return generate_sequential_code(DoctorReport, 'doctor_report_id', 'DR')




report_repository: ReportRepository = ReportRepository()

