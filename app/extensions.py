"""Flask extensions initialization.

This module initializes all Flask extensions used throughout the application.
Extensions are instantiated here but bound to the app in create_app().
"""

from typing import Any
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

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
