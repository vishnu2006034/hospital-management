"""Prescription routes."""

from typing import Dict

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user

from app.services.prescription_service import PrescriptionService

prescriptions_bp: Blueprint = Blueprint('prescriptions', __name__, url_prefix='/prescriptions')


@prescriptions_bp.route('/')
@login_required
def list_prescriptions() -> str:
    """List prescriptions with search and pagination."""
    page: int = request.args.get('page', 1, type=int)
    search: str = request.args.get('q', '').strip()
    prescriptions = PrescriptionService.get_all_prescriptions(page=page, search=search)
    return render_template('prescriptions/list.html', prescriptions=prescriptions, search=search)


@prescriptions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_prescription() -> str | Response:
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        PrescriptionService.create_prescription(data, prescribed_by=current_user.user_id)
        flash('Prescription added.', 'success')
        return redirect(url_for('visits.view_visit', visit_id=data['visit_id']))

    visit_id: str = request.args.get('visit_id', '')
    visits = PrescriptionService.get_recent_visits()
    inventory = PrescriptionService.get_available_inventory()
    return render_template('prescriptions/form.html', prescription=None,
                           visits=visits, inventory=inventory, visit_id=visit_id)


@prescriptions_bp.route('/<int:prescription_id>/delete', methods=['POST'])
@login_required
def delete_prescription(prescription_id: int) -> Response:
    prescription = PrescriptionService.get_prescription_by_id(prescription_id)
    visit_id: int = prescription.visit_id
    PrescriptionService.delete_prescription(prescription_id)
    flash('Prescription removed.', 'success')
    return redirect(url_for('visits.view_visit', visit_id=visit_id))
