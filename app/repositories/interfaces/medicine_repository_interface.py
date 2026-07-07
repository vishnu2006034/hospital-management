from abc import ABC, abstractmethod
from typing import Optional, Any
from flask_sqlalchemy.pagination import Pagination
from app.dtos.medicine import MedicineResponse, MedicineCreateRequest

class IMedicineRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_value: int) -> Optional[MedicineResponse]:
        pass

    @abstractmethod
    def add(self, entity_dto: MedicineCreateRequest) -> MedicineResponse:
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
