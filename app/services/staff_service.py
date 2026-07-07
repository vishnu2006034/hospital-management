"""Staff service for business logic."""

from typing import Dict, List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.interfaces.staff_service_interface import IStaffService
from app.dtos.user import UserResponse, UserCreateRequest, UserUpdateRequest, RoleResponse, UserRoleResponse
from app.mappers.user_mapper import UserMapper
from app.utils import clean_input_data


class StaffService(IStaffService):
    """Service layer for Staff (User) business operations."""
    _user_repository: UserRepository = UserRepository()

    @staticmethod
    def get_all_staff(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ) -> Pagination:
        """Get paginated list of staff members."""
        return StaffService._user_repository.search(search, page=page, per_page=per_page)

    @staticmethod
    def get_user_by_id(user_id: int) -> UserResponse:
        """Get a user by ID."""
        return StaffService._user_repository.get_by_id(user_id)

    @staticmethod
    def generate_employee_code() -> str:
        return StaffService._user_repository.get_next_employee_code()

    @staticmethod
    def create_staff(data: Dict[str, Any]) -> UserResponse:
        """Create a new staff member."""
        cleaned = clean_input_data(data)

        dto = UserCreateRequest(
            first_name=cleaned['first_name'],
            last_name=cleaned.get('last_name'),
            email=cleaned['email'],
            password=cleaned.get('password'),
            gender=cleaned.get('gender'),
            dob=cleaned.get('dob'),
            phone=cleaned.get('phone'),
            department=cleaned.get('department'),
            specialization=cleaned.get('specialization'),
            license_number=cleaned.get('license_number'),
            joining_date=cleaned.get('joining_date'),
            status=cleaned.get('status') or 'ACTIVE',
            role_id=int(cleaned.get('role_id')) if cleaned.get('role_id') else None
        )

        user_dto = StaffService._user_repository.add(dto)

        if dto.role_id:
            StaffService._user_repository.assign_role(user_dto.user_id, dto.role_id)

        StaffService._user_repository.commit()
        return StaffService._user_repository.get_by_id(user_dto.user_id)

    @staticmethod
    def update_staff(user_id: int, data: Dict[str, Any]) -> UserResponse:
        """Update an existing staff member."""
        cleaned = clean_input_data(data)
        user_model = db.session.get(User, user_id)
        if not user_model:
            return None

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
                setattr(user_model, field, cleaned[field])

        # Set status directly on user model
        status = cleaned.get("status")
        if status:
            user_model.status = status

        # Update password if provided
        if cleaned.get("password"):
            user_model.password = cleaned["password"]

        StaffService._user_repository.commit()
        return UserMapper.to_dto(user_model)

    @staticmethod
    def get_user_roles(user_id: int) -> List[UserRoleResponse]:
        """Get all role assignments for a user."""
        return StaffService._user_repository.get_user_roles(user_id)

    @staticmethod
    def toggle_role(user_id: int, role_id: int) -> str:
        """Toggle a role's active status for a user."""
        action = StaffService._user_repository.toggle_role(user_id, role_id)
        StaffService._user_repository.commit()
        return action

    @staticmethod
    def get_all_roles() -> List[RoleResponse]:
        """Get all available roles."""
        return StaffService._user_repository.get_all_roles()

    @staticmethod
    def get_role_by_id(role_id: int) -> Optional[RoleResponse]:
        """Get a role by ID."""
        return StaffService._user_repository.get_role_by_id(role_id)

    @staticmethod
    def get_active_doctors_count() -> int:
        """Count active doctors."""
        return StaffService._user_repository.get_active_doctors_count()
