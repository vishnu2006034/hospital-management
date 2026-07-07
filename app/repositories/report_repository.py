"""Report repository for database operations."""

from typing import List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.doctor_report import DoctorReport
from app.models.patient import Patient
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.report_repository_interface import IReportRepository
from app.mappers.report_mapper import ReportMapper
from app.dtos.report import ReportResponse, ReportCreateRequest
from app.utils import generate_sequential_code


class ReportRepository(BaseRepository[DoctorReport], IReportRepository):
    """Repository for DoctorReport entity database operations."""

    def __init__(self) -> None:
        super().__init__(DoctorReport)

    def get_by_id(self, id_value: int) -> Optional[ReportResponse]:
        model = db.session.get(DoctorReport, id_value)
        return ReportMapper.to_dto(model) if model else None

    def add(self, entity_dto: ReportCreateRequest) -> ReportResponse:
        model = ReportMapper.to_model(entity_dto)
        db.session.add(model)
        db.session.flush()
        return ReportMapper.to_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(DoctorReport, entity_id)
        if model:
            db.session.delete(model)

    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ) -> Pagination:
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
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        pagination.items = [ReportMapper.to_dto(r) for r in pagination.items]
        return pagination

    def generate_report_number(self) -> str:
        """Generate the next doctor report number."""
        return generate_sequential_code(DoctorReport, 'doctor_report_id', 'DR')


report_repository: ReportRepository = ReportRepository()
