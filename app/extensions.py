"""Flask extensions initialization.

This module initializes all Flask extensions used throughout the application.
Extensions are instantiated here but bound to the app in create_app().
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

class BaseModel(DeclarativeBase):
    __allow_unmapped__ = True

# ── Database ─────────────────────────────────────────────────────
db: SQLAlchemy = SQLAlchemy(model_class=BaseModel)
migrate: Migrate = Migrate()

# ── Security ─────────────────────────────────────────────────────
csrf: CSRFProtect = CSRFProtect()
