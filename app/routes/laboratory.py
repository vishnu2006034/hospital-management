from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.decorators import roles_required
from app.models.laboratory import Laboratory
from app.models.lab_report import LabReport
from app.models.lab_test_catalog import LabTestCatalog
from app.models.patient import Patient
from app.models.visit import Visit
from app.models.user import User

laboratory_bp = Blueprint('laboratory', __name__, url_prefix='/laboratory')


# ==================== LAB REQUESTS ====================

@laboratory_bp.route('/')
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse', 'Lab Technician')
def list_lab():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '').strip()
    search = request.args.get('q', '').strip()

    query = Laboratory.query.join(Patient)
    if status:
        query = query.filter(Laboratory.test_status == status)
    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.patient_number.ilike(f'%{search}%'),
            )
        )
    query = query.order_by(Laboratory.created_at.desc())
    labs = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('laboratory/list.html', labs=labs, status=status, search=search)


@laboratory_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse')
def add_lab():
    if request.method == 'POST':
        lab = Laboratory(
            visit_id=request.form['visit_id'],
            patient_id=request.form['patient_id'],
            requested_by=current_user.user_id,
            lab_technician_id=request.form.get('lab_technician_id', type=int) or None,
            priority=request.form.get('priority', 'NORMAL'),
            sample_type=request.form.get('sample_type') or None,
            remarks=request.form.get('remarks') or None,
        )
        db.session.add(lab)
        db.session.commit()
        flash('Lab request created.', 'success')
        return redirect(url_for('laboratory.view_lab', lab_id=lab.lab_id))

    visit_id = request.args.get('visit_id', '')
    visits = Visit.query.order_by(Visit.visit_date.desc()).limit(50).all()
    patients = Patient.query.order_by(Patient.first_name).all()
    technicians = User.query.filter_by(status='ACTIVE').order_by(User.first_name).all()
    return render_template('laboratory/form.html', lab=None, visits=visits,
                           patients=patients, technicians=technicians, visit_id=visit_id)


@laboratory_bp.route('/<int:lab_id>')
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse', 'Lab Technician')
def view_lab(lab_id):
    lab = Laboratory.query.get_or_404(lab_id)
    reports = lab.reports.all()
    return render_template('laboratory/detail.html', lab=lab, reports=reports)


@laboratory_bp.route('/<int:lab_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse')
def edit_lab(lab_id):
    lab = Laboratory.query.get_or_404(lab_id)
    if request.method == 'POST':
        lab.test_status = request.form.get('test_status', lab.test_status)
        lab.priority = request.form.get('priority', lab.priority)
        lab.lab_technician_id = request.form.get('lab_technician_id', type=int) or None
        lab.sample_type = request.form.get('sample_type') or None
        lab.remarks = request.form.get('remarks') or None
        if request.form.get('sample_collected_at'):
            lab.sample_collected_at = request.form['sample_collected_at']
        if lab.test_status == 'COMPLETED' and not lab.completed_at:
            from datetime import datetime
            lab.completed_at = datetime.utcnow()
        db.session.commit()
        flash('Lab request updated.', 'success')
        return redirect(url_for('laboratory.view_lab', lab_id=lab.lab_id))

    technicians = User.query.filter_by(status='ACTIVE').order_by(User.first_name).all()
    visits = Visit.query.order_by(Visit.visit_date.desc()).limit(50).all()
    patients = Patient.query.order_by(Patient.first_name).all()
    return render_template('laboratory/form.html', lab=lab, visits=visits,
                           patients=patients, technicians=technicians, visit_id='')


# ==================== LAB REPORTS ====================

@laboratory_bp.route('/<int:lab_id>/report/add', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator', 'Lab Technician')
def add_report(lab_id):
    lab = Laboratory.query.get_or_404(lab_id)
    if request.method == 'POST':
        last = LabReport.query.order_by(LabReport.lab_report_id.desc()).first()
        next_num = (last.lab_report_id + 1) if last else 1
        report_number = f'LR{next_num:06d}'

        report = LabReport(
            lab_id=lab.lab_id,
            test_id=request.form['test_id'],
            patient_id=lab.patient_id,
            doctor_id=lab.requested_by,
            report_number=report_number,
            result=request.form['result'],
            unit=request.form.get('unit') or None,
            reference_range=request.form.get('reference_range') or None,
            is_abnormal=bool(request.form.get('is_abnormal')),
            remarks=request.form.get('remarks') or None,
        )
        db.session.add(report)
        db.session.commit()
        flash(f'Lab report {report_number} added.', 'success')
        return redirect(url_for('laboratory.view_lab', lab_id=lab.lab_id))

    tests = LabTestCatalog.query.filter_by(is_active=True).order_by(LabTestCatalog.test_name).all()
    return render_template('laboratory/report_form.html', lab=lab, report=None, tests=tests)


# ==================== LAB TEST CATALOG ====================

@laboratory_bp.route('/catalog')
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse', 'Lab Technician')
def list_catalog():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()

    query = LabTestCatalog.query
    if search:
        query = query.filter(
            db.or_(
                LabTestCatalog.test_name.ilike(f'%{search}%'),
                LabTestCatalog.test_code.ilike(f'%{search}%'),
                LabTestCatalog.category.ilike(f'%{search}%'),
            )
        )
    query = query.order_by(LabTestCatalog.test_name)
    tests = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('laboratory/catalog_list.html', tests=tests, search=search)


@laboratory_bp.route('/catalog/add', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator', 'Lab Technician')
def add_catalog():
    if request.method == 'POST':
        test = LabTestCatalog(
            test_code=request.form['test_code'],
            test_name=request.form['test_name'],
            category=request.form.get('category') or None,
            sample_type=request.form.get('sample_type') or None,
            unit=request.form.get('unit') or None,
            reference_range=request.form.get('reference_range') or None,
            normal_min=request.form.get('normal_min') or None,
            normal_max=request.form.get('normal_max') or None,
            default_price=request.form.get('default_price') or None,
            description=request.form.get('description') or None,
        )
        db.session.add(test)
        db.session.commit()
        flash(f'Test "{test.test_name}" added to catalog.', 'success')
        return redirect(url_for('laboratory.list_catalog'))

    return render_template('laboratory/catalog_form.html', test=None)


@laboratory_bp.route('/catalog/<int:test_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator', 'Lab Technician')
def edit_catalog(test_id):
    test = LabTestCatalog.query.get_or_404(test_id)
    if request.method == 'POST':
        test.test_code = request.form['test_code']
        test.test_name = request.form['test_name']
        test.category = request.form.get('category') or None
        test.sample_type = request.form.get('sample_type') or None
        test.unit = request.form.get('unit') or None
        test.reference_range = request.form.get('reference_range') or None
        test.normal_min = request.form.get('normal_min') or None
        test.normal_max = request.form.get('normal_max') or None
        test.default_price = request.form.get('default_price') or None
        test.description = request.form.get('description') or None
        test.is_active = bool(request.form.get('is_active'))
        db.session.commit()
        flash(f'Test "{test.test_name}" updated.', 'success')
        return redirect(url_for('laboratory.list_catalog'))

    return render_template('laboratory/catalog_form.html', test=test)
