from abc import ABC, abstractmethod
from typing import List, Optional, Any
from flask_sqlalchemy.pagination import Pagination
from app.dtos.inventory import InventoryResponse, InventoryCreateRequest, InventoryTransactionResponse
from app.dtos.medicine import MedicineResponse

class IInventoryRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_value: int) -> Optional[InventoryResponse]:
        pass

    @abstractmethod
    def add(self, entity_dto: InventoryCreateRequest) -> InventoryResponse:
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
        filter_type: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
    ) -> Pagination:
        pass

    @abstractmethod
    def get_medicines(self) -> List[MedicineResponse]:
        pass

    @abstractmethod
    def get_recent_transactions(
        self, inventory_id: int, limit: int = 20
    ) -> List[InventoryTransactionResponse]:
        pass

    @abstractmethod
    def create_transaction(
        self,
        inventory_id: int,
        transaction_type: str,
        quantity: int,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        performed_by: Optional[int] = None,
        remarks: Optional[str] = None,
    ) -> InventoryTransactionResponse:
        pass

    @abstractmethod
    def update_stock(
        self, inventory_id: int, transaction_type: str, quantity: int
    ) -> Optional[InventoryResponse]:
        pass
