"""UserRole association model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app import db

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.role import Role


class UserRole(db.Model):
    """Many-to-many association between User and Role with metadata.

    Links users to their assigned roles and tracks who assigned the role
    and when it was assigned. Supports activation/deactivation of roles.
    """

    __tablename__: str = 'user_roles'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )

    # Primary Key
    user_role_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    user_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
    )
    role_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('roles.role_id', ondelete='CASCADE'),
        nullable=False,
    )
    assigned_by: Optional[int] = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id', ondelete='SET NULL'),
    )

    # Metadata
    assigned_at: datetime = db.Column(db.DateTime, server_default=db.func.now())
    is_active: bool = db.Column(db.Boolean, default=True)

    # Relationships
    user: 'User' = db.relationship(
        'User', back_populates='user_roles', foreign_keys=[user_id]
    )
    role: 'Role' = db.relationship('Role', back_populates='user_roles')
    assigner: Optional['User'] = db.relationship('User', foreign_keys=[assigned_by])

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

