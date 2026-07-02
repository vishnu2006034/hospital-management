import click
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_cors import CORS

from config import config

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()

# Configure login manager
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'warning'


def create_app(config_name='development'):
    """Application factory pattern."""
    flask_app = Flask(__name__)
    flask_app.config.from_object(config[config_name])
    config[config_name].init_app(flask_app)

    # Initialize extensions with app
    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)
    csrf.init_app(flask_app)
    mail.init_app(flask_app)
    CORS(flask_app)

    # Import models so Flask-Migrate can detect them
    with flask_app.app_context():
        from app import models  # noqa: F401

    # Flask-Login user loader
    @login_manager.user_loader
    def load_user(user_id):
        from app.models.user import User
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.patients import patients_bp
    from app.routes.visits import visits_bp
    from app.routes.prescriptions import prescriptions_bp
    from app.routes.medicines import medicines_bp
    from app.routes.inventory import inventory_bp
    from app.routes.laboratory import laboratory_bp
    from app.routes.reports import reports_bp
    from app.routes.staff import staff_bp

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

    # Register CLI commands
    register_cli_commands(flask_app)

    # Register error handlers
    register_error_handlers(flask_app)

    return flask_app


def register_cli_commands(app):
    """Register custom Flask CLI commands."""

    @app.cli.command('seed-roles')
    def seed_roles():
        """Seed the roles table with default roles."""
        from app.models.role import Role

        default_roles = [
            ('Administrator', 'System Administrator'),
            ('Doctor', 'Medical Practitioner'),
            ('Nurse', 'Nursing Staff'),
            ('Receptionist', 'Reception'),
            ('Pharmacist', 'Pharmacy'),
            ('Lab Technician', 'Laboratory'),
            ('Inventory Manager', 'Inventory'),
            ('Accountant', 'Billing'),
            ('Patient', 'Portal User'),
        ]

        added = 0
        for role_name, description in default_roles:
            if not Role.query.filter_by(role_name=role_name).first():
                db.session.add(Role(role_name=role_name, description=description))
                added += 1

        db.session.commit()
        click.echo(f'Seeded {added} new role(s). Total roles: {Role.query.count()}')

    @app.cli.command('create-admin')
    @click.option('--code', prompt='Employee code', help='Unique employee code')
    @click.option('--email', prompt='Email', help='Admin email')
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
    @click.option('--first-name', prompt='First name')
    @click.option('--last-name', prompt='Last name', default='')
    def create_admin(code, email, password, first_name, last_name):
        """Create an administrator user."""
        from app.models.user import User
        from app.models.role import Role
        from app.models.user_role import UserRole

        if User.query.filter_by(email=email).first():
            click.echo(f'Error: User with email {email} already exists.')
            return

        user = User(
            employee_code=code,
            first_name=first_name,
            last_name=last_name or None,
            email=email,
            status='ACTIVE',
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # get user_id

        admin_role = Role.query.filter_by(role_name='Administrator').first()
        if admin_role:
            db.session.add(UserRole(user_id=user.user_id, role_id=admin_role.role_id))

        db.session.commit()
        click.echo(f'Admin user "{user.full_name}" created successfully.')


def register_error_handlers(app):
    """Register custom error pages."""

    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not Found', 'message': 'The requested resource was not found.'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return {'error': 'Internal Server Error', 'message': 'An unexpected error occurred.'}, 500

    @app.errorhandler(403)
    def forbidden(error):
        return {'error': 'Forbidden', 'message': 'You do not have permission to access this resource.'}, 403
