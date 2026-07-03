from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.decorators import roles_required
from app.models.visit import Visit
from app.models.patient import Patient
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole

visits_bp = Blueprint('visits', __name__, url_prefix='/visits')


@visits_bp.route('/')
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse', 'Receptionist')
def list_visits():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '').strip()
    search = request.args.get('q', '').strip()

    query = Visit.query.join(Patient).join(User, Visit.doctor_id == User.user_id)
    if status:
        query = query.filter(Visit.visit_status == status)
    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.patient_number.ilike(f'%{search}%'),
            )
        )
    query = query.order_by(Visit.visit_date.desc())
    visits = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('visits/list.html', visits=visits, status=status, search=search)


@visits_bp.route('/add', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse', 'Receptionist')
def add_visit():
    if request.method == 'POST':
        visit = Visit(
            patient_id=request.form['patient_id'],
            doctor_id=request.form['doctor_id'],
            visit_type=request.form.get('visit_type', 'OUTPATIENT'),
            visit_status='OPEN',
            chief_complaint=request.form.get('chief_complaint') or None,
            diagnosis=request.form.get('diagnosis') or None,
            treatment_plan=request.form.get('treatment_plan') or None,
            notes=request.form.get('notes') or None,
            height=request.form.get('height') or None,
            weight=request.form.get('weight') or None,
            temperature=request.form.get('temperature') or None,
            blood_pressure=request.form.get('blood_pressure') or None,
            pulse_rate=request.form.get('pulse_rate') or None,
            oxygen_level=request.form.get('oxygen_level') or None,
        )
        if request.form.get('admission_date'):
            visit.admission_date = request.form['admission_date']
        db.session.add(visit)
        db.session.commit()
        flash('Visit created successfully.', 'success')
        return redirect(url_for('visits.view_visit', visit_id=visit.visit_id))

    patients = Patient.query.order_by(Patient.first_name).all()
    doctors = User.query.join(
        UserRole, User.user_id == UserRole.user_id
    ).join(
        Role, UserRole.role_id == Role.role_id
    ).filter(
        Role.role_name == 'Doctor',
        User.status == 'ACTIVE'
    ).all()
    # Fallback: if no doctors with role, show all active users
    if not doctors:
        doctors = User.query.filter_by(status='ACTIVE').order_by(User.first_name).all()
    patient_id = request.args.get('patient_id', '')
    return render_template('visits/form.html', visit=None, patients=patients,
                           doctors=doctors, patient_id=patient_id)


@visits_bp.route('/<int:visit_id>')
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse', 'Receptionist')
def view_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    prescriptions = visit.prescriptions.all()
    lab_requests = visit.lab_requests.all()
    doctor_reports = visit.doctor_reports.all()
    return render_template('visits/detail.html', visit=visit,
                           prescriptions=prescriptions, lab_requests=lab_requests,
                           doctor_reports=doctor_reports)


@visits_bp.route('/<int:visit_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse', 'Receptionist')
def edit_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    if request.method == 'POST':
        visit.visit_type = request.form.get('visit_type', visit.visit_type)
        visit.visit_status = request.form.get('visit_status', visit.visit_status)
        visit.chief_complaint = request.form.get('chief_complaint') or None
        visit.diagnosis = request.form.get('diagnosis') or None
        visit.treatment_plan = request.form.get('treatment_plan') or None
        visit.notes = request.form.get('notes') or None
        visit.height = request.form.get('height') or None
        visit.weight = request.form.get('weight') or None
        visit.temperature = request.form.get('temperature') or None
        visit.blood_pressure = request.form.get('blood_pressure') or None
        visit.pulse_rate = request.form.get('pulse_rate') or None
        visit.oxygen_level = request.form.get('oxygen_level') or None
        if request.form.get('admission_date'):
            visit.admission_date = request.form['admission_date']
        if request.form.get('discharge_date'):
            visit.discharge_date = request.form['discharge_date']
        db.session.commit()
        flash('Visit updated.', 'success')
        return redirect(url_for('visits.view_visit', visit_id=visit.visit_id))

    patients = Patient.query.order_by(Patient.first_name).all()
    doctors = User.query.filter_by(status='ACTIVE').order_by(User.first_name).all()
    return render_template('visits/form.html', visit=visit, patients=patients, doctors=doctors, patient_id='')


@visits_bp.route('/<int:visit_id>/delete', methods=['POST'])
@login_required
@roles_required('Administrator', 'Doctor', 'Nurse', 'Receptionist')
def delete_visit(visit_id):
    visit = Visit.query.get_or_404(visit_id)
    db.session.delete(visit)
    db.session.commit()
    flash('Visit deleted.', 'success')
    return redirect(url_for('visits.list_visits'))
