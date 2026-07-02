from app import db


class Visit(db.Model):
    """Patient visit — outpatient consultation or inpatient admission."""

    __tablename__ = 'visits'

    visit_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    patient_id = db.Column(
        db.BigInteger,
        db.ForeignKey('patients.patient_id', ondelete='CASCADE'),
        nullable=False,
    )
    doctor_id = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
        nullable=False,
    )
    visit_type = db.Column(db.String(20), default='OUTPATIENT')
    visit_status = db.Column(db.String(20), default='OPEN')
    visit_date = db.Column(db.DateTime, server_default=db.func.now())
    admission_date = db.Column(db.DateTime)
    discharge_date = db.Column(db.DateTime)

    # Clinical
    chief_complaint = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment_plan = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Vitals
    height = db.Column(db.Numeric(5, 2))
    weight = db.Column(db.Numeric(5, 2))
    temperature = db.Column(db.Numeric(4, 1))
    blood_pressure = db.Column(db.String(20))
    pulse_rate = db.Column(db.Integer)
    oxygen_level = db.Column(db.Integer)

    # Timestamps (schema improvement)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ------ Relationships ------
    patient = db.relationship('Patient', back_populates='visits')
    doctor = db.relationship('User', back_populates='visits_as_doctor')
    prescriptions = db.relationship(
        'Prescription', back_populates='visit', lazy='dynamic', passive_deletes=True
    )
    lab_requests = db.relationship(
        'Laboratory', back_populates='visit', lazy='dynamic', passive_deletes=True
    )
    doctor_reports = db.relationship(
        'DoctorReport', back_populates='visit', lazy='dynamic', passive_deletes=True
    )

    # ------ Indexes (match SQL) ------
    __table_args__ = (
        db.Index('idx_visit_patient', 'patient_id'),
        db.Index('idx_visit_doctor', 'doctor_id'),
    )

    def __repr__(self):
        return f'<Visit {self.visit_id} type={self.visit_type} status={self.visit_status}>'
