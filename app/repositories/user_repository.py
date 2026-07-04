"""User repository for database operations."""

from typing import List, Optional

from app import db
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User entity database operations."""

    def __init__(self) -> None:
        super().__init__(User)

    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ):
        """Search users with pagination."""
        query = User.query
        if search:
            query = query.filter(
                db.or_(
                    User.first_name.ilike(f'%{search}%'),
                    User.last_name.ilike(f'%{search}%'),
                    User.employee_code.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%'),
                    User.department.ilike(f'%{search}%'),
                )
            )
        query = query.order_by(User.created_at.desc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by their email address."""
        return User.query.filter_by(email=email).first()

    def get_next_employee_code(self) -> str:
        """Generate the next available employee code."""
        last: Optional[User] = User.query.order_by(User.user_id.desc()).first()
        next_num: int = (last.user_id + 1) if last else 1
        return f'EMP{next_num}'

    def get_user_roles(self, user_id: int) -> List[UserRole]:
        """Get all role assignments for a user."""
        return UserRole.query.filter_by(user_id=user_id).all()

    def assign_role(self, user_id: int, role_id: int) -> UserRole:
        """Assign a role to a user."""
        user_role: UserRole = UserRole(user_id=user_id, role_id=role_id)
        db.session.add(user_role)
        return user_role

    def toggle_role(self, user_id: int, role_id: int) -> str:
        """Toggle a role's active status for a user."""
        existing: Optional[UserRole] = UserRole.query.filter_by(
            user_id=user_id, role_id=role_id
        ).first()
        if existing:
            existing.is_active = not existing.is_active
            return 'activated' if existing.is_active else 'deactivated'
        else:
            self.assign_role(user_id, role_id)
            return 'assigned'

    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        """Get a role by its name."""
        return Role.query.filter_by(role_name=role_name).first()

    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        """Get a role by its ID."""
        return db.session.get(Role, role_id)

    def get_all_roles(self) -> List[Role]:
        """Get all available roles."""
        return Role.query.order_by(Role.role_name).all()


user_repository: UserRepository = UserRepository()

