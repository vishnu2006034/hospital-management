"""Authentication service for business logic."""

from typing import Dict, List, Optional, Any

from flask_login import login_user, logout_user

from app import db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.interfaces.auth_service_interface import IAuthService
from app.dtos.user import UserResponse, UserCreateRequest
from app.mappers.user_mapper import UserMapper


class AuthService(IAuthService):
    """Service layer for Authentication business operations."""
    _user_repository: UserRepository = UserRepository()

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[UserResponse]:
        """Authenticate a user by email and password."""
        # Retrieve the user model to verify password
        user_model = User.query.filter_by(email=email).first()
        if user_model is None or not user_model.check_password(password):
            return None
        return UserMapper.to_dto(user_model)

    @staticmethod
    def login(user: UserResponse, remember: bool = False) -> None:
        user_model = db.session.get(User, user.user_id)
        if user_model:
            login_user(user_model, remember=remember)

    @staticmethod
    def logout() -> None:
        logout_user()

    @staticmethod
    def validate_registration(data: Dict[str, str]) -> List[str]:
        """Validate registration data."""
        errors: List[str] = []
        if not data.get('first_name'):
            errors.append('First name is required.')
        if not data.get('email'):
            errors.append('Email is required.')
        if not data.get('password'):
            errors.append('Password is required.')
        if data.get('password') != data.get('confirm_password'):
            errors.append('Passwords do not match.')
        if len(data.get('password', '')) < 6:
            errors.append('Password must be at least 6 characters.')
        if AuthService._user_repository.exists(email=data.get('email', '')):
            errors.append('An account with this email already exists.')
        return errors

    @staticmethod
    def generate_employee_code() -> str:
        return AuthService._user_repository.get_next_employee_code()

    @staticmethod
    def create_user(data: Dict[str, str]) -> UserResponse:
        """Create a new user account."""
        dto = UserCreateRequest(
            first_name=data['first_name'],
            last_name=data.get('last_name'),
            email=data['email'],
            password=data['password']
        )
        user_dto = AuthService._user_repository.add(dto)

        role_name: Optional[str] = data.get('role')
        if role_name:
            role = AuthService._user_repository.get_role_by_name(role_name)
            if role:
                AuthService._user_repository.assign_role(user_dto.user_id, role.role_id)

        AuthService._user_repository.commit()
        # Reload to get the assigned roles
        return AuthService._user_repository.get_by_id(user_dto.user_id)
