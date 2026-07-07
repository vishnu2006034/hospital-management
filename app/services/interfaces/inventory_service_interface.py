from abc import ABC, abstractmethod
from typing import List, Optional
from flask_sqlalchemy.pagination import Pagination
from app.dtos.inventory import InventoryResponse, InventoryTransactionResponse
from app.dtos.medicine import MedicineResponse

class IInventoryService(ABC):
    @abstractmethod
    def get_all_inventory(
        self,
        page: int = 1,
        per_page: int = 15,
        search: Optional[str] = None,
        filter_type: Optional[str] = None,
    ) -> Pagination:
        pass

    @abstractmethod
    def get_inventory_by_id(self, inventory_id: int) -> InventoryResponse:
        pass

    @abstractmethod
    def create_inventory(
        self, data: dict, performed_by: Optional[int] = None
    ) -> InventoryResponse:
        pass

    @abstractmethod
    def update_inventory(self, inventory_id: int, data: dict) -> InventoryResponse:
        pass

    @abstractmethod
    def add_transaction(
        self, inventory_id: int, data: dict, performed_by: int
    ) -> None:
        pass

    @abstractmethod
    def get_recent_transactions(self, inventory_id: int, limit: int = 20) -> List[InventoryTransactionResponse]:
        pass

    @abstractmethod
    def get_all_medicines(self) -> List[MedicineResponse]:
        pass
