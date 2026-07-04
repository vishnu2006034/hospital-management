"""LabReport database model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app import db

if TYPE_CHECKING:
    from app.models.laboratory import Laboratory
    from app.models.lab_test_catalog import LabTestCatalog
    from app.models.patient import Patient
    from app.models.user import User


class LabReport(db.Model):
    """Individual test result within a laboratory request.

    Stores the result of a single lab test, including reference ranges
    and abnormality flags. Each lab request can have multiple reports.
    """

    __tablename__: str = 'lab_report'

    # ── Primary Key ──────────────────────────────────────────────
    lab_report_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # ── Foreign Keys ─────────────────────────────────────────────
    lab_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('laboratory.lab_id', ondelete='CASCADE'),
        nullable=False,
    )
    test_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('lab_test_catalog.test_id'),
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
    verified_by: Optional[int] = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
    )

    # ── Report Information ───────────────────────────────────────
    report_number: str = db.Column(db.String(30), unique=True, nullable=False)
    result: str = db.Column(db.Text, nullable=False)
    unit: Optional[str] = db.Column(db.String(30))
    reference_range: Optional[str] = db.Column(db.String(100))
    is_abnormal: bool = db.Column(db.Boolean, default=False)
    remarks: Optional[str] = db.Column(db.Text)

    # ── Verification ─────────────────────────────────────────────
    verified_at: Optional[datetime] = db.Column(db.DateTime)

    # ── File Storage ─────────────────────────────────────────────
    report_file: Optional[str] = db.Column(db.Text)

    # ── Timestamps ───────────────────────────────────────────────
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())

    # ── Relationships ────────────────────────────────────────────
    laboratory: 'Laboratory' = db.relationship('Laboratory', back_populates='reports')
    test: 'LabTestCatalog' = db.relationship('LabTestCatalog', back_populates='lab_reports')
    patient: 'Patient' = db.relationship('Patient', back_populates='lab_reports')
    doctor: 'User' = db.relationship('User', foreign_keys=[doctor_id])
    verifier: Optional['User'] = db.relationship('User', foreign_keys=[verified_by])

    # ── Indexes ──────────────────────────────────────────────────
    __table_args__ = (
        db.Index('idx_lab_report_lab', 'lab_id'),
        db.Index('idx_lab_report_test', 'test_id'),
        db.Index('idx_lab_report_patient', 'patient_id'),
        db.Index('idx_lab_report_doctor', 'doctor_id'),
    )

    def __repr__(self) -> str:
        return f'<LabReport {self.report_number} abnormal={self.is_abnormal}>'
