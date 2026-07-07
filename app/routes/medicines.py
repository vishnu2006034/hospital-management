"""Medicine routes."""

from typing import Dict

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required

from app.services.medicine_service import MedicineService

medicines_bp: Blueprint = Blueprint('medicines', __name__, url_prefix='/medicines')


@medicines_bp.route('/')
@login_required
def list_medicines() -> str:
    """List medicines with search and pagination."""
    page: int = request.args.get('page', 1, type=int)
    search: str = request.args.get('q', '').strip()
    medicines = MedicineService.get_all_medicines(page=page, search=search)
    return render_template('medicines/list.html', medicines=medicines, search=search)


@medicines_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_medicine() -> str | Response:
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        medicine = MedicineService.create_medicine(data)
        flash(f'Medicine "{medicine.medicine_name}" added.', 'success')
        return redirect(url_for('medicines.list_medicines'))

    return render_template('medicines/form.html', medicine=None)


@medicines_bp.route('/<int:medicine_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medicine(medicine_id: int) -> str | Response:
    medicine = MedicineService.get_medicine_by_id(medicine_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        MedicineService.update_medicine(medicine_id, data)
        flash(f'Medicine "{medicine.medicine_name}" updated.', 'success')
        return redirect(url_for('medicines.list_medicines'))

    return render_template('medicines/form.html', medicine=medicine)


@medicines_bp.route('/<int:medicine_id>/delete', methods=['POST'])
@login_required
def delete_medicine(medicine_id: int) -> Response:
    medicine = MedicineService.get_medicine_by_id(medicine_id)
    name: str = medicine.medicine_name
    MedicineService.delete_medicine(medicine_id)
    flash(f'Medicine "{name}" deleted.', 'success')
    return redirect(url_for('medicines.list_medicines'))
