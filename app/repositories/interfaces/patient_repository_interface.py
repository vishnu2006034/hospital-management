from abc import ABC, abstractmethod
from typing import List, Optional, Any
from flask_sqlalchemy.pagination import Pagination
from app.dtos.patient import PatientResponse, PatientCreateRequest
from app.dtos.visit import VisitResponse

class IPatientRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_value: int) -> Optional[PatientResponse]:
        pass

    @abstractmethod
    def add(self, entity_dto: PatientCreateRequest) -> PatientResponse:
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
    def search(self, search: Optional[str], page: int = 1, per_page: int = 15) -> Pagination:
        pass

    @abstractmethod
    def get_next_patient_number(self) -> str:
        pass

    @abstractmethod
    def get_patient_visits(self, patient_id: int, limit: int = 20) -> List[VisitResponse]:
        pass

    @abstractmethod
    def get_all_patients(self) -> List[PatientResponse]:
        pass

    @abstractmethod
    def get_total_patients_count(self) -> int:
        pass
