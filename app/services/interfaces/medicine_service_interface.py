from abc import ABC, abstractmethod
from typing import Optional
from flask_sqlalchemy.pagination import Pagination
from app.dtos.medicine import MedicineResponse

class IMedicineService(ABC):
    @abstractmethod
    def get_all_medicines(
        self, page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        pass

    @abstractmethod
    def get_medicine_by_id(self, medicine_id: int) -> MedicineResponse:
        pass

    @abstractmethod
    def create_medicine(self, data: dict) -> MedicineResponse:
        pass

    @abstractmethod
    def update_medicine(self, medicine_id: int, data: dict) -> MedicineResponse:
        pass

    @abstractmethod
    def delete_medicine(self, medicine_id: int) -> None:
        pass
