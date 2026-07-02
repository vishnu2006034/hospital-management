from app import db


class Patient(db.Model):
    """Patient demographics and medical background."""

    __tablename__ = 'patients'

    patient_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    patient_number = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    dob = db.Column(db.Date)
    blood_group = db.Column(db.String(5))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))
    address = db.Column(db.Text)
    emergency_contact_name = db.Column(db.String(100))
    emergency_contact_phone = db.Column(db.String(15))
    allergies = db.Column(db.Text)
    medical_history = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ------ Relationships ------
    visits = db.relationship('Visit', back_populates='patient', lazy='dynamic')
    lab_requests = db.relationship('Laboratory', back_populates='patient', lazy='dynamic')
    lab_reports = db.relationship('LabReport', back_populates='patient', lazy='dynamic')
    doctor_reports = db.relationship('DoctorReport', back_populates='patient', lazy='dynamic')

    @property
    def full_name(self):
        parts = [self.first_name, self.last_name]
        return ' '.join(p for p in parts if p)

    def __repr__(self):
        return f'<Patient {self.patient_number} – {self.full_name}>'
