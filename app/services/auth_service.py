"""Authentication service for business logic."""

from typing import Dict, List, Optional, Any

from flask_login import login_user, logout_user

from app.models.user import User
from app.repositories.user_repository import user_repository


class AuthService:
    """Service layer for Authentication business operations."""

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """Authenticate a user by email and password.

        Args:
            email: User's email address.
            password: User's password.

        Returns:
            The authenticated user, or None if invalid.
        """
        user: Optional[User] = user_repository.get_by_email(email)
        if user is None or not user.check_password(password):
            return None
        if user.status != 'ACTIVE':
            return None
        return user

    @staticmethod
    def login(user: User, remember: bool = False) -> None:
        """Log in a user.

        Args:
            user: The user to log in.
            remember: Whether to remember the user session.
        """
        login_user(user, remember=remember)

    @staticmethod
    def logout() -> None:
        """Log out the current user."""
        logout_user()

    @staticmethod
    def validate_registration(data: Dict[str, str]) -> List[str]:
        """Validate registration data.

        Args:
            data: Registration form data.

        Returns:
            List of validation error messages (empty if valid).
        """
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
        if user_repository.exists(email=data.get('email', '')):
            errors.append('An account with this email already exists.')
        return errors

    @staticmethod
    def generate_employee_code() -> str:
        """Generate a new employee code.

        Returns:
            A unique employee code.
        """
        return user_repository.get_next_employee_code()

    @staticmethod
    def create_user(data: Dict[str, str]) -> User:
        """Create a new user account.

        Args:
            data: User registration data.

        Returns:
            The created user entity.
        """
        user: User = User(
            employee_code=user_repository.get_next_employee_code(),
            first_name=data['first_name'],
            last_name=data.get('last_name'),
            email=data['email'],
            status='ACTIVE',
        )
        user.set_password(data['password'])
        user_repository.add(user)

        role_name: Optional[str] = data.get('role')
        if role_name:
            role = user_repository.get_role_by_name(role_name)
            if role:
                user_repository.assign_role(user.user_id, role.role_id)

        user_repository.commit()
        return user
