from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.decorators import roles_required
from app.models.medicine import Medicine

medicines_bp = Blueprint('medicines', __name__, url_prefix='/medicines')


@medicines_bp.route('/')
@login_required
@roles_required('Administrator', 'Pharmacist', 'Inventory Manager', 'Doctor', 'Nurse')
def list_medicines():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()

    query = Medicine.query
    if search:
        query = query.filter(
            db.or_(
                Medicine.medicine_name.ilike(f'%{search}%'),
                Medicine.generic_name.ilike(f'%{search}%'),
                Medicine.category.ilike(f'%{search}%'),
            )
        )
    query = query.order_by(Medicine.medicine_name)
    medicines = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('medicines/list.html', medicines=medicines, search=search)


@medicines_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator', 'Pharmacist', 'Inventory Manager')
def add_medicine():
    if request.method == 'POST':
        medicine = Medicine(
            medicine_name=request.form['medicine_name'],
            generic_name=request.form.get('generic_name') or None,
            category=request.form.get('category') or None,
            dosage_form=request.form.get('dosage_form') or None,
            strength=request.form.get('strength') or None,
            manufacturer=request.form.get('manufacturer') or None,
            unit_price=request.form.get('unit_price') or None,
        )
        db.session.add(medicine)
        db.session.commit()
        flash(f'Medicine "{medicine.medicine_name}" added.', 'success')
        return redirect(url_for('medicines.list_medicines'))

    return render_template('medicines/form.html', medicine=None)


@medicines_bp.route('/<int:medicine_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator', 'Pharmacist', 'Inventory Manager')
def edit_medicine(medicine_id):
    medicine = Medicine.query.get_or_404(medicine_id)
    if request.method == 'POST':
        medicine.medicine_name = request.form['medicine_name']
        medicine.generic_name = request.form.get('generic_name') or None
        medicine.category = request.form.get('category') or None
        medicine.dosage_form = request.form.get('dosage_form') or None
        medicine.strength = request.form.get('strength') or None
        medicine.manufacturer = request.form.get('manufacturer') or None
        medicine.unit_price = request.form.get('unit_price') or None
        db.session.commit()
        flash(f'Medicine "{medicine.medicine_name}" updated.', 'success')
        return redirect(url_for('medicines.list_medicines'))

    return render_template('medicines/form.html', medicine=medicine)


@medicines_bp.route('/<int:medicine_id>/delete', methods=['POST'])
@login_required
@roles_required('Administrator', 'Pharmacist', 'Inventory Manager')
def delete_medicine(medicine_id):
    medicine = Medicine.query.get_or_404(medicine_id)
    name = medicine.medicine_name
    db.session.delete(medicine)
    db.session.commit()
    flash(f'Medicine "{name}" deleted.', 'success')
    return redirect(url_for('medicines.list_medicines'))
