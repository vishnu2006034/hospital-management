"""Flask extensions initialization.

This module initializes all Flask extensions used throughout the application.
Extensions are instantiated here but bound to the app in create_app().
"""

from typing import Any
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from hogc.engines.crud import PostgreSQLCRUDProvider

class BaseModel(DeclarativeBase):
    __allow_unmapped__ = True

    def __init__(self, **kwargs: Any) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

# Database
db: SQLAlchemy = SQLAlchemy(model_class=BaseModel)
migrate: Migrate = Migrate()

# Security
csrf: CSRFProtect = CSRFProtect()

# CRUD Provider
crud_provider: PostgreSQLCRUDProvider | None = None

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

class UserSession(UserMixin):
    """Compatibility user class for Flask-Login backed by hogc-crud-engine."""
    
    def __init__(self, user_id: str, email: str, first_name: str, last_name: str | None, status: str, role: str | None, password_hash: str) -> None:
        self.user_id = user_id
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.status = status
        self.role = role
        self.password_hash = password_hash

    def get_id(self) -> str:
        return self.user_id

    @property
    def is_active(self) -> bool:
        return self.status == "ACTIVE"

    @property
    def full_name(self) -> str:
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p)

    @property
    def role_names(self) -> list[str]:
        return [self.role] if self.role else []

    def has_role(self, role_name: str) -> bool:
        return role_name == self.role

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


