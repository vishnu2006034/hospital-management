"""Role database model."""

from datetime import datetime
from typing import TYPE_CHECKING, List

from app import db

if TYPE_CHECKING:
    from app.models.user_role import UserRole


class Role(db.Model):
    """System role — Administrator, Doctor, Nurse, etc.

    Defines the different roles available in the hospital system.
    Each role grants specific permissions and access levels.
    """

    __tablename__: str = 'roles'

    # Primary Key
    role_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Role Information
    role_name: str = db.Column(db.String(50), unique=True, nullable=False)
    description: str = db.Column(db.Text)

    # Timestamps
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    user_roles: List['UserRole'] = db.relationship(
        'UserRole', back_populates='role', lazy='dynamic', passive_deletes=True
    )

