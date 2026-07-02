from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Landing / Dashboard page."""
    return render_template('index.html')


@main_bp.route('/dashboard')
def dashboard():
    """Main dashboard after login."""
    return render_template('dashboard.html')
