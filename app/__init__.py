
from typing import Optional

from flask import Flask
from flask_login import LoginManager

from config import Config
from app.extensions import db, migrate, csrf
from app.errors import register_error_handlers

# Authentication
login_manager: LoginManager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'

# The application models have been migrated to the CRUD engine.


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

    # Initialize CRUD Provider
    from hogc.engines.crud import PostgreSQLCRUDProvider
    from hogc.engines.crud.schema.base import Base
    from contextlib import contextmanager
    @contextmanager
    def session_context():
        yield db.session

    from app import extensions
    extensions.crud_provider = PostgreSQLCRUDProvider(session_factory=session_context)

    # Create EAV Tables and Seed Metadata
    with flask_app.app_context():
        Base.metadata.create_all(db.engine)
        from app.crud_init import initialize_crud_metadata
        initialize_crud_metadata()

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[extensions.UserSession]:
        from app.extensions import crud_provider, UserSession
        from hogc.lib.base import RequestContext as BaseRequestContext
        from hogc.lib.contracts.crud.requests import GetRecordRequest
        from hogc.lib.kernel.context import HogcContext, TenantContext, UserContext, ExecutionContext, RequestContext, get_context_provider

        provider_ctx = get_context_provider()
        tenant = TenantContext(tenant_id="default", org_id="default")
        user = UserContext(user_id=user_id, username="system", email="system@example.com")
        exec_ctx = ExecutionContext(source="system")
        req_ctx = RequestContext(tenant=tenant, user=user, execution=exec_ctx)
        platform_ctx = HogcContext(request=req_ctx)
        token = provider_ctx.set(platform_ctx)

        try:
            base_req_ctx = BaseRequestContext(
                tenant_id="default",
                org_id="default",
                user_id="system",
                roles=[]
            )
            request = GetRecordRequest(
                context=base_req_ctx,
                module_id="user",
                record_id=user_id
            )
            response = crud_provider.records.get_record(request)
            data = response.data.data
            return UserSession(
                user_id=user_id,
                email=data.get("email"),
                first_name=data.get("first_name"),
                last_name=data.get("last_name"),
                status=data.get("status", "ACTIVE"),
                role=data.get("role"),
                password_hash=data.get("password_hash")
            )
        except Exception:
            return None
        finally:
            provider_ctx.reset(token)


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
