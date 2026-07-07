from abc import ABC, abstractmethod
from typing import List, Optional
from flask_sqlalchemy.pagination import Pagination
from app.dtos.patient import PatientResponse
from app.dtos.visit import VisitResponse

class IPatientService(ABC):
    @abstractmethod
    def get_all_patients(
        self, page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        pass

    @abstractmethod
    def get_patient_by_id(self, patient_id: int) -> PatientResponse:
        pass

    @abstractmethod
    def generate_patient_number(self) -> str:
        pass

    @abstractmethod
    def create_patient(self, data: dict) -> PatientResponse:
        pass

    @abstractmethod
    def update_patient(self, patient_id: int, data: dict) -> PatientResponse:
        pass

    @abstractmethod
    def delete_patient(self, patient_id: int) -> None:
        pass

    @abstractmethod
    def get_patient_visits(self, patient_id: int, limit: int = 20) -> List[VisitResponse]:
        pass

    @abstractmethod
    def get_total_patients_count(self) -> int:
        pass
