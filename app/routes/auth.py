from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app import db
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember_me'))

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

        if user.status != 'ACTIVE':
            flash('Your account is not active. Please contact the administrator.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=remember)
        flash(f'Welcome back, {user.full_name}!', 'success')

        # Redirect to the page the user was trying to access, or dashboard
        next_page = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        role_name = request.form.get('role', '')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation
        errors = []
        if not first_name:
            errors.append('First name is required.')
        if not email:
            errors.append('Email is required.')
        if not password:
            errors.append('Password is required.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters.')
        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')

        if errors:
            for err in errors:
                flash(err, 'error')
            return redirect(url_for('auth.register'))

        # Generate employee code (auto-increment pattern)
        last_user = User.query.order_by(User.user_id.desc()).first()
        next_num = (last_user.user_id + 1) if last_user else 1
        employee_code = f'EMP{next_num:05d}'

        # Create user
        user = User(
            employee_code=employee_code,
            first_name=first_name,
            last_name=last_name or None,
            email=email,
            status='ACTIVE',
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Assign role if provided
        if role_name:
            role_map = {
                'admin': 'Administrator',
                'doctor': 'Doctor',
                'nurse': 'Nurse',
                'receptionist': 'Receptionist',
                'pharmacist': 'Pharmacist',
                'lab_technician': 'Lab Technician',
            }
            db_role_name = role_map.get(role_name.lower(), role_name)
            role = Role.query.filter_by(role_name=db_role_name).first()
            if role:
                db.session.add(
                    UserRole(user_id=user.user_id, role_id=role.role_id)
                )

        db.session.commit()
        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))
