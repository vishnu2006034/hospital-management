"""Laboratory repositories for database operations."""

from datetime import datetime
from typing import List, Optional

from app import db
from app.models.laboratory import Laboratory
from app.models.lab_report import LabReport
from app.models.lab_test_catalog import LabTestCatalog
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.user import User
from app.repositories.base_repository import BaseRepository


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
    ):
        """Search lab requests with optional status filter and pagination.

        Args:
            search: Search term for patient name or number.
            status: Filter by test status.
            page: Page number.
            per_page: Items per page.

        Returns:
            Paginated lab request results.
        """
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
        """Get all reports for a lab request.

        Args:
            lab: The laboratory entity.

        Returns:
            List of lab reports.
        """
        return lab.reports.all()

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

    def get_all_technicians(self) -> List[User]:
        """Get all active lab technicians.

        Returns:
            List of active users.
        """
        return User.query.filter_by(status='ACTIVE').order_by(User.first_name).all()

    def generate_report_number(self) -> str:
        """Generate the next lab report number.

        Returns:
            A new report number in format LR000001.
        """
        last: Optional[LabReport] = LabReport.query.order_by(
            LabReport.lab_report_id.desc()
        ).first()
        next_num: int = (last.lab_report_id + 1) if last else 1
        return f'LR{next_num}'

    def update_completion_time(self, lab: Laboratory) -> None:
        """Set completion time if test is marked completed.

        Args:
            lab: The laboratory entity to update.
        """
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
    ):
        """Search lab test catalog with pagination.

        Args:
            search: Search term for test name, code, or category.
            page: Page number.
            per_page: Items per page.

        Returns:
            Paginated catalog results.
        """
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

    def get_active_tests(self) -> List[LabTestCatalog]:
        """Get all active tests in the catalog.

        Returns:
            List of active lab tests.
        """
        return LabTestCatalog.query.filter_by(is_active=True).order_by(
            LabTestCatalog.test_name
        ).all()


laboratory_repository: LaboratoryRepository = LaboratoryRepository()
lab_report_repository: LabReportRepository = LabReportRepository()
lab_test_catalog_repository: LabTestCatalogRepository = LabTestCatalogRepository()

