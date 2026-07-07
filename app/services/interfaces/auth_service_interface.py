from abc import ABC, abstractmethod
from typing import List, Optional
from app.dtos.user import UserResponse, UserCreateRequest

class IAuthService(ABC):
    @abstractmethod
    def authenticate_user(self, email: str, password: str) -> Optional[UserResponse]:
        pass

    @abstractmethod
    def login(self, user: UserResponse, remember: bool = False) -> None:
        pass

    @abstractmethod
    def logout(self) -> None:
        pass

    @abstractmethod
    def validate_registration(self, data: dict) -> List[str]:
        pass

    @abstractmethod
    def generate_employee_code(self) -> str:
        pass

    @abstractmethod
    def create_user(self, data: dict) -> UserResponse:
        pass
