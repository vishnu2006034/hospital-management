"""User repository for database operations."""

from typing import List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.user_repository_interface import IUserRepository
from app.mappers.user_mapper import UserMapper
from app.dtos.user import UserResponse, UserCreateRequest, UserUpdateRequest, RoleResponse, UserRoleResponse
from app.utils import generate_sequential_code


class UserRepository(BaseRepository[User], IUserRepository):
    """Repository for User entity database operations."""

    def __init__(self) -> None:
        super().__init__(User)

    def get_by_id(self, id_value: int) -> Optional[UserResponse]:
        model = db.session.get(User, id_value)
        return UserMapper.to_dto(model) if model else None

    def add(self, entity_dto: UserCreateRequest) -> UserResponse:
        model = UserMapper.to_model(entity_dto)
        db.session.add(model)
        db.session.flush()
        return UserMapper.to_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(User, entity_id)
        if model:
            db.session.delete(model)

    def search(
        self,
        search: Optional[str] = None,
        page: int = 1,
        per_page: int = 15,
        sort_by: str = "created_at",
        descending: bool = True,
    ) -> Pagination:
        """Search users with pagination."""
        query = User.query

        if search:
            query = query.filter(
                db.or_(
                    User.first_name.ilike(f"%{search}%"),
                    User.last_name.ilike(f"%{search}%"),
                    User.employee_code.ilike(f"%{search}%"),
                    User.email.ilike(f"%{search}%"),
                    User.department.ilike(f"%{search}%"),
                )
            )

        # Whitelist sortable fields
        allowed_sort_fields = (
            "created_at",
            "first_name",
            "last_name",
            "employee_code",
            "email",
            "department",
            "joining_date",
            "status",
        )

        if sort_by not in allowed_sort_fields:
            sort_by = "created_at"

        column = getattr(User, sort_by)
        query = query.order_by(
            column.desc() if descending else column.asc()
        )

        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )
        pagination.items = [UserMapper.to_dto(u) for u in pagination.items]
        return pagination

    def get_by_email(self, email: str) -> Optional[UserResponse]:
        """Get a user by their email address."""
        model = User.query.filter_by(email=email).first()
        return UserMapper.to_dto(model) if model else None

    def get_next_employee_code(self) -> str:
        """Generate the next available employee code."""
        return generate_sequential_code(User, 'user_id', 'EMP')

    def get_user_roles(self, user_id: int) -> List[UserRoleResponse]:
        """Get all role assignments for a user."""
        models = UserRole.query.filter_by(user_id=user_id).all()
        return [UserMapper.to_user_role_dto(ur) for ur in models]

    def assign_role(self, user_id: int, role_id: int) -> UserRoleResponse:
        """Assign a role to a user."""
        user_role = UserRole(user_id=user_id, role_id=role_id)
        db.session.add(user_role)
        db.session.flush()
        return UserMapper.to_user_role_dto(user_role)

    def toggle_role(self, user_id: int, role_id: int) -> str:
        """Toggle a role's active status for a user."""
        existing = UserRole.query.filter_by(
            user_id=user_id, role_id=role_id
        ).first()
        if existing:
            existing.is_active = not existing.is_active
            return 'activated' if existing.is_active else 'deactivated'
        else:
            self.assign_role(user_id, role_id)
            return 'assigned'

    def get_role_by_name(self, role_name: str) -> Optional[RoleResponse]:
        """Get a role by its name."""
        model = Role.query.filter_by(role_name=role_name).first()
        return UserMapper.to_role_dto(model) if model else None

    def get_role_by_id(self, role_id: int) -> Optional[RoleResponse]:
        """Get a role by its ID."""
        model = db.session.get(Role, role_id)
        return UserMapper.to_role_dto(model) if model else None

    def get_all_roles(self) -> List[RoleResponse]:
        """Get all available roles."""
        models = Role.query.order_by(Role.role_name).all()
        return [UserMapper.to_role_dto(r) for r in models]

    def get_all_doctors(self) -> List[UserResponse]:
        """Get all active doctors."""
        doctors = User.query.join(
            UserRole, User.user_id == UserRole.user_id
        ).join(
            Role, UserRole.role_id == Role.role_id
        ).filter(
            Role.role_name == 'Doctor',
            User.status == 'ACTIVE'
        ).all()
        if not doctors:
            doctors = User.query.filter_by(status='ACTIVE').order_by(
                User.first_name
            ).all()
        return [UserMapper.to_dto(d) for d in doctors]

    def get_all_technicians(self) -> List[UserResponse]:
        """Get all active lab technicians."""
        models = User.query.filter_by(status='ACTIVE').order_by(User.first_name).all()
        return [UserMapper.to_dto(t) for t in models]

    def get_active_doctors_count(self) -> int:
        """Count active doctors."""
        role_name = 'Doctor'
        doctor_role = Role.query.filter_by(role_name=role_name).first()
        if doctor_role:
            return User.query.join(
                UserRole, User.user_id == UserRole.user_id
            ).filter(
                UserRole.role_id == doctor_role.role_id,
                UserRole.is_active.is_(True),
                User.status == 'ACTIVE',
            ).count()
        else:
            return User.query.filter_by(status='ACTIVE').count()


user_repository: UserRepository = UserRepository()
