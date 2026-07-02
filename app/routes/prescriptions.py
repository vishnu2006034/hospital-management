from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.prescription import Prescription
from app.models.visit import Visit
from app.models.inventory import Inventory
from app.models.medicine import Medicine

prescriptions_bp = Blueprint('prescriptions', __name__, url_prefix='/prescriptions')


@prescriptions_bp.route('/')
@login_required
def list_prescriptions():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()

    query = Prescription.query.join(Visit).join(
        Inventory, Prescription.inventory_id == Inventory.inventory_id
    ).join(Medicine, Inventory.medicine_id == Medicine.medicine_id)

    if search:
        query = query.filter(
            db.or_(
                Medicine.medicine_name.ilike(f'%{search}%'),
                Medicine.generic_name.ilike(f'%{search}%'),
            )
        )
    query = query.order_by(Prescription.created_at.desc())
    prescriptions = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('prescriptions/list.html', prescriptions=prescriptions, search=search)


@prescriptions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_prescription():
    if request.method == 'POST':
        prescription = Prescription(
            visit_id=request.form['visit_id'],
            inventory_id=request.form['inventory_id'],
            prescribed_by=current_user.user_id,
            dosage=request.form.get('dosage') or None,
            frequency=request.form.get('frequency') or None,
            duration=request.form.get('duration') or None,
            quantity=request.form.get('quantity', type=int) or None,
            instructions=request.form.get('instructions') or None,
        )
        db.session.add(prescription)

        # Deduct stock
        if prescription.quantity:
            inv = Inventory.query.get(int(request.form['inventory_id']))
            if inv:
                inv.quantity_in_stock = max(0, inv.quantity_in_stock - prescription.quantity)

        db.session.commit()
        flash('Prescription added.', 'success')
        return redirect(url_for('visits.view_visit', visit_id=request.form['visit_id']))

    visit_id = request.args.get('visit_id', '')
    visits = Visit.query.order_by(Visit.visit_date.desc()).limit(50).all()
    inventory = Inventory.query.join(Medicine).filter(
        Inventory.quantity_in_stock > 0
    ).order_by(Medicine.medicine_name).all()
    return render_template('prescriptions/form.html', prescription=None,
                           visits=visits, inventory=inventory, visit_id=visit_id)


@prescriptions_bp.route('/<int:prescription_id>/delete', methods=['POST'])
@login_required
def delete_prescription(prescription_id):
    prescription = Prescription.query.get_or_404(prescription_id)
    visit_id = prescription.visit_id
    db.session.delete(prescription)
    db.session.commit()
    flash('Prescription removed.', 'success')
    return redirect(url_for('visits.view_visit', visit_id=visit_id))
