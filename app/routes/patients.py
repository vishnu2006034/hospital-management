"""Patient routes."""

from typing import Dict

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required

from app.services.patient_service import PatientService

patients_bp: Blueprint = Blueprint('patients', __name__, url_prefix='/patients')


@patients_bp.route('/')
@login_required
def list_patients() -> str:
    """List patients with search and pagination."""
    page: int = request.args.get('page', 1, type=int)
    search: str = request.args.get('q', '').strip()
    patients = PatientService.get_all_patients(page=page, search=search)
    return render_template('patients/list.html', patients=patients, search=search)


@patients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_patient() -> str | Response:
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        patient = PatientService.create_patient(data)
        flash(f'Patient {patient.full_name} registered as {patient.patient_number}.', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient.patient_id))

    return render_template('patients/form.html', patient=None)


@patients_bp.route('/<int:patient_id>')
@login_required
def view_patient(patient_id: int) -> str:
    """View a single patient with recent visits."""
    patient = PatientService.get_patient_by_id(patient_id)
    visits = PatientService.get_patient_visits(patient)
    return render_template('patients/detail.html', patient=patient, visits=visits)


@patients_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id: int) -> str | Response:
    patient = PatientService.get_patient_by_id(patient_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        PatientService.update_patient(patient, data)
        flash(f'Patient {patient.full_name} updated.', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient.patient_id))

    return render_template('patients/form.html', patient=patient)


@patients_bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete_patient(patient_id: int) -> Response:
    patient = PatientService.get_patient_by_id(patient_id)
    name: str = patient.full_name
    PatientService.delete_patient(patient)
    flash(f'Patient {name} deleted.', 'success')
    return redirect(url_for('patients.list_patients'))
