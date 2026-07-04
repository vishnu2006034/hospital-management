
from flask import Flask
from flask_login import LoginManager

from config import Config
from app.extensions import db, migrate, csrf
from app.errors import register_error_handlers

# ── Authentication ───────────────────────────────────────────────
login_manager: LoginManager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# We import models *after* db and extensions are defined and exposed,
# so that any models doing `from app import db` will succeed.
from app import models

from app.constants import (
    VisitType,
    VisitStatus,
    UserStatus,
    RoleName,
    TransactionType,
    ReferenceType,
    LabPriority,
    LabStatus,
    FlashCategory,
)
from app.exceptions import (
    AppError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    BusinessRuleError,
    InsufficientStockError,
    DuplicateResourceError,
)


def create_app() -> Flask:
    """Application factory pattern."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)
    csrf.init_app(flask_app)

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(models.User, int(user_id))

    # Register blueprints
    from app.routes import (
        main_bp,
        auth_bp,
        patients_bp,
        visits_bp,
        prescriptions_bp,
        medicines_bp,
        inventory_bp,
        laboratory_bp,
        reports_bp,
        staff_bp,
    )

    flask_app.register_blueprint(main_bp)
    flask_app.register_blueprint(auth_bp, url_prefix='/auth')
    flask_app.register_blueprint(patients_bp)
    flask_app.register_blueprint(visits_bp)
    flask_app.register_blueprint(prescriptions_bp)
    flask_app.register_blueprint(medicines_bp)
    flask_app.register_blueprint(inventory_bp)
    flask_app.register_blueprint(laboratory_bp)
    flask_app.register_blueprint(reports_bp)
    flask_app.register_blueprint(staff_bp)


    # Register error handlers
    register_error_handlers(flask_app)

    return flask_app


__all__ = [
    'create_app',
    'db',
    'migrate',
    'login_manager',
    'csrf',
    # Subpackages
    'models',
    # Enums
    'VisitType',
    'VisitStatus',
    'UserStatus',
    'RoleName',
    'TransactionType',
    'ReferenceType',
    'LabPriority',
    'LabStatus',
    'FlashCategory',
    # Exceptions
    'AppError',
    'NotFoundError',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'ConflictError',
    'BusinessRuleError',
    'InsufficientStockError',
    'DuplicateResourceError',
]
