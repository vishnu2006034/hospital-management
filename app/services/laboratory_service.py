"""Laboratory service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.laboratory import Laboratory
from app.models.lab_report import LabReport
from app.models.lab_test_catalog import LabTestCatalog
from app.repositories.laboratory_repository import (
    LaboratoryRepository,
    LabReportRepository,
    LabTestCatalogRepository
)
from app.repositories.visit_repository import VisitRepository
from app.repositories.patient_repository import PatientRepository
from app.repositories.user_repository import UserRepository
from app.services.interfaces.laboratory_service_interface import ILaboratoryService
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
from app.dtos.visit import VisitResponse
from app.dtos.patient import PatientResponse
from app.dtos.user import UserResponse
from app.mappers.laboratory_mapper import LaboratoryMapper
from app.utils import clean_input_data


class LaboratoryService(ILaboratoryService):
    """Service layer for Laboratory business operations."""
    _laboratory_repository: LaboratoryRepository = LaboratoryRepository()
    _lab_report_repository: LabReportRepository = LabReportRepository()
    _lab_test_catalog_repository: LabTestCatalogRepository = LabTestCatalogRepository()
    _visit_repository: VisitRepository = VisitRepository()
    _patient_repository: PatientRepository = PatientRepository()
    _user_repository: UserRepository = UserRepository()

    @staticmethod
    def get_all_lab_requests(
        page: int = 1,
        per_page: int = 15,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Pagination:
        """Get paginated list of lab requests."""
        return LaboratoryService._laboratory_repository.search(
            search, status=status, page=page, per_page=per_page
        )

    @staticmethod
    def get_lab_by_id(lab_id: int) -> LaboratoryResponse:
        """Get a lab request by ID."""
        return LaboratoryService._laboratory_repository.get_by_id(lab_id)

    @staticmethod
    def create_lab_request(data: Dict[str, Any], requested_by: int) -> LaboratoryResponse:
        """Create a new lab request."""
        cleaned = clean_input_data(data)

        dto = LaboratoryCreateRequest(
            visit_id=int(cleaned['visit_id']),
            patient_id=int(cleaned['patient_id']),
            lab_technician_id=int(cleaned['lab_technician_id']) if cleaned.get('lab_technician_id') else None,
            priority=cleaned.get('priority') or 'NORMAL',
            sample_type=cleaned.get('sample_type'),
            remarks=cleaned.get('remarks'),
            requested_by=requested_by
        )

        lab_dto = LaboratoryService._laboratory_repository.add(dto)

        LaboratoryService._laboratory_repository.commit()
        return LaboratoryService._laboratory_repository.get_by_id(lab_dto.lab_id)

    @staticmethod
    def update_lab_request(lab_id: int, data: Dict[str, Any]) -> LaboratoryResponse:
        """Update an existing lab request."""
        cleaned = clean_input_data(data)
        lab_model = db.session.get(Laboratory, lab_id)
        if not lab_model:
            return None

        dto = LaboratoryUpdateRequest(
            test_status=cleaned.get('test_status') or lab_model.test_status,
            priority=cleaned.get('priority') or lab_model.priority,
            lab_technician_id=int(cleaned['lab_technician_id']) if cleaned.get('lab_technician_id') else None,
            sample_type=cleaned.get('sample_type'),
            remarks=cleaned.get('remarks')
        )
        if cleaned.get('sample_collected_at'):
            dto.sample_collected_at = cleaned['sample_collected_at']

        LaboratoryMapper.update_model(lab_model, dto)
        LaboratoryService._laboratory_repository.update_completion_time(lab_model.lab_id)
        LaboratoryService._laboratory_repository.commit()
        return LaboratoryMapper.to_dto(lab_model)

    @staticmethod
    def generate_report_number() -> str:
        """Generate a new lab report number."""
        return LaboratoryService._laboratory_repository.generate_report_number()

    @staticmethod
    def add_report(lab_id: int, data: Dict[str, Any]) -> LabReportResponse:
        """Add a report to a lab request."""
        cleaned = clean_input_data(data)
        lab_dto = LaboratoryService._laboratory_repository.get_by_id(lab_id)
        if not lab_dto:
            return None

        report_number = LaboratoryService._laboratory_repository.generate_report_number()
        
        dto = LabReportCreateRequest(
            test_id=int(cleaned['test_id']),
            result=cleaned['result'],
            unit=cleaned.get('unit'),
            reference_range=cleaned.get('reference_range'),
            is_abnormal=bool(cleaned.get('is_abnormal')),
            remarks=cleaned.get('remarks'),
            lab_id=lab_dto.lab_id,
            patient_id=lab_dto.patient_id,
            doctor_id=lab_dto.requested_by,
            report_number=report_number
        )

        report_dto = LaboratoryService._lab_report_repository.add(dto)
        LaboratoryService._lab_report_repository.commit()
        return report_dto

    @staticmethod
    def get_lab_reports(lab_id: int) -> List[LabReportResponse]:
        """Get all reports for a lab request."""
        return LaboratoryService._laboratory_repository.get_lab_reports(lab_id)

    @staticmethod
    def get_all_catalog_tests(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        """Get paginated list of catalog tests."""
        return LaboratoryService._lab_test_catalog_repository.search(
            search, page=page, per_page=per_page
        )

    @staticmethod
    def get_catalog_test_by_id(test_id: int) -> LabTestCatalogResponse:
        """Get a catalog test by ID."""
        return LaboratoryService._lab_test_catalog_repository.get_by_id(test_id)

    @staticmethod
    def create_catalog_test(data: Dict[str, Any]) -> LabTestCatalogResponse:
        """Create a new catalog test."""
        cleaned = clean_input_data(data)

        dto = LabTestCatalogCreateRequest(
            test_code=cleaned['test_code'],
            test_name=cleaned['test_name'],
            category=cleaned.get('category'),
            sample_type=cleaned.get('sample_type'),
            unit=cleaned.get('unit'),
            reference_range=cleaned.get('reference_range'),
            normal_min=cleaned.get('normal_min'),
            normal_max=cleaned.get('normal_max'),
            default_price=cleaned.get('default_price'),
            description=cleaned.get('description')
        )

        catalog_dto = LaboratoryService._lab_test_catalog_repository.add(dto)
        LaboratoryService._lab_test_catalog_repository.commit()
        return catalog_dto

    @staticmethod
    def update_catalog_test(
        test_id: int, data: Dict[str, Any]
    ) -> LabTestCatalogResponse:
        """Update an existing catalog test."""
        cleaned = clean_input_data(data)
        catalog_model = db.session.get(LabTestCatalog, test_id)
        if not catalog_model:
            return None

        dto = LabTestCatalogUpdateRequest(
            test_code=cleaned['test_code'],
            test_name=cleaned['test_name'],
            category=cleaned.get('category'),
            sample_type=cleaned.get('sample_type'),
            unit=cleaned.get('unit'),
            reference_range=cleaned.get('reference_range'),
            normal_min=cleaned.get('normal_min'),
            normal_max=cleaned.get('normal_max'),
            default_price=cleaned.get('default_price'),
            description=cleaned.get('description'),
            is_active=bool(cleaned.get('is_active'))
        )

        LaboratoryMapper.update_catalog_model(catalog_model, dto)
        LaboratoryService._lab_test_catalog_repository.commit()
        return LaboratoryMapper.to_catalog_dto(catalog_model)

    @staticmethod
    def get_recent_visits(limit: int = 50) -> List[VisitResponse]:
        """Get recent visits."""
        return LaboratoryService._visit_repository.get_recent_visits(limit)

    @staticmethod
    def get_all_patients() -> List[PatientResponse]:
        return LaboratoryService._patient_repository.get_all_patients()

    @staticmethod
    def get_all_technicians() -> List[UserResponse]:
        """Get all active technicians."""
        return LaboratoryService._user_repository.get_all_technicians()

    @staticmethod
    def get_active_catalog_tests() -> List[LabTestCatalogResponse]:
        """Get all active catalog tests."""
        models = LabTestCatalog.query.filter_by(is_active=True).order_by(LabTestCatalog.test_name).all()
        return [LaboratoryMapper.to_catalog_dto(t) for t in models]
