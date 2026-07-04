"""Visit routes."""

from typing import Dict

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required

from app.services.visit_service import VisitService

visits_bp: Blueprint = Blueprint('visits', __name__, url_prefix='/visits')


@visits_bp.route('/')
@login_required
def list_visits() -> str:
    """List visits with search and pagination."""
    page: int = request.args.get('page', 1, type=int)
    status: str = request.args.get('status', '').strip()
    search: str = request.args.get('q', '').strip()
    visits = VisitService.get_all_visits(page=page, status=status, search=search)
    return render_template('visits/list.html', visits=visits, status=status, search=search)


@visits_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_visit() -> str | Response:
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        admission_date = request.form.get('admission_date')
        visit = VisitService.create_visit(data, admission_date=admission_date)
        flash('Visit created successfully.', 'success')
        return redirect(url_for('visits.view_visit', visit_id=visit.visit_id))

    patients = VisitService.get_all_patients()
    doctors = VisitService.get_all_doctors()
    patient_id: str = request.args.get('patient_id', '')
    return render_template('visits/form.html', visit=None, patients=patients,
                           doctors=doctors, patient_id=patient_id)


@visits_bp.route('/<int:visit_id>')
@login_required
def view_visit(visit_id: int) -> str:
    """View a single visit with related entities."""
    visit = VisitService.get_visit_by_id(visit_id)
    details = VisitService.get_visit_details(visit)
    return render_template('visits/detail.html', visit=visit,
                           prescriptions=details['prescriptions'],
                           lab_requests=details['lab_requests'],
                           doctor_reports=details['doctor_reports'])


@visits_bp.route('/<int:visit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_visit(visit_id: int) -> str | Response:
    visit = VisitService.get_visit_by_id(visit_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        admission_date = request.form.get('admission_date')
        discharge_date = request.form.get('discharge_date')
        VisitService.update_visit(visit, data, admission_date=admission_date,
                                  discharge_date=discharge_date)
        flash('Visit updated.', 'success')
        return redirect(url_for('visits.view_visit', visit_id=visit.visit_id))

    patients = VisitService.get_all_patients()
    doctors = VisitService.get_all_doctors()
    return render_template('visits/form.html', visit=visit, patients=patients,
                           doctors=doctors, patient_id='')


@visits_bp.route('/<int:visit_id>/delete', methods=['POST'])
@login_required
def delete_visit(visit_id: int) -> Response:
    visit = VisitService.get_visit_by_id(visit_id)
    VisitService.delete_visit(visit)
    flash('Visit deleted.', 'success')
    return redirect(url_for('visits.list_visits'))
