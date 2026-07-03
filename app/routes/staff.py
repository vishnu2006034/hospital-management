from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.decorators import roles_required
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')


@staff_bp.route('/')
@login_required
@roles_required('Administrator')
def list_staff():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()

    query = User.query
    if search:
        query = query.filter(
            db.or_(
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.employee_code.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
                User.department.ilike(f'%{search}%'),
            )
        )
    query = query.order_by(User.created_at.desc())
    staff = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('staff/list.html', staff=staff, search=search)


@staff_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator')
def add_staff():
    if request.method == 'POST':
        last = User.query.order_by(User.user_id.desc()).first()
        next_num = (last.user_id + 1) if last else 1
        employee_code = f'EMP{next_num:05d}'

        user = User(
            employee_code=employee_code,
            first_name=request.form['first_name'],
            last_name=request.form.get('last_name') or None,
            gender=request.form.get('gender') or None,
            dob=request.form.get('dob') or None,
            phone=request.form.get('phone') or None,
            email=request.form.get('email') or None,
            department=request.form.get('department') or None,
            specialization=request.form.get('specialization') or None,
            license_number=request.form.get('license_number') or None,
            joining_date=request.form.get('joining_date') or None,
            status=request.form.get('status', 'ACTIVE'),
        )
        user.set_password(request.form.get('password', 'changeme123'))
        db.session.add(user)
        db.session.flush()

        # Assign role
        role_id = request.form.get('role_id', type=int)
        if role_id:
            db.session.add(UserRole(user_id=user.user_id, role_id=role_id))

        db.session.commit()
        flash(f'Staff member {user.full_name} ({employee_code}) added.', 'success')
        return redirect(url_for('staff.view_staff', user_id=user.user_id))

    roles = Role.query.order_by(Role.role_name).all()
    return render_template('staff/form.html', user=None, roles=roles)


@staff_bp.route('/<int:user_id>')
@login_required
@roles_required('Administrator')
def view_staff(user_id):
    user = User.query.get_or_404(user_id)
    user_roles = UserRole.query.filter_by(user_id=user_id).all()
    return render_template('staff/detail.html', user=user, user_roles=user_roles)


@staff_bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator')
def edit_staff(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form.get('last_name') or None
        user.gender = request.form.get('gender') or None
        user.dob = request.form.get('dob') or None
        user.phone = request.form.get('phone') or None
        user.email = request.form.get('email') or None
        user.department = request.form.get('department') or None
        user.specialization = request.form.get('specialization') or None
        user.license_number = request.form.get('license_number') or None
        user.joining_date = request.form.get('joining_date') or None
        user.status = request.form.get('status', 'ACTIVE')
        if request.form.get('password'):
            user.set_password(request.form['password'])
        db.session.commit()
        flash(f'Staff member {user.full_name} updated.', 'success')
        return redirect(url_for('staff.view_staff', user_id=user.user_id))

    roles = Role.query.order_by(Role.role_name).all()
    return render_template('staff/form.html', user=user, roles=roles)


@staff_bp.route('/<int:user_id>/toggle-role', methods=['POST'])
@login_required
@roles_required('Administrator')
def toggle_role(user_id):
    role_id = request.form.get('role_id', type=int)
    if not role_id:
        flash('No role specified.', 'error')
        return redirect(url_for('staff.view_staff', user_id=user_id))

    existing = UserRole.query.filter_by(user_id=user_id, role_id=role_id).first()
    if existing:
        existing.is_active = not existing.is_active
        action = 'activated' if existing.is_active else 'deactivated'
    else:
        db.session.add(UserRole(user_id=user_id, role_id=role_id))
        action = 'assigned'

    db.session.commit()
    role = Role.query.get(role_id)
    flash(f'Role "{role.role_name}" {action}.', 'success')
    return redirect(url_for('staff.view_staff', user_id=user_id))
