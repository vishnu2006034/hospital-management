from app import db


class Laboratory(db.Model):
    """Laboratory request — groups one or more test results."""

    __tablename__ = 'laboratory'

    lab_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
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
    requested_by = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
        nullable=False,
    )
    lab_technician_id = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
    )
    priority = db.Column(db.String(20), default='NORMAL')
    sample_type = db.Column(db.String(50))
    sample_collected_at = db.Column(db.DateTime)
    test_status = db.Column(db.String(30), default='PENDING')
    remarks = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    completed_at = db.Column(db.DateTime)

    # ------ Relationships ------
    visit = db.relationship('Visit', back_populates='lab_requests')
    patient = db.relationship('Patient', back_populates='lab_requests')
    requester = db.relationship(
        'User', back_populates='lab_requests', foreign_keys=[requested_by]
    )
    technician = db.relationship(
        'User', back_populates='lab_assignments', foreign_keys=[lab_technician_id]
    )
    reports = db.relationship(
        'LabReport', back_populates='laboratory', lazy='dynamic', passive_deletes=True
    )

    # ------ Indexes (match SQL) ------
    __table_args__ = (
        db.Index('idx_lab_visit', 'visit_id'),
        db.Index('idx_lab_patient', 'patient_id'),
        db.Index('idx_lab_status', 'test_status'),
        db.Index('idx_lab_requested_by', 'requested_by'),
    )

    def __repr__(self):
        return f'<Laboratory {self.lab_id} status={self.test_status}>'
