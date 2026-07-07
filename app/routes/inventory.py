"""Inventory routes."""

from typing import Dict

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user

from app.services.inventory_service import InventoryService

inventory_bp: Blueprint = Blueprint('inventory', __name__, url_prefix='/inventory')


@inventory_bp.route('/')
@login_required
def list_inventory() -> str:
    """List inventory items with search, filter, and pagination."""
    page: int = request.args.get('page', 1, type=int)
    search: str = request.args.get('q', '').strip()
    filter_type: str = request.args.get('filter', '')
    inventory = InventoryService.get_all_inventory(
        page=page, search=search, filter_type=filter_type
    )
    return render_template('inventory/list.html', inventory=inventory,
                           search=search, filter_type=filter_type)


@inventory_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_inventory() -> str | Response:
    """Add a new inventory item."""
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        InventoryService.create_inventory(data, performed_by=current_user.user_id)
        flash('Inventory batch added.', 'success')
        return redirect(url_for('inventory.list_inventory'))

    medicines = InventoryService.get_all_medicines()
    return render_template('inventory/form.html', inv=None, medicines=medicines)


@inventory_bp.route('/<int:inventory_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inventory(inventory_id: int) -> str | Response:
    """Edit an existing inventory item."""
    inv = InventoryService.get_inventory_by_id(inventory_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        InventoryService.update_inventory(inventory_id, data)
        flash('Inventory batch updated.', 'success')
        return redirect(url_for('inventory.list_inventory'))

    medicines = InventoryService.get_all_medicines()
    return render_template('inventory/form.html', inv=inv, medicines=medicines)


@inventory_bp.route('/<int:inventory_id>/transaction', methods=['GET', 'POST'])
@login_required
def add_transaction(inventory_id: int) -> str | Response:
    """Add a stock transaction to an inventory item."""
    inv = InventoryService.get_inventory_by_id(inventory_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        InventoryService.add_transaction(inventory_id, data, performed_by=current_user.user_id)
        # Re-fetch inventory to get correct updated quantity
        inv = InventoryService.get_inventory_by_id(inventory_id)
        flash(f'Transaction recorded. Stock: {inv.quantity_in_stock}', 'success')
        return redirect(url_for('inventory.list_inventory'))

    transactions = InventoryService.get_recent_transactions(inventory_id)
    return render_template('inventory/transaction.html', inv=inv, transactions=transactions)
