"""Staff service for business logic."""

from typing import Dict, List, Optional, Any

from app.models.user import User
from app.repositories.user_repository import user_repository


class StaffService:
    """Service layer for Staff (User) business operations."""

    @staticmethod
    def get_all_staff(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ):
        """Get paginated list of staff members."""
        return user_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Get a user by ID."""
        return user_repository.get_by_id(user_id)

    @staticmethod
    def generate_employee_code() -> str:
        return user_repository.get_next_employee_code()

    @staticmethod
    def create_staff(data: Dict[str, Any]) -> User:
        """Create a new staff member."""
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        user: User = User(
            employee_code=user_repository.get_next_employee_code(),
            first_name=cleaned['first_name'],
            last_name=cleaned.get('last_name'),
            gender=cleaned.get('gender'),
            dob=cleaned.get('dob'),
            phone=cleaned.get('phone'),
            email=cleaned.get('email'),
            department=cleaned.get('department'),
            specialization=cleaned.get('specialization'),
            license_number=cleaned.get('license_number'),
            joining_date=cleaned.get('joining_date'),
            status=cleaned.get('status') or 'ACTIVE',
        )
        user.set_password(cleaned.get('password'))
        user_repository.add(user)

        role_id: Optional[int] = cleaned.get('role_id')
        if role_id:
            user_repository.assign_role(user.user_id, role_id)

        user_repository.commit()
        return user

    @staticmethod
    def update_staff(user: User, data: Dict[str, Any]) -> User:
        """Update an existing staff member."""
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        user.first_name = cleaned['first_name']
        user.last_name = cleaned.get('last_name')
        user.gender = cleaned.get('gender')
        user.dob = cleaned.get('dob')
        user.phone = cleaned.get('phone')
        user.email = cleaned.get('email')
        user.department = cleaned.get('department')
        user.specialization = cleaned.get('specialization')
        user.license_number = cleaned.get('license_number')
        user.joining_date = cleaned.get('joining_date')
        user.status = cleaned.get('status') or 'ACTIVE'
        if cleaned.get('password'):
            user.set_password(cleaned['password'])
        user_repository.commit()
        return user

    @staticmethod
    def get_user_roles(user_id: int) -> List:
        """Get all role assignments for a user."""
        return user_repository.get_user_roles(user_id)

    @staticmethod
    def toggle_role(user_id: int, role_id: int) -> str:
        """Toggle a role's active status for a user."""
        return user_repository.toggle_role(user_id, role_id)

    @staticmethod
    def get_all_roles() -> List:
        """Get all available roles."""
        return user_repository.get_all_roles()

    @staticmethod
    def get_role_by_id(role_id: int):
        """Get a role by ID."""
        return user_repository.get_role_by_id(role_id)
