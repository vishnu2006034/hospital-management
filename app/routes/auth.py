from flask import Blueprint, render_template, redirect, url_for, flash, request

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if request.method == 'POST':
        # TODO: Implement login logic once User model is ready
        flash('Login functionality will be available once the database schema is set up.', 'info')
        return redirect(url_for('main.index'))
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if request.method == 'POST':
        # TODO: Implement registration logic once User model is ready
        flash('Registration functionality will be available once the database schema is set up.', 'info')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """User logout."""
    # TODO: Implement logout logic
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.index'))
