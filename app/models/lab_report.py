from app import db


class LabReport(db.Model):
    """Individual test result within a laboratory request."""

    __tablename__ = 'lab_report'

    lab_report_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    lab_id = db.Column(
        db.BigInteger,
        db.ForeignKey('laboratory.lab_id', ondelete='CASCADE'),
        nullable=False,
    )
    test_id = db.Column(
        db.BigInteger,
        db.ForeignKey('lab_test_catalog.test_id'),
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
    result = db.Column(db.Text, nullable=False)
    unit = db.Column(db.String(30))
    reference_range = db.Column(db.String(100))
    is_abnormal = db.Column(db.Boolean, default=False)
    remarks = db.Column(db.Text)
    verified_by = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
    )
    verified_at = db.Column(db.DateTime)
    report_file = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # ------ Relationships ------
    laboratory = db.relationship('Laboratory', back_populates='reports')
    test = db.relationship('LabTestCatalog', back_populates='lab_reports')
    patient = db.relationship('Patient', back_populates='lab_reports')
    doctor = db.relationship('User', foreign_keys=[doctor_id])
    verifier = db.relationship('User', foreign_keys=[verified_by])

    # ------ Indexes (match SQL) ------
    __table_args__ = (
        db.Index('idx_lab_report_lab', 'lab_id'),
        db.Index('idx_lab_report_test', 'test_id'),
        db.Index('idx_lab_report_patient', 'patient_id'),
        db.Index('idx_lab_report_doctor', 'doctor_id'),
    )


