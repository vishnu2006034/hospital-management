"""Staff routes."""

from typing import Dict, List

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required

from app.services.staff_service import StaffService

staff_bp: Blueprint = Blueprint('staff', __name__, url_prefix='/staff')


@staff_bp.route('/')
@login_required
def list_staff() -> str:
    """List staff with search and pagination."""
    page: int = request.args.get('page', 1, type=int)
    search: str = request.args.get('q', '').strip()
    staff = StaffService.get_all_staff(page=page, search=search)
    return render_template('staff/list.html', staff=staff, search=search)


@staff_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_staff() -> str | Response:
    """Add a new staff member."""
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        user = StaffService.create_staff(data)
        flash(f'Staff member {user.full_name} ({user.employee_code}) added.', 'success')
        return redirect(url_for('staff.view_staff', user_id=user.user_id))

    roles = StaffService.get_all_roles()
    return render_template('staff/form.html', user=None, roles=roles)


@staff_bp.route('/<int:user_id>')
@login_required
def view_staff(user_id: int) -> str:
    """View a single staff member with roles."""
    user = StaffService.get_user_by_id(user_id)
    user_roles = StaffService.get_user_roles(user_id)
    return render_template('staff/detail.html', user=user, user_roles=user_roles)


@staff_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_staff(user_id: int) -> str | Response:
    """Edit an existing staff member."""
    user = StaffService.get_user_by_id(user_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        StaffService.update_staff(user, data)
        flash(f'Staff member {user.full_name} updated.', 'success')
        return redirect(url_for('staff.view_staff', user_id=user.user_id))

    roles = StaffService.get_all_roles()
    return render_template('staff/form.html', user=user, roles=roles)


@staff_bp.route('/<int:user_id>/toggle-role', methods=['POST'])
@login_required
def toggle_role(user_id: int) -> Response:
    """Toggle a role for a staff member."""
    role_id = request.form.get('role_id', type=int)
    if not role_id:
        flash('No role specified.', 'error')
        return redirect(url_for('staff.view_staff', user_id=user_id))

    action: str = StaffService.toggle_role(user_id, role_id)
    role = StaffService.get_role_by_id(role_id)
    flash(f'Role "{role.role_name}" {action}.', 'success')
    return redirect(url_for('staff.view_staff', user_id=user_id))
