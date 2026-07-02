from app import db


class DoctorReport(db.Model):
    """Doctor consultation report for a visit."""

    __tablename__ = 'doctor_report'

    doctor_report_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    visit_id = db.Column(
        db.BigInteger,
        db.ForeignKey('visits.visit_id', ondelete='CASCADE'),
        nullable=False,
    )
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
    report_number = db.Column(db.String(30), unique=True, nullable=False)
    chief_complaint = db.Column(db.Text)
    clinical_findings = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    treatment_plan = db.Column(db.Text)
    prescribed_medicines = db.Column(db.Text)
    doctor_notes = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_date = db.Column(db.Date)
    next_visit_reason = db.Column(db.Text)
    report_file = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ------ Relationships ------
    visit = db.relationship('Visit', back_populates='doctor_reports')
    patient = db.relationship('Patient', back_populates='doctor_reports')
    doctor = db.relationship('User', back_populates='doctor_reports')

    # ------ Indexes (match SQL) ------
    __table_args__ = (
        db.Index('idx_doctor_report_visit', 'visit_id'),
        db.Index('idx_doctor_report_patient', 'patient_id'),
        db.Index('idx_doctor_report_doctor', 'doctor_id'),
    )

    def __repr__(self):
        return f'<DoctorReport {self.report_number}>'
