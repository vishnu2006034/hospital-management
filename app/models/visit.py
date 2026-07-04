"""Visit database model."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from app import db

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.user import User
    from app.models.prescription import Prescription
    from app.models.laboratory import Laboratory
    from app.models.doctor_report import DoctorReport


class Visit(db.Model):
    """Patient visit — outpatient consultation or inpatient admission.

    Tracks the complete lifecycle of a patient visit including vitals,
    clinical information, and links to prescriptions, lab requests,
    and doctor reports.
    """

    __tablename__: str = 'visits'

    # ── Primary Key ──────────────────────────────────────────────
    visit_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # ── Foreign Keys ─────────────────────────────────────────────
    patient_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('patients.patient_id', ondelete='CASCADE'),
        nullable=False,
    )
    doctor_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
        nullable=False,
    )

    # ── Visit Information ────────────────────────────────────────
    visit_type: str = db.Column(db.String(20), default='OUTPATIENT')
    visit_status: str = db.Column(db.String(20), default='OPEN')
    visit_date: datetime = db.Column(db.DateTime, server_default=db.func.now())
    admission_date: Optional[datetime] = db.Column(db.DateTime)
    discharge_date: Optional[datetime] = db.Column(db.DateTime)

    # ── Clinical Information ─────────────────────────────────────
    chief_complaint: Optional[str] = db.Column(db.Text)
    diagnosis: Optional[str] = db.Column(db.Text)
    treatment_plan: Optional[str] = db.Column(db.Text)
    notes: Optional[str] = db.Column(db.Text)

    # ── Vital Signs ──────────────────────────────────────────────
    height: Optional[Decimal] = db.Column(db.Numeric(5, 2))
    weight: Optional[Decimal] = db.Column(db.Numeric(5, 2))
    temperature: Optional[Decimal] = db.Column(db.Numeric(4, 1))
    blood_pressure: Optional[str] = db.Column(db.String(20))
    pulse_rate: Optional[int] = db.Column(db.Integer)
    oxygen_level: Optional[int] = db.Column(db.Integer)

    # ── Timestamps ───────────────────────────────────────────────
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())
    updated_at: datetime = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ── Relationships ────────────────────────────────────────────
    patient: 'Patient' = db.relationship('Patient', back_populates='visits')
    doctor: 'User' = db.relationship('User', back_populates='visits_as_doctor')
    prescriptions: List['Prescription'] = db.relationship(
        'Prescription', back_populates='visit', lazy='dynamic', passive_deletes=True
    )
    lab_requests: List['Laboratory'] = db.relationship(
        'Laboratory', back_populates='visit', lazy='dynamic', passive_deletes=True
    )
    doctor_reports: List['DoctorReport'] = db.relationship(
        'DoctorReport', back_populates='visit', lazy='dynamic', passive_deletes=True
    )

    # ── Indexes ──────────────────────────────────────────────────
    __table_args__ = (
        db.Index('idx_visit_patient', 'patient_id'),
        db.Index('idx_visit_doctor', 'doctor_id'),
    )

    def __repr__(self) -> str:
        return f'<Visit {self.visit_id} type={self.visit_type} status={self.visit_status}>'
