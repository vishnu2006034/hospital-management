from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.models.doctor_report import DoctorReport
from app.models.visit import Visit
from app.models.patient import Patient

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')


@reports_bp.route('/')
@login_required
def list_reports():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()

    query = DoctorReport.query.join(Patient)
    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                DoctorReport.report_number.ilike(f'%{search}%'),
                DoctorReport.diagnosis.ilike(f'%{search}%'),
            )
        )
    query = query.order_by(DoctorReport.created_at.desc())
    reports = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('reports/list.html', reports=reports, search=search)


@reports_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_report():
    if request.method == 'POST':
        last = DoctorReport.query.order_by(DoctorReport.doctor_report_id.desc()).first()
        next_num = (last.doctor_report_id + 1) if last else 1
        report_number = f'DR{next_num:06d}'

        report = DoctorReport(
            visit_id=request.form['visit_id'],
            patient_id=request.form['patient_id'],
            doctor_id=current_user.user_id,
            report_number=report_number,
            chief_complaint=request.form.get('chief_complaint') or None,
            clinical_findings=request.form.get('clinical_findings') or None,
            diagnosis=request.form.get('diagnosis') or None,
            treatment_plan=request.form.get('treatment_plan') or None,
            prescribed_medicines=request.form.get('prescribed_medicines') or None,
            doctor_notes=request.form.get('doctor_notes') or None,
            follow_up_required=bool(request.form.get('follow_up_required')),
            follow_up_date=request.form.get('follow_up_date') or None,
            next_visit_reason=request.form.get('next_visit_reason') or None,
        )
        db.session.add(report)
        db.session.commit()
        flash(f'Report {report_number} created.', 'success')
        return redirect(url_for('reports.view_report', report_id=report.doctor_report_id))

    visit_id = request.args.get('visit_id', '')
    visits = Visit.query.order_by(Visit.visit_date.desc()).limit(50).all()
    patients = Patient.query.order_by(Patient.first_name).all()
    return render_template('reports/form.html', report=None, visits=visits,
                           patients=patients, visit_id=visit_id)


@reports_bp.route('/<int:report_id>')
@login_required
def view_report(report_id):
    report = DoctorReport.query.get_or_404(report_id)
    return render_template('reports/detail.html', report=report)


@reports_bp.route('/<int:report_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    report = DoctorReport.query.get_or_404(report_id)
    if request.method == 'POST':
        report.chief_complaint = request.form.get('chief_complaint') or None
        report.clinical_findings = request.form.get('clinical_findings') or None
        report.diagnosis = request.form.get('diagnosis') or None
        report.treatment_plan = request.form.get('treatment_plan') or None
        report.prescribed_medicines = request.form.get('prescribed_medicines') or None
        report.doctor_notes = request.form.get('doctor_notes') or None
        report.follow_up_required = bool(request.form.get('follow_up_required'))
        report.follow_up_date = request.form.get('follow_up_date') or None
        report.next_visit_reason = request.form.get('next_visit_reason') or None
        db.session.commit()
        flash('Report updated.', 'success')
        return redirect(url_for('reports.view_report', report_id=report.doctor_report_id))

    visits = Visit.query.order_by(Visit.visit_date.desc()).limit(50).all()
    patients = Patient.query.order_by(Patient.first_name).all()
    return render_template('reports/form.html', report=report, visits=visits,
                           patients=patients, visit_id='')
