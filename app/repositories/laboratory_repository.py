"""Laboratory repositories for database operations."""

from datetime import datetime
from typing import List, Optional

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.laboratory import Laboratory
from app.models.lab_report import LabReport
from app.models.lab_test_catalog import LabTestCatalog
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.user import User
from app.repositories.base_repository import BaseRepository
from app.utils import generate_sequential_code


class LaboratoryRepository(BaseRepository[Laboratory]):
    """Repository for Laboratory entity database operations."""

    def __init__(self) -> None:
        super().__init__(Laboratory)

    def search(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> Pagination:
        """Search lab requests with optional status filter and pagination."""
        query = Laboratory.query.join(Patient)
        if status:
            query = query.filter(Laboratory.test_status == status)
        if search:
            query = query.filter(
                db.or_(
                    Patient.first_name.ilike(f'%{search}%'),
                    Patient.last_name.ilike(f'%{search}%'),
                    Patient.patient_number.ilike(f'%{search}%'),
                )
            )
        query = query.order_by(Laboratory.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_lab_reports(self, lab: Laboratory) -> List[LabReport]:
        """Get all reports for a lab request."""
        return lab.reports.all()



    def generate_report_number(self) -> str:
        """Generate the next lab report number."""
        return generate_sequential_code(LabReport, 'lab_report_id', 'LR')

    def update_completion_time(self, lab: Laboratory) -> None:
        """Set completion time if test is marked completed."""
        if lab.test_status == 'COMPLETED' and not lab.completed_at:
            lab.completed_at = datetime.utcnow()


class LabReportRepository(BaseRepository[LabReport]):
    """Repository for LabReport entity database operations."""

    def __init__(self) -> None:
        super().__init__(LabReport)


class LabTestCatalogRepository(BaseRepository[LabTestCatalog]):
    """Repository for LabTestCatalog entity database operations."""

    def __init__(self) -> None:
        super().__init__(LabTestCatalog)

    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ) -> Pagination:
        """Search lab test catalog with pagination."""
        query = LabTestCatalog.query
        if search:
            query = query.filter(
                db.or_(
                    LabTestCatalog.test_name.ilike(f'%{search}%'),
                    LabTestCatalog.test_code.ilike(f'%{search}%'),
                    LabTestCatalog.category.ilike(f'%{search}%'),
                )
            )
        query = query.order_by(LabTestCatalog.test_name)
        return query.paginate(page=page, per_page=per_page, error_out=False)


laboratory_repository: LaboratoryRepository = LaboratoryRepository()
lab_report_repository: LabReportRepository = LabReportRepository()
lab_test_catalog_repository: LabTestCatalogRepository = LabTestCatalogRepository()


