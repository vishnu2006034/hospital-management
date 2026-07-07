from abc import ABC, abstractmethod
from typing import List, Optional, Any
from flask_sqlalchemy.pagination import Pagination
from app.dtos.prescription import PrescriptionResponse, PrescriptionCreateRequest
from app.dtos.inventory import InventoryResponse

class IPrescriptionRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_value: int) -> Optional[PrescriptionResponse]:
        pass

    @abstractmethod
    def add(self, entity_dto: PrescriptionCreateRequest) -> PrescriptionResponse:
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
    def get_available_inventory(self) -> List[InventoryResponse]:
        pass

    @abstractmethod
    def deduct_stock(self, inventory_id: int, quantity: int) -> None:
        pass
