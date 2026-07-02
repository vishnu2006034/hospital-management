from flask import Blueprint, render_template
from flask_login import login_required
from datetime import date
from app import db
from app.models.patient import Patient
from app.models.user import User
from app.models.visit import Visit
from app.models.role import Role
from app.models.user_role import UserRole

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing / Dashboard page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard after login."""
    total_patients = Patient.query.count()
    
    # Query active doctors
    doctor_role = Role.query.filter_by(role_name='Doctor').first()
    if doctor_role:
        active_doctors = User.query.join(UserRole, User.user_id == UserRole.user_id).filter(
            UserRole.role_id == doctor_role.role_id,
            UserRole.is_active == True,
            User.status == 'ACTIVE'
        ).count()
    else:
        active_doctors = User.query.filter_by(status='ACTIVE').count()

    today = date.today()
    # Query today's visits
    today_appointments = Visit.query.filter(db.func.date(Visit.visit_date) == today).count()
    
    # Calculate available beds (Capacity of 100 minus active IPD visits)
    active_admissions = Visit.query.filter_by(visit_type='INPATIENT', visit_status='OPEN').count()
    available_beds = max(0, 100 - active_admissions)

    return render_template('dashboard.html',
                           total_patients=total_patients,
                           active_doctors=active_doctors,
                           today_appointments=today_appointments,
                           available_beds=available_beds)
