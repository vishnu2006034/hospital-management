"""Patient database model."""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from app import db

if TYPE_CHECKING:
    from app.models.visit import Visit
    from app.models.laboratory import Laboratory
    from app.models.lab_report import LabReport
    from app.models.doctor_report import DoctorReport


class Patient(db.Model):
    """Patient demographics and medical background.

    Stores personal information, emergency contacts, and medical history
    for each patient registered in the hospital system.
    """

    __tablename__: str = 'patients'

    # Primary Key
    patient_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Identification
    patient_number: str = db.Column(db.String(20), unique=True, nullable=False)

    # Personal Information
    first_name: str = db.Column(db.String(50), nullable=False)
    last_name: Optional[str] = db.Column(db.String(50))
    gender: Optional[str] = db.Column(db.String(10))
    dob: Optional[date] = db.Column(db.Date)
    blood_group: Optional[str] = db.Column(db.String(5))

    # Contact Information
    phone: Optional[str] = db.Column(db.String(15))
    email: Optional[str] = db.Column(db.String(100))
    address: Optional[str] = db.Column(db.Text)

    # Emergency Contact
    emergency_contact_name: Optional[str] = db.Column(db.String(100))
    emergency_contact_phone: Optional[str] = db.Column(db.String(15))

    # Medical Information
    allergies: Optional[str] = db.Column(db.Text)
    medical_history: Optional[str] = db.Column(db.Text)

    # Timestamps
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())
    updated_at: datetime = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # Relationships
    visits: List['Visit'] = db.relationship(
        'Visit', back_populates='patient', lazy='dynamic', passive_deletes=True
    )
    lab_requests: List['Laboratory'] = db.relationship(
        'Laboratory', back_populates='patient', lazy='dynamic', passive_deletes=True
    )
    lab_reports: List['LabReport'] = db.relationship(
        'LabReport', back_populates='patient', lazy='dynamic', passive_deletes=True
    )
    doctor_reports: List['DoctorReport'] = db.relationship(
        'DoctorReport', back_populates='patient', lazy='dynamic', passive_deletes=True
    )

    def update_name(self, first_name: str, last_name: Optional[str] = None) -> None:
        self.first_name = first_name.strip()
        self.last_name = last_name.strip() if last_name else None

    
    
    @property
    def full_name(self) -> str:
        """Return concatenated first and last name."""
        parts: List[Optional[str]] = [self.first_name, self.last_name]
        return ' '.join(p for p in parts if p)

