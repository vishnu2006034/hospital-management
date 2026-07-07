from abc import ABC, abstractmethod
from typing import List, Optional
from flask_sqlalchemy.pagination import Pagination
from app.dtos.user import UserResponse, RoleResponse, UserRoleResponse

class IStaffService(ABC):
    @abstractmethod
    def get_all_staff(
        self, page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        pass

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> UserResponse:
        pass

    @abstractmethod
    def generate_employee_code(self) -> str:
        pass

    @abstractmethod
    def create_staff(self, data: dict) -> UserResponse:
        pass

    @abstractmethod
    def update_staff(self, user_id: int, data: dict) -> UserResponse:
        pass

    @abstractmethod
    def get_user_roles(self, user_id: int) -> List[UserRoleResponse]:
        pass

    @abstractmethod
    def toggle_role(self, user_id: int, role_id: int) -> str:
        pass

    @abstractmethod
    def get_all_roles(self) -> List[RoleResponse]:
        pass

    @abstractmethod
    def get_role_by_id(self, role_id: int) -> Optional[RoleResponse]:
        pass

    @abstractmethod
    def get_active_doctors_count(self) -> int:
        pass
