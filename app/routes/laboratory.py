"""Laboratory routes."""

from typing import Dict

from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_required, current_user

from app.services.laboratory_service import LaboratoryService

laboratory_bp: Blueprint = Blueprint('laboratory', __name__, url_prefix='/laboratory')


# LAB REQUESTS

@laboratory_bp.route('/')
@login_required
def list_lab() -> str:
    """List lab requests with search, status filter, and pagination."""
    page: int = request.args.get('page', 1, type=int)
    status: str = request.args.get('status', '').strip()
    search: str = request.args.get('q', '').strip()
    labs = LaboratoryService.get_all_lab_requests(page=page, status=status, search=search)
    return render_template('laboratory/list.html', labs=labs, status=status, search=search)


@laboratory_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_lab() -> str | Response:
    """Add a new lab request."""
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        lab = LaboratoryService.create_lab_request(data, requested_by=current_user.user_id)
        flash('Lab request created.', 'success')
        return redirect(url_for('laboratory.view_lab', lab_id=lab.lab_id))

    visit_id: str = request.args.get('visit_id', '')
    visits = LaboratoryService.get_recent_visits()
    patients = LaboratoryService.get_all_patients()
    technicians = LaboratoryService.get_all_technicians()
    return render_template('laboratory/form.html', lab=None, visits=visits,
                           patients=patients, technicians=technicians, visit_id=visit_id)


@laboratory_bp.route('/<int:lab_id>')
@login_required
def view_lab(lab_id: int) -> str:
    """View a single lab request with reports."""
    lab = LaboratoryService.get_lab_by_id(lab_id)
    reports = LaboratoryService.get_lab_reports(lab)
    return render_template('laboratory/detail.html', lab=lab, reports=reports)


@laboratory_bp.route('/<int:lab_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lab(lab_id: int) -> str | Response:
    """Edit an existing lab request."""
    lab = LaboratoryService.get_lab_by_id(lab_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        LaboratoryService.update_lab_request(lab, data)
        flash('Lab request updated.', 'success')
        return redirect(url_for('laboratory.view_lab', lab_id=lab.lab_id))

    technicians = LaboratoryService.get_all_technicians()
    visits = LaboratoryService.get_recent_visits()
    patients = LaboratoryService.get_all_patients()
    return render_template('laboratory/form.html', lab=lab, visits=visits,
                           patients=patients, technicians=technicians, visit_id='')


# LAB REPORTS

@laboratory_bp.route('/<int:lab_id>/report/add', methods=['GET', 'POST'])
@login_required
def add_report(lab_id: int) -> str | Response:
    """Add a report to a lab request."""
    lab = LaboratoryService.get_lab_by_id(lab_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        report = LaboratoryService.add_report(lab, data)
        flash(f'Lab report {report.report_number} added.', 'success')
        return redirect(url_for('laboratory.view_lab', lab_id=lab.lab_id))

    from app.models.lab_test_catalog import LabTestCatalog
    tests = LabTestCatalog.query.filter_by(is_active=True).order_by(
        LabTestCatalog.test_name
    ).all()
    return render_template('laboratory/report_form.html', lab=lab, report=None, tests=tests)


# LAB TEST CATALOG

@laboratory_bp.route('/catalog')
@login_required
def list_catalog() -> str:
    """List lab test catalog with search and pagination."""
    page: int = request.args.get('page', 1, type=int)
    search: str = request.args.get('q', '').strip()
    tests = LaboratoryService.get_all_catalog_tests(page=page, search=search)
    return render_template('laboratory/catalog_list.html', tests=tests, search=search)


@laboratory_bp.route('/catalog/add', methods=['GET', 'POST'])
@login_required
def add_catalog() -> str | Response:
    """Add a new catalog test."""
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        test = LaboratoryService.create_catalog_test(data)
        flash(f'Test "{test.test_name}" added to catalog.', 'success')
        return redirect(url_for('laboratory.list_catalog'))

    return render_template('laboratory/catalog_form.html', test=None)


@laboratory_bp.route('/catalog/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_catalog(test_id: int) -> str | Response:
    """Edit an existing catalog test."""
    test = LaboratoryService.get_catalog_test_by_id(test_id)
    if request.method == 'POST':
        data: Dict[str, str] = request.form.to_dict()
        LaboratoryService.update_catalog_test(test, data)
        flash(f'Test "{test.test_name}" updated.', 'success')
        return redirect(url_for('laboratory.list_catalog'))

    return render_template('laboratory/catalog_form.html', test=test)
