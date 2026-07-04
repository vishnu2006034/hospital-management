"""Routes package.

Flask blueprint route handlers for each domain.
"""

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

__all__ = [
    'main_bp',
    'auth_bp',
    'patients_bp',
    'visits_bp',
    'prescriptions_bp',
    'medicines_bp',
    'inventory_bp',
    'laboratory_bp',
    'reports_bp',
    'staff_bp',
]
