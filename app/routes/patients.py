from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.models.patient import Patient

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')


@patients_bp.route('/')
@login_required
def list_patients():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('q', '').strip()

    query = Patient.query
    if search:
        query = query.filter(
            db.or_(
                Patient.first_name.ilike(f'%{search}%'),
                Patient.last_name.ilike(f'%{search}%'),
                Patient.patient_number.ilike(f'%{search}%'),
                Patient.phone.ilike(f'%{search}%'),
            )
        )
    query = query.order_by(Patient.created_at.desc())
    patients = query.paginate(page=page, per_page=15, error_out=False)
    return render_template('patients/list.html', patients=patients, search=search)


@patients_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_patient():
    if request.method == 'POST':
        last = Patient.query.order_by(Patient.patient_id.desc()).first()
        next_num = (last.patient_id + 1) if last else 1
        patient_number = f'PAT{next_num:06d}'

        patient = Patient(
            patient_number=patient_number,
            first_name=request.form['first_name'],
            last_name=request.form.get('last_name') or None,
            gender=request.form.get('gender') or None,
            dob=request.form.get('dob') or None,
            blood_group=request.form.get('blood_group') or None,
            phone=request.form.get('phone') or None,
            email=request.form.get('email') or None,
            address=request.form.get('address') or None,
            emergency_contact_name=request.form.get('emergency_contact_name') or None,
            emergency_contact_phone=request.form.get('emergency_contact_phone') or None,
            allergies=request.form.get('allergies') or None,
            medical_history=request.form.get('medical_history') or None,
        )
        db.session.add(patient)
        db.session.commit()
        flash(f'Patient {patient.full_name} registered as {patient_number}.', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient.patient_id))

    return render_template('patients/form.html', patient=None)


@patients_bp.route('/<int:patient_id>')
@login_required
def view_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    visits = patient.visits.order_by(db.text('visit_date DESC')).limit(20).all()
    return render_template('patients/detail.html', patient=patient, visits=visits)


@patients_bp.route('/<int:patient_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    if request.method == 'POST':
        patient.first_name = request.form['first_name']
        patient.last_name = request.form.get('last_name') or None
        patient.gender = request.form.get('gender') or None
        patient.dob = request.form.get('dob') or None
        patient.blood_group = request.form.get('blood_group') or None
        patient.phone = request.form.get('phone') or None
        patient.email = request.form.get('email') or None
        patient.address = request.form.get('address') or None
        patient.emergency_contact_name = request.form.get('emergency_contact_name') or None
        patient.emergency_contact_phone = request.form.get('emergency_contact_phone') or None
        patient.allergies = request.form.get('allergies') or None
        patient.medical_history = request.form.get('medical_history') or None
        db.session.commit()
        flash(f'Patient {patient.full_name} updated.', 'success')
        return redirect(url_for('patients.view_patient', patient_id=patient.patient_id))

    return render_template('patients/form.html', patient=patient)


@patients_bp.route('/<int:patient_id>/delete', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    name = patient.full_name
    db.session.delete(patient)
    db.session.commit()
    flash(f'Patient {name} deleted.', 'success')
    return redirect(url_for('patients.list_patients'))
