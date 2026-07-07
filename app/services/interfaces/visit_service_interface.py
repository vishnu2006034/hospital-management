from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from flask_sqlalchemy.pagination import Pagination
from app.dtos.visit import VisitResponse
from app.dtos.patient import PatientResponse
from app.dtos.user import UserResponse

class IVisitService(ABC):
    @abstractmethod
    def get_all_visits(
        self,
        page: int = 1,
        per_page: int = 15,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Pagination:
        pass

    @abstractmethod
    def get_visit_by_id(self, visit_id: int) -> VisitResponse:
        pass

    @abstractmethod
    def create_visit(
        self, data: dict, admission_date: Optional[str] = None
    ) -> VisitResponse:
        pass

    @abstractmethod
    def update_visit(
        self,
        visit_id: int,
        data: dict,
        admission_date: Optional[str] = None,
        discharge_date: Optional[str] = None,
    ) -> VisitResponse:
        pass

    @abstractmethod
    def delete_visit(self, visit_id: int) -> None:
        pass

    @abstractmethod
    def get_all_patients(self) -> List[PatientResponse]:
        pass

    @abstractmethod
    def get_all_doctors(self) -> List[UserResponse]:
        pass

    @abstractmethod
    def get_visit_details(self, visit_id: int) -> Dict[str, List[Any]]:
        pass

    @abstractmethod
    def get_today_appointments_count(self) -> int:
        pass

    @abstractmethod
    def get_active_admissions_count(self) -> int:
        pass
