"""Report routes."""

from typing import Dict

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user

from app.services.report_service import ReportService

reports_bp: Blueprint = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def list_reports() -> str:
    """List doctor reports with search and pagination."""
    page: int = request.args.get('page', 1, type=int)
    search: str = request.args.get('q', '').strip()
    reports = ReportService.get_all_reports(page=page, search=search)
    return render_template('reports/list.html', reports=reports, search=search)


@reports_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_report() -> str | Response:
    """Add a new doctor report."""
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        report = ReportService.create_report(data, doctor_id=current_user.user_id)
        flash(f'Report {report.report_number} created.', 'success')
        return redirect(url_for('reports.view_report', report_id=report.doctor_report_id))

    visit_id: str = request.args.get('visit_id', '')
    visits = ReportService.get_recent_visits()
    patients = ReportService.get_all_patients()
    return render_template('reports/form.html', report=None, visits=visits,
                           patients=patients, visit_id=visit_id)


@reports_bp.route('/<report_id>')
@login_required
def view_report(report_id: str) -> str:
    """View a single doctor report."""
    report = ReportService.get_report_by_id(report_id)
    return render_template('reports/detail.html', report=report)


@reports_bp.route('/<report_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_report(report_id: str) -> str | Response:
    """Edit an existing doctor report."""
    report = ReportService.get_report_by_id(report_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        ReportService.update_report(report_id, data)
        flash('Report updated.', 'success')
        return redirect(url_for('reports.view_report', report_id=report.doctor_report_id))

    visits = ReportService.get_recent_visits()
    patients = ReportService.get_all_patients()
    return render_template('reports/form.html', report=report, visits=visits,
                           patients=patients, visit_id='')
