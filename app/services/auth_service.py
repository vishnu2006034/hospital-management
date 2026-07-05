"""Authentication service for business logic."""

from typing import Dict, List, Optional, Any

from flask_login import login_user, logout_user

from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    
    """Service layer for Authentication business operations."""
    _user_repository:UserRepository=UserRepository()
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password."""
      
        user: Optional[User] = AuthService._user_repository.get_by_email(email)
        if user is None or not user.check_password(password):
            return None
        
        def can_login(self) -> bool:
            return self.status == "ACTIVE"
        return user
    
    @staticmethod
    def login(user: User, remember: bool = False) -> None:
        login_user(user, remember=remember)

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
        user_repository = UserRepository()
        return AuthService._user_repository.get_next_employee_code()

    @staticmethod
    def create_user(data: Dict[str, str]) -> User:
        """Create a new user account."""
        user: User = User()
        user.employee_code=AuthService._user_repository.get_next_employee_code()
        user.first_name=data['first_name']
        user.last_name=data.get('last_name')
        user.email=data['email']
        user.status='ACTIVE'
        user.password=data['password']
        AuthService._user_repository.add(user)

        role_name: Optional[str] = data.get('role')
        if role_name:
            role = AuthService._user_repository.get_role_by_name(role_name)
            if role:
                AuthService.user_repository.assign_role(user.user_id, role.role_id)

        AuthService.user_repository.commit()
        return user
