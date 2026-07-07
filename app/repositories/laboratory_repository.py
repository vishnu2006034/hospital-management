"""Laboratory repositories for database operations."""

from datetime import datetime
from typing import List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.laboratory import Laboratory
from app.models.lab_report import LabReport
from app.models.lab_test_catalog import LabTestCatalog
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.laboratory_repository_interface import (
    ILaboratoryRepository,
    ILabReportRepository,
    ILabTestCatalogRepository
)
from app.mappers.laboratory_mapper import LaboratoryMapper
from app.dtos.laboratory import (
    LaboratoryResponse,
    LaboratoryCreateRequest,
    LaboratoryUpdateRequest,
    LabReportResponse,
    LabReportCreateRequest,
    LabTestCatalogResponse,
    LabTestCatalogCreateRequest,
    LabTestCatalogUpdateRequest,
)
from app.utils import generate_sequential_code


class LaboratoryRepository(BaseRepository[Laboratory], ILaboratoryRepository):
    """Repository for Laboratory entity database operations."""

    def __init__(self) -> None:
        super().__init__(Laboratory)

    def get_by_id(self, id_value: int) -> Optional[LaboratoryResponse]:
        model = db.session.get(Laboratory, id_value)
        return LaboratoryMapper.to_dto(model) if model else None

    def add(self, entity_dto: LaboratoryCreateRequest) -> LaboratoryResponse:
        model = LaboratoryMapper.to_model(entity_dto)
        db.session.add(model)
        db.session.flush()
        return LaboratoryMapper.to_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(Laboratory, entity_id)
        if model:
            db.session.delete(model)

    def search(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> Pagination:
        """Search lab requests with optional status filter and pagination."""
        from app.models.patient import Patient  # Local import to avoid circular dependencies
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
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        pagination.items = [LaboratoryMapper.to_dto(lab) for lab in pagination.items]
        return pagination

    def get_lab_reports(self, lab_id: int) -> List[LabReportResponse]:
        """Get all reports for a lab request."""
        lab = db.session.get(Laboratory, lab_id)
        if lab:
            return [LaboratoryMapper.to_report_dto(r) for r in lab.reports.all()]
        return []

    def generate_report_number(self) -> str:
        """Generate the next lab report number."""
        return generate_sequential_code(LabReport, 'lab_report_id', 'LR')

    def update_completion_time(self, lab_id: int) -> None:
        """Set completion time if test is marked completed."""
        lab = db.session.get(Laboratory, lab_id)
        if lab and lab.test_status == 'COMPLETED' and not lab.completed_at:
            lab.completed_at = datetime.utcnow()


class LabReportRepository(BaseRepository[LabReport], ILabReportRepository):
    """Repository for LabReport entity database operations."""

    def __init__(self) -> None:
        super().__init__(LabReport)

    def get_by_id(self, id_value: int) -> Optional[LabReportResponse]:
        model = db.session.get(LabReport, id_value)
        return LaboratoryMapper.to_report_dto(model) if model else None

    def add(self, entity_dto: LabReportCreateRequest) -> LabReportResponse:
        model = LaboratoryMapper.to_report_model(entity_dto)
        db.session.add(model)
        db.session.flush()
        return LaboratoryMapper.to_report_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(LabReport, entity_id)
        if model:
            db.session.delete(model)


class LabTestCatalogRepository(BaseRepository[LabTestCatalog], ILabTestCatalogRepository):
    """Repository for LabTestCatalog entity database operations."""

    def __init__(self) -> None:
        super().__init__(LabTestCatalog)

    def get_by_id(self, id_value: int) -> Optional[LabTestCatalogResponse]:
        model = db.session.get(LabTestCatalog, id_value)
        return LaboratoryMapper.to_catalog_dto(model) if model else None

    def add(self, entity_dto: LabTestCatalogCreateRequest) -> LabTestCatalogResponse:
        model = LaboratoryMapper.to_catalog_model(entity_dto)
        db.session.add(model)
        db.session.flush()
        return LaboratoryMapper.to_catalog_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(LabTestCatalog, entity_id)
        if model:
            db.session.delete(model)

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
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        pagination.items = [LaboratoryMapper.to_catalog_dto(t) for t in pagination.items]
        return pagination


laboratory_repository: LaboratoryRepository = LaboratoryRepository()
lab_report_repository: LabReportRepository = LabReportRepository()
lab_test_catalog_repository: LabTestCatalogRepository = LabTestCatalogRepository()
