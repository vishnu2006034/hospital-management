"""Main routes.

Dashboard and landing page routes.
"""

from typing import Dict, Any

from flask import Blueprint, render_template
from flask_login import login_required

from app.services.patient_service import PatientService
from app.services.staff_service import StaffService
from app.services.visit_service import VisitService

main_bp: Blueprint = Blueprint('main', __name__)


@main_bp.route('/')
def index() -> str:
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard() -> str:
    total_patients: int = PatientService.get_total_patients_count()
    active_doctors: int = StaffService.get_active_doctors_count()
    today_appointments: int = VisitService.get_today_appointments_count()
    
    # Calculate available beds (capacity of 100 minus active inpatient visits)
    active_admissions: int = VisitService.get_active_admissions_count()
    available_beds: int = max(0, 100 - active_admissions)

    context: Dict[str, Any] = {
        'total_patients': total_patients,
        'active_doctors': active_doctors,
        'today_appointments': today_appointments,
        'available_beds': available_beds,
    }
    return render_template('dashboard.html', **context)
