"""Main routes.

Dashboard and landing page routes.
"""

from datetime import date
from typing import Dict, Any

from flask import Blueprint, render_template
from flask_login import login_required

from app.extensions import db
from app.constants import VisitType, VisitStatus, RoleName
from app.models.patient import Patient
from app.models.user import User
from app.models.visit import Visit
from app.models.role import Role
from app.models.user_role import UserRole

main_bp: Blueprint = Blueprint('main', __name__)


@main_bp.route('/')
def index() -> str:
    """Landing page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard() -> str:
    """Main dashboard with key metrics."""
    total_patients: int = Patient.query.count()

    # Count active doctors
    doctor_role = Role.query.filter_by(role_name=RoleName.DOCTOR.value).first()
    if doctor_role:
        active_doctors: int = User.query.join(
            UserRole, User.user_id == UserRole.user_id
        ).filter(
            UserRole.role_id == doctor_role.role_id,
            UserRole.is_active.is_(True),
            User.status == 'ACTIVE',
        ).count()
    else:
        active_doctors = User.query.filter_by(status='ACTIVE').count()

    today: date = date.today()
    today_appointments: int = Visit.query.filter(
        db.func.date(Visit.visit_date) == today
    ).count()

    # Calculate available beds (capacity of 100 minus active inpatient visits)
    active_admissions: int = Visit.query.filter_by(
        visit_type=VisitType.INPATIENT.value,
        visit_status=VisitStatus.OPEN.value,
    ).count()
    available_beds: int = max(0, 100 - active_admissions)

    context: Dict[str, Any] = {
        'total_patients': total_patients,
        'active_doctors': active_doctors,
        'today_appointments': today_appointments,
        'available_beds': available_beds,
    }
    return render_template('dashboard.html', **context)
