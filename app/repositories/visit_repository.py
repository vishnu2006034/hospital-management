"""Visit repository for database operations."""

from typing import List, Optional, Any, Dict

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.visit import Visit
from app.models.patient import Patient
from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.visit_repository_interface import IVisitRepository
from app.mappers.visit_mapper import VisitMapper
from app.dtos.visit import VisitResponse, VisitCreateRequest
from app.mappers.prescription_mapper import PrescriptionMapper
from app.mappers.laboratory_mapper import LaboratoryMapper
from app.mappers.report_mapper import ReportMapper


class VisitRepository(BaseRepository[Visit], IVisitRepository):
    """Repository for Visit entity database operations."""

    def __init__(self) -> None:
        super().__init__(Visit)

    def get_by_id(self, id_value: int) -> Optional[VisitResponse]:
        model = db.session.get(Visit, id_value)
        return VisitMapper.to_dto(model) if model else None

    def add(self, entity_dto: VisitCreateRequest) -> VisitResponse:
        model = VisitMapper.to_model(entity_dto)
        db.session.add(model)
        db.session.flush()
        return VisitMapper.to_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(Visit, entity_id)
        if model:
            db.session.delete(model)

    def search(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> Pagination:
        """Search visits with optional status filter and pagination."""
        query = Visit.query.join(Patient).join(User, Visit.doctor_id == User.user_id)
        if status:
            query = query.filter(Visit.visit_status == status)
        if search:
            query = query.filter(
                db.or_(
                    Patient.first_name.ilike(f'%{search}%'),
                    Patient.last_name.ilike(f'%{search}%'),
                    Patient.patient_number.ilike(f'%{search}%'),
                )
            )
        query = query.order_by(Visit.visit_date.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        pagination.items = [VisitMapper.to_dto(v) for v in pagination.items]
        return pagination

    def get_visit_details(self, visit_id: int) -> Dict[str, List[Any]]:
        """Get all related entities for a visit."""
        visit = db.session.get(Visit, visit_id)
        if visit:
            return {
                'prescriptions': [PrescriptionMapper.to_dto(p) for p in visit.prescriptions.all()],
                'lab_requests': [LaboratoryMapper.to_dto(l) for l in visit.lab_requests.all()],
                'doctor_reports': [ReportMapper.to_dto(r) for r in visit.doctor_reports.all()],
            }
        return {'prescriptions': [], 'lab_requests': [], 'doctor_reports': []}

    def get_recent_visits(self, limit: int = 50) -> List[VisitResponse]:
        """Get recent visits."""
        models = Visit.query.order_by(Visit.visit_date.desc()).limit(limit).all()
        return [VisitMapper.to_dto(v) for v in models]

    def get_today_appointments_count(self) -> int:
        """Count today's visits/appointments."""
        from datetime import date
        today = date.today()
        return Visit.query.filter(db.func.date(Visit.visit_date) == today).count()

    def get_active_admissions_count(self) -> int:
        """Count open inpatient admissions."""
        return Visit.query.filter_by(
            visit_type='INPATIENT',
            visit_status='OPEN',
        ).count()


visit_repository: VisitRepository = VisitRepository()
