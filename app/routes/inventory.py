from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.inventory import Inventory
from app.models.inventory_transaction import InventoryTransaction
from app.models.medicine import Medicine

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')


@inventory_bp.route('/')
@login_required
def list_inventory():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()
    filter_type = request.args.get('filter', '')

    query = Inventory.query.join(Medicine)
    if search:
        query = query.filter(
            db.or_(
                Medicine.medicine_name.ilike(f'%{search}%'),
                Inventory.batch_number.ilike(f'%{search}%'),
                Inventory.supplier.ilike(f'%{search}%'),
            )
        )
    if filter_type == 'low':
        query = query.filter(Inventory.quantity_in_stock <= Inventory.minimum_stock)
    elif filter_type == 'expired':
        from datetime import date
        query = query.filter(Inventory.expiry_date < date.today())

    query = query.order_by(Medicine.medicine_name, Inventory.batch_number)
    inventory = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('inventory/list.html', inventory=inventory,
                           search=search, filter_type=filter_type)


@inventory_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_inventory():
    if request.method == 'POST':
        inv = Inventory(
            medicine_id=request.form['medicine_id'],
            batch_number=request.form['batch_number'],
            expiry_date=request.form.get('expiry_date') or None,
            purchase_price=request.form.get('purchase_price') or None,
            selling_price=request.form.get('selling_price') or None,
            quantity_in_stock=request.form.get('quantity_in_stock', 0, type=int),
            minimum_stock=request.form.get('minimum_stock', 0, type=int),
            supplier=request.form.get('supplier') or None,
        )
        db.session.add(inv)
        db.session.flush()

        # Record initial stock transaction
        if inv.quantity_in_stock > 0:
            txn = InventoryTransaction(
                inventory_id=inv.inventory_id,
                transaction_type='IN',
                quantity=inv.quantity_in_stock,
                reference_type='PURCHASE',
                performed_by=current_user.user_id,
                remarks='Initial stock entry',
            )
            db.session.add(txn)

        db.session.commit()
        flash(f'Inventory batch "{inv.batch_number}" added.', 'success')
        return redirect(url_for('inventory.list_inventory'))

    medicines = Medicine.query.order_by(Medicine.medicine_name).all()
    return render_template('inventory/form.html', inv=None, medicines=medicines)


@inventory_bp.route('/<int:inventory_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inventory(inventory_id):
    inv = Inventory.query.get_or_404(inventory_id)
    if request.method == 'POST':
        inv.batch_number = request.form['batch_number']
        inv.expiry_date = request.form.get('expiry_date') or None
        inv.purchase_price = request.form.get('purchase_price') or None
        inv.selling_price = request.form.get('selling_price') or None
        inv.minimum_stock = request.form.get('minimum_stock', 0, type=int)
        inv.supplier = request.form.get('supplier') or None
        db.session.commit()
        flash('Inventory batch updated.', 'success')
        return redirect(url_for('inventory.list_inventory'))

    medicines = Medicine.query.order_by(Medicine.medicine_name).all()
    return render_template('inventory/form.html', inv=inv, medicines=medicines)


@inventory_bp.route('/<int:inventory_id>/transaction', methods=['GET', 'POST'])
@login_required
def add_transaction(inventory_id):
    inv = Inventory.query.get_or_404(inventory_id)
    if request.method == 'POST':
        txn_type = request.form['transaction_type']
        qty = int(request.form['quantity'])

        txn = InventoryTransaction(
            inventory_id=inv.inventory_id,
            transaction_type=txn_type,
            quantity=qty,
            reference_type=request.form.get('reference_type') or None,
            reference_id=request.form.get('reference_id', type=int) or None,
            performed_by=current_user.user_id,
            remarks=request.form.get('remarks') or None,
        )
        db.session.add(txn)

        # Update stock
        if txn_type == 'IN':
            inv.quantity_in_stock += qty
        elif txn_type == 'OUT':
            inv.quantity_in_stock = max(0, inv.quantity_in_stock - qty)
        elif txn_type == 'ADJUSTMENT':
            inv.quantity_in_stock = qty  # set absolute value

        db.session.commit()
        flash(f'Transaction recorded. Stock: {inv.quantity_in_stock}', 'success')
        return redirect(url_for('inventory.list_inventory'))

    transactions = inv.transactions.order_by(
        InventoryTransaction.transaction_date.desc()
    ).limit(20).all()
    return render_template('inventory/transaction.html', inv=inv, transactions=transactions)
