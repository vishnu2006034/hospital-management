"""Laboratory database model."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from app import db

if TYPE_CHECKING:
    from app.models.visit import Visit
    from app.models.patient import Patient
    from app.models.user import User
    from app.models.lab_report import LabReport


class Laboratory(db.Model):
    """Laboratory request — groups one or more test results.

    Represents a lab test order for a patient visit. Contains one or
    more lab reports with individual test results.
    """

    __tablename__: str = 'laboratory'

    # ── Primary Key ──────────────────────────────────────────────
    lab_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # ── Foreign Keys ─────────────────────────────────────────────
    visit_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('visits.visit_id', ondelete='CASCADE'),
        nullable=False,
    )
    patient_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('patients.patient_id', ondelete='CASCADE'),
        nullable=False,
    )
    requested_by: int = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
        nullable=False,
    )
    lab_technician_id: Optional[int] = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
    )

    # ── Lab Request Information ──────────────────────────────────
    priority: str = db.Column(db.String(20), default='NORMAL')
    sample_type: Optional[str] = db.Column(db.String(50))
    sample_collected_at: Optional[datetime] = db.Column(db.DateTime)
    test_status: str = db.Column(db.String(30), default='PENDING')
    remarks: Optional[str] = db.Column(db.Text)

    # ── Timestamps ───────────────────────────────────────────────
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())
    completed_at: Optional[datetime] = db.Column(db.DateTime)

    # ── Relationships ────────────────────────────────────────────
    visit: 'Visit' = db.relationship('Visit', back_populates='lab_requests')
    patient: 'Patient' = db.relationship('Patient', back_populates='lab_requests')
    requester: 'User' = db.relationship(
        'User', back_populates='lab_requests', foreign_keys=[requested_by]
    )
    technician: Optional['User'] = db.relationship(
        'User', back_populates='lab_assignments', foreign_keys=[lab_technician_id]
    )
    reports: List['LabReport'] = db.relationship(
        'LabReport', back_populates='laboratory', lazy='dynamic', passive_deletes=True
    )

    # ── Indexes ──────────────────────────────────────────────────
    __table_args__ = (
        db.Index('idx_lab_visit', 'visit_id'),
        db.Index('idx_lab_patient', 'patient_id'),
        db.Index('idx_lab_status', 'test_status'),
        db.Index('idx_lab_requested_by', 'requested_by'),
    )

    def __repr__(self) -> str:
        return f'<Laboratory {self.lab_id} status={self.test_status}>'
