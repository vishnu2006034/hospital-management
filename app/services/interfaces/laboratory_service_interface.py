from abc import ABC, abstractmethod
from typing import List, Optional
from flask_sqlalchemy.pagination import Pagination
from app.dtos.laboratory import (
    LaboratoryResponse,
    LabReportResponse,
    LabTestCatalogResponse,
)
from app.dtos.visit import VisitResponse
from app.dtos.patient import PatientResponse
from app.dtos.user import UserResponse

class ILaboratoryService(ABC):
    @abstractmethod
    def get_all_lab_requests(
        self,
        page: int = 1,
        per_page: int = 15,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Pagination:
        pass

    @abstractmethod
    def get_lab_by_id(self, lab_id: int) -> LaboratoryResponse:
        pass

    @abstractmethod
    def create_lab_request(self, data: dict, requested_by: int) -> LaboratoryResponse:
        pass

    @abstractmethod
    def update_lab_request(self, lab_id: int, data: dict) -> LaboratoryResponse:
        pass

    @abstractmethod
    def generate_report_number(self) -> str:
        pass

    @abstractmethod
    def add_report(self, lab_id: int, data: dict) -> LabReportResponse:
        pass

    @abstractmethod
    def get_lab_reports(self, lab_id: int) -> List[LabReportResponse]:
        pass

    @abstractmethod
    def get_all_catalog_tests(
        self, page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        pass

    @abstractmethod
    def get_catalog_test_by_id(self, test_id: int) -> LabTestCatalogResponse:
        pass

    @abstractmethod
    def create_catalog_test(self, data: dict) -> LabTestCatalogResponse:
        pass

    @abstractmethod
    def update_catalog_test(
        self, test_id: int, data: dict
    ) -> LabTestCatalogResponse:
        pass

    @abstractmethod
    def get_recent_visits(self, limit: int = 50) -> List[VisitResponse]:
        pass

    @abstractmethod
    def get_all_patients(self) -> List[PatientResponse]:
        pass

    @abstractmethod
    def get_all_technicians(self) -> List[UserResponse]:
        pass

    @abstractmethod
    def get_active_catalog_tests(self) -> List[LabTestCatalogResponse]:
        pass
