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

    @app.cli.command('seed-data')
    def seed_data():
        """Seed the database with roles, lab test catalog, medicines, and inventory."""
        from app.models.role import Role
        from app.models.lab_test_catalog import LabTestCatalog
        from app.models.medicine import Medicine
        from app.models.inventory import Inventory
        from datetime import date, timedelta

        # 1. Seed Roles
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

        roles_added = 0
        for role_name, description in default_roles:
            if not Role.query.filter_by(role_name=role_name).first():
                db.session.add(Role(role_name=role_name, description=description))
                roles_added += 1

        # 2. Seed Lab Test Catalog
        default_tests = [
            {
                'test_code': 'CBC',
                'test_name': 'Complete Blood Count',
                'category': 'Hematology',
                'sample_type': 'Whole Blood',
                'unit': '10^3/uL',
                'reference_range': '4.5 - 11.0',
                'normal_min': 4.5,
                'normal_max': 11.0,
                'default_price': 350.00,
                'description': 'Evaluates overall health and detects a wide range of disorders, including anemia, infection and leukemia.'
            },
            {
                'test_code': 'GLU_FAST',
                'test_name': 'Blood Glucose (Fasting)',
                'category': 'Biochemistry',
                'sample_type': 'Fluoride Plasma',
                'unit': 'mg/dL',
                'reference_range': '70 - 99',
                'normal_min': 70.0,
                'normal_max': 99.0,
                'default_price': 150.00,
                'description': 'Measures blood sugar level after fasting.'
            },
            {
                'test_code': 'LIPID',
                'test_name': 'Lipid Profile',
                'category': 'Biochemistry',
                'sample_type': 'Serum',
                'unit': 'mg/dL',
                'reference_range': '< 200',
                'normal_min': 0.0,
                'normal_max': 200.0,
                'default_price': 600.00,
                'description': 'Measures cholesterol and triglycerides in the blood.'
            },
            {
                'test_code': 'LFT',
                'test_name': 'Liver Function Test',
                'category': 'Biochemistry',
                'sample_type': 'Serum',
                'unit': 'U/L',
                'reference_range': '7 - 56',
                'normal_min': 7.0,
                'normal_max': 56.0,
                'default_price': 750.00,
                'description': 'Measures the levels of proteins, liver enzymes, and bilirubin in your blood.'
            },
            {
                'test_code': 'THYROID',
                'test_name': 'Thyroid Profile (T3, T4, TSH)',
                'category': 'Endocrinology',
                'sample_type': 'Serum',
                'unit': 'uIU/mL',
                'reference_range': '0.45 - 4.50',
                'normal_min': 0.45,
                'normal_max': 4.50,
                'default_price': 800.00,
                'description': 'Checks how well your thyroid is working and detects thyroid disorders.'
            },
            {
                'test_code': 'RFT',
                'test_name': 'Renal Function Test',
                'category': 'Biochemistry',
                'sample_type': 'Serum',
                'unit': 'mg/dL',
                'reference_range': '0.6 - 1.2',
                'normal_min': 0.6,
                'normal_max': 1.2,
                'default_price': 500.00,
                'description': 'Checks kidney function by measuring creatinine and blood urea nitrogen.'
            },
            {
                'test_code': 'HBA1C',
                'test_name': 'HbA1c (Glycated Hemoglobin)',
                'category': 'Biochemistry',
                'sample_type': 'Whole Blood',
                'unit': '%',
                'reference_range': '4.0 - 5.6',
                'normal_min': 4.0,
                'normal_max': 5.6,
                'default_price': 450.00,
                'description': 'Reflects average blood sugar levels over the past 2 to 3 months.'
            },
            {
                'test_code': 'URINE_R_M',
                'test_name': 'Urine Routine Analysis',
                'category': 'Urinalysis',
                'sample_type': 'Urine',
                'unit': None,
                'reference_range': 'Normal',
                'normal_min': None,
                'normal_max': None,
                'default_price': 200.00,
                'description': 'Physical, chemical, and microscopic examination of urine.'
            }
        ]

        tests_added = 0
        for test_data in default_tests:
            if not LabTestCatalog.query.filter_by(test_code=test_data['test_code']).first():
                db.session.add(LabTestCatalog(**test_data))
                tests_added += 1

        # 3. Seed Medicines & Inventory
        default_medicines = [
            {
                'medicine_name': 'Paracetamol 650mg',
                'generic_name': 'Acetaminophen',
                'category': 'Analgesic/Antipyretic',
                'dosage_form': 'Tablet',
                'strength': '650mg',
                'manufacturer': 'GSK',
                'unit_price': 2.00,
                'batch_number': 'PM8902',
                'quantity': 500,
                'min_stock': 50,
                'supplier': 'Astra Health'
            },
            {
                'medicine_name': 'Amoxicillin 500mg',
                'generic_name': 'Amoxicillin',
                'category': 'Antibiotic',
                'dosage_form': 'Capsule',
                'strength': '500mg',
                'manufacturer': 'Abbott',
                'unit_price': 5.00,
                'batch_number': 'AM2341',
                'quantity': 200,
                'min_stock': 20,
                'supplier': 'Medica Distributors'
            },
            {
                'medicine_name': 'Ibuprofen 400mg',
                'generic_name': 'Ibuprofen',
                'category': 'NSAID',
                'dosage_form': 'Tablet',
                'strength': '400mg',
                'manufacturer': 'Pfizer',
                'unit_price': 3.50,
                'batch_number': 'IB4492',
                'quantity': 300,
                'min_stock': 30,
                'supplier': 'Global Pharma'
            },
            {
                'medicine_name': 'Metformin 500mg',
                'generic_name': 'Metformin Hydrochloride',
                'category': 'Antidiabetic',
                'dosage_form': 'Tablet',
                'strength': '500mg',
                'manufacturer': 'Merck',
                'unit_price': 1.50,
                'batch_number': 'MT1092',
                'quantity': 400,
                'min_stock': 40,
                'supplier': 'Astra Health'
            },
            {
                'medicine_name': 'Pantoprazole 40mg',
                'generic_name': 'Pantoprazole Sodium',
                'category': 'Proton Pump Inhibitor',
                'dosage_form': 'Tablet',
                'strength': '40mg',
                'manufacturer': 'Sun Pharma',
                'unit_price': 4.00,
                'batch_number': 'PP7721',
                'quantity': 250,
                'min_stock': 25,
                'supplier': 'Sun Pharma Distributors'
            }
        ]

        meds_added = 0
        inventory_added = 0
        for med_data in default_medicines:
            medicine = Medicine.query.filter_by(medicine_name=med_data['medicine_name']).first()
            if not medicine:
                medicine = Medicine(
                    medicine_name=med_data['medicine_name'],
                    generic_name=med_data['generic_name'],
                    category=med_data['category'],
                    dosage_form=med_data['dosage_form'],
                    strength=med_data['strength'],
                    manufacturer=med_data['manufacturer'],
                    unit_price=med_data['unit_price']
                )
                db.session.add(medicine)
                db.session.flush() # get medicine_id
                meds_added += 1
            
            # Check inventory batch
            if not Inventory.query.filter_by(medicine_id=medicine.medicine_id, batch_number=med_data['batch_number']).first():
                inventory = Inventory(
                    medicine_id=medicine.medicine_id,
                    batch_number=med_data['batch_number'],
                    expiry_date=date.today() + timedelta(days=365),
                    purchase_price=med_data['unit_price'] * 0.7, # 30% margin
                    selling_price=med_data['unit_price'],
                    quantity_in_stock=med_data['quantity'],
                    minimum_stock=med_data['min_stock'],
                    supplier=med_data['supplier']
                )
                db.session.add(inventory)
                inventory_added += 1

        db.session.commit()
        click.echo("Database seeding completed:")
        click.echo(f"  - Seeded {roles_added} role(s).")
        click.echo(f"  - Seeded {tests_added} lab test profile(s).")
        click.echo(f"  - Seeded {meds_added} medicine(s).")
        click.echo(f"  - Seeded {inventory_added} inventory batch(es).")


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
