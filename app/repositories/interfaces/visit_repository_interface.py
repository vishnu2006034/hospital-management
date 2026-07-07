from abc import ABC, abstractmethod
from typing import List, Optional, Any, Dict
from flask_sqlalchemy.pagination import Pagination
from app.dtos.visit import VisitResponse, VisitCreateRequest

class IVisitRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_value: int) -> Optional[VisitResponse]:
        pass

    @abstractmethod
    def add(self, entity_dto: VisitCreateRequest) -> VisitResponse:
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
    def get_visit_details(self, visit_id: int) -> Dict[str, List[Any]]:
        pass

    @abstractmethod
    def get_recent_visits(self, limit: int = 50) -> List[VisitResponse]:
        pass

    @abstractmethod
    def get_today_appointments_count(self) -> int:
        pass

    @abstractmethod
    def get_active_admissions_count(self) -> int:
        pass
