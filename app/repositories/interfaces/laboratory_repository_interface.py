from abc import ABC, abstractmethod
from typing import List, Optional, Any
from flask_sqlalchemy.pagination import Pagination
from app.dtos.laboratory import (
    LaboratoryResponse,
    LaboratoryCreateRequest,
    LabReportResponse,
    LabReportCreateRequest,
    LabTestCatalogResponse,
    LabTestCatalogCreateRequest,
)

class ILaboratoryRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_value: int) -> Optional[LaboratoryResponse]:
        pass

    @abstractmethod
    def add(self, entity_dto: LaboratoryCreateRequest) -> LaboratoryResponse:
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def exists(self, **kwargs: Any) -> bool:
        pass

    @abstractmethod
    def search(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> Pagination:
        pass

    @abstractmethod
    def get_lab_reports(self, lab_id: int) -> List[LabReportResponse]:
        pass

    @abstractmethod
    def generate_report_number(self) -> str:
        pass

    @abstractmethod
    def update_completion_time(self, lab_id: int) -> None:
        pass


class ILabReportRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_value: int) -> Optional[LabReportResponse]:
        pass

    @abstractmethod
    def add(self, entity_dto: LabReportCreateRequest) -> LabReportResponse:
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def exists(self, **kwargs: Any) -> bool:
        pass


class ILabTestCatalogRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_value: int) -> Optional[LabTestCatalogResponse]:
        pass

    @abstractmethod
    def add(self, entity_dto: LabTestCatalogCreateRequest) -> LabTestCatalogResponse:
        pass

    @abstractmethod
    def delete(self, entity_id: int) -> None:
        pass

    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def exists(self, **kwargs: Any) -> bool:
        pass

    @abstractmethod
    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ) -> Pagination:
        pass
