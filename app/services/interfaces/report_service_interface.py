from abc import ABC, abstractmethod
from typing import List, Optional
from flask_sqlalchemy.pagination import Pagination
from app.dtos.report import ReportResponse
from app.dtos.visit import VisitResponse
from app.dtos.patient import PatientResponse

class IReportService(ABC):
    @abstractmethod
    def get_all_reports(
        self, page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        pass

    @abstractmethod
    def get_report_by_id(self, report_id: int) -> ReportResponse:
        pass

    @abstractmethod
    def generate_report_number(self) -> str:
        pass

    @abstractmethod
    def create_report(self, data: dict, doctor_id: int) -> ReportResponse:
        pass

    @abstractmethod
    def update_report(self, report_id: int, data: dict) -> ReportResponse:
        pass

    @abstractmethod
    def get_recent_visits(self, limit: int = 50) -> List[VisitResponse]:
        pass

    @abstractmethod
    def get_all_patients(self) -> List[PatientResponse]:
        pass
