"""DoctorReport database model."""

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional

from app import db

if TYPE_CHECKING:
    from app.models.visit import Visit
    from app.models.patient import Patient
    from app.models.user import User


class DoctorReport(db.Model):
    """Doctor consultation report for a visit.

    Comprehensive report created by a doctor after a patient consultation,
    including diagnosis, treatment plan, and follow-up information.
    """

    __tablename__: str = 'doctor_report'

    # Primary Key
    doctor_report_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
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
    doctor_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
        nullable=False,
    )

    # Report Information
    report_number: str = db.Column(db.String(30), unique=True, nullable=False)
    chief_complaint: Optional[str] = db.Column(db.Text)
    clinical_findings: Optional[str] = db.Column(db.Text)
    diagnosis: Optional[str] = db.Column(db.Text)
    treatment_plan: Optional[str] = db.Column(db.Text)
    prescribed_medicines: Optional[str] = db.Column(db.Text)
    doctor_notes: Optional[str] = db.Column(db.Text)

    # Follow-up Information
    follow_up_required: bool = db.Column(db.Boolean, default=False)
    follow_up_date: Optional[date] = db.Column(db.Date)
    next_visit_reason: Optional[str] = db.Column(db.Text)

    # File Storage
    report_file: Optional[str] = db.Column(db.Text)

    # Timestamps
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())
    updated_at: datetime = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # Relationships
    visit: 'Visit' = db.relationship('Visit', back_populates='doctor_reports')
    patient: 'Patient' = db.relationship('Patient', back_populates='doctor_reports')
    doctor: 'User' = db.relationship('User', back_populates='doctor_reports')

    # Indexes
    __table_args__ = (
        db.Index('idx_doctor_report_visit', 'visit_id'),
        db.Index('idx_doctor_report_patient', 'patient_id'),
        db.Index('idx_doctor_report_doctor', 'doctor_id'),
    )

