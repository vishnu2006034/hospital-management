"""Staff service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.user_repository import UserRepository
from app.utils import clean_input_data


class StaffService:
    """Service layer for Staff (User) business operations."""
    _user_repository:UserRepository=UserRepository()
    @staticmethod
    def get_all_staff(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        """Get paginated list of staff members."""
        return StaffService._user_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_user_by_id(user_id: int) -> User:
        """Get a user by ID."""
        return StaffService._user_repository.get_by_id(user_id)

    @staticmethod
    def generate_employee_code() -> str:
        return StaffService._user_repository.get_next_employee_code()

    @staticmethod
    def create_staff(data: Dict[str, Any]) -> User:
        """Create a new staff member."""
        cleaned = clean_input_data(data)

        user: User = User()
        user.employee_code=StaffService._user_repository.get_next_employee_code()
        user.first_name=cleaned['first_name']
        user.last_name=cleaned.get('last_name')
        user.gender=cleaned.get('gender')
        user.dob=cleaned.get('dob')
        user.phone=cleaned.get('phone')
        user.email=cleaned.get('email')
        user.department=cleaned.get('department')
        user.specialization=cleaned.get('specialization')
        user.license_number=cleaned.get('license_number')
        user.joining_date=cleaned.get('joining_date')
        user.status=cleaned.get('status') or 'ACTIVE'
        user.set_password(cleaned.get('password'))
        StaffService._user_repository.add(user)

        role_id: Optional[int] = cleaned.get('role_id')
        if role_id:
            StaffService._user_repository.assign_role(user.user_id, role_id)

        StaffService._user_repository.commit()
        return user

    @staticmethod
    def update_staff(user: User, data: Dict[str, Any]) -> User:
        """Update an existing staff member."""
        cleaned = clean_input_data(data)

        editable_fields = (
            "first_name",
            "last_name",
            "gender",
            "dob",
            "phone",
            "email",
            "department",
            "specialization",
            "license_number",
            "joining_date",
        )

        for field in editable_fields:
            if field in cleaned:
                setattr(user, field, cleaned[field])

        # Update status using encapsulated methods
        status = cleaned.get("status")
        if status == "ACTIVE":
            user.activate()
        elif status == "INACTIVE":
            user.deactivate()
        elif status == "SUSPENDED":
            user.suspend()

        # Update password using the write-only property
        if cleaned.get("password"):
            user.password = cleaned["password"]

        StaffService._user_repository.commit()
        return user

    @staticmethod
    def get_user_roles(user_id: int) -> List[UserRole]:
        """Get all role assignments for a user."""
        return StaffService._user_repository.get_user_roles(user_id)

    @staticmethod
    def toggle_role(user_id: int, role_id: int) -> str:
        """Toggle a role's active status for a user."""
        return StaffService._user_repository.toggle_role(user_id, role_id)

    @staticmethod
    def get_all_roles() -> List[Role]:
        """Get all available roles."""
        return StaffService._user_repository.get_all_roles()

    @staticmethod
    def get_role_by_id(role_id: int) -> Optional[Role]:
        """Get a role by ID."""
        return StaffService._user_repository.get_role_by_id(role_id)
