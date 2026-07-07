from abc import ABC, abstractmethod
from typing import List, Optional
from flask_sqlalchemy.pagination import Pagination
from app.dtos.prescription import PrescriptionResponse
from app.dtos.inventory import InventoryResponse
from app.dtos.visit import VisitResponse

class IPrescriptionService(ABC):
    @abstractmethod
    def get_all_prescriptions(
        self, page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        pass

    @abstractmethod
    def get_prescription_by_id(self, prescription_id: int) -> PrescriptionResponse:
        pass

    @abstractmethod
    def create_prescription(self, data: dict, prescribed_by: int) -> PrescriptionResponse:
        pass

    @abstractmethod
    def delete_prescription(self, prescription_id: int) -> None:
        pass

    @abstractmethod
    def get_available_inventory(self) -> List[InventoryResponse]:
        pass

    @abstractmethod
    def get_recent_visits(self, limit: int = 50) -> List[VisitResponse]:
        pass
