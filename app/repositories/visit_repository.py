"""Visit repository for database operations."""

from typing import List, Optional

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.visit import Visit
from app.models.patient import Patient
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.base_repository import BaseRepository


class VisitRepository(BaseRepository[Visit]):
    """Repository for Visit entity database operations."""

    def __init__(self) -> None:
        super().__init__(Visit)

    def search(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> "Pagination[Visit]":
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
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_visit_details(self, visit: Visit) -> dict:
        """Get all related entities for a visit."""
        return {
            'prescriptions': visit.prescriptions.all(),
            'lab_requests': visit.lab_requests.all(),
            'doctor_reports': visit.doctor_reports.all(),
        }

    def get_recent_visits(self, limit: int = 50) -> List[Visit]:
        """Get recent visits."""
        return Visit.query.order_by(Visit.visit_date.desc()).limit(limit).all()


visit_repository: VisitRepository = VisitRepository()

