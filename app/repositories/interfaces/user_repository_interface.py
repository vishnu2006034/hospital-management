from abc import ABC, abstractmethod
from typing import List, Optional, Any
from flask_sqlalchemy.pagination import Pagination
from app.dtos.user import UserResponse, UserCreateRequest, UserUpdateRequest, RoleResponse, UserRoleResponse

class IUserRepository(ABC):
    @abstractmethod
    def get_by_id(self, id_value: int) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def add(self, entity_dto: UserCreateRequest) -> UserResponse:
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
        search: Optional[str],
        page: int = 1,
        per_page: int = 15,
        sort_by: str = "created_at",
        descending: bool = True,
    ) -> Pagination:
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def get_next_employee_code(self) -> str:
        pass

    @abstractmethod
    def get_user_roles(self, user_id: int) -> List[UserRoleResponse]:
        pass

    @abstractmethod
    def assign_role(self, user_id: int, role_id: int) -> UserRoleResponse:
        pass

    @abstractmethod
    def toggle_role(self, user_id: int, role_id: int) -> str:
        pass

    @abstractmethod
    def get_role_by_name(self, role_name: str) -> Optional[RoleResponse]:
        pass

    @abstractmethod
    def get_role_by_id(self, role_id: int) -> Optional[RoleResponse]:
        pass

    @abstractmethod
    def get_all_roles(self) -> List[RoleResponse]:
        pass

    @abstractmethod
    def get_all_doctors(self) -> List[UserResponse]:
        pass

    @abstractmethod
    def get_all_technicians(self) -> List[UserResponse]:
        pass

    @abstractmethod
    def get_active_doctors_count(self) -> int:
        pass
