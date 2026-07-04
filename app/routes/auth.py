"""Authentication routes."""

from typing import Dict, List, Optional

from flask import Blueprint, render_template, redirect, url_for, flash, request, Response
from flask_login import login_required, current_user

from app.services.auth_service import AuthService

auth_bp: Blueprint = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email: str = request.form.get('email', '').strip()
        password: str = request.form.get('password', '')
        remember: bool = bool(request.form.get('remember_me'))

        user = AuthService.authenticate_user(email, password)

        if user is None:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

        if user.status != 'ACTIVE':
            flash('Your account is not active. Please contact the administrator.', 'warning')
            return redirect(url_for('auth.login'))

        AuthService.login(user, remember=remember)
        flash(f'Welcome back, {user.full_name}!', 'success')

        next_page: Optional[str] = request.args.get('next')
        return redirect(next_page or url_for('main.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register() -> str | Response:
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        data: Dict[str, str] = {
            'first_name': request.form.get('first_name', '').strip(),
            'last_name': request.form.get('last_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'role': request.form.get('role', ''),
            'password': request.form.get('password', ''),
            'confirm_password': request.form.get('confirm_password', ''),
        }

        errors: List[str] = AuthService.validate_registration(data)
        if errors:
            for err in errors:
                flash(err, 'error')
            return redirect(url_for('auth.register'))

        AuthService.create_user(data)
        flash('Account created successfully! Please sign in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout() -> Response:
    AuthService.logout()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))
