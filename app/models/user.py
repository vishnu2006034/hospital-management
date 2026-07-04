"""User (Staff) database model."""

from datetime import date, datetime
from typing import TYPE_CHECKING, List, Optional

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db

if TYPE_CHECKING:
    from app.models.user_role import UserRole
    from app.models.visit import Visit
    from app.models.prescription import Prescription
    from app.models.laboratory import Laboratory
    from app.models.doctor_report import DoctorReport


class User(UserMixin, db.Model):
    """Staff / system user — doctors, nurses, admins, etc.

    Represents any employee of the hospital including doctors, nurses,
    pharmacists, lab technicians, and administrative staff.
    """

    __tablename__: str = 'users'

    # ── Primary Key ──────────────────────────────────────────────
    user_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # ── Identification ───────────────────────────────────────────
    employee_code: str = db.Column(db.String(20), unique=True, nullable=False)

    # ── Personal Information ─────────────────────────────────────
    first_name: str = db.Column(db.String(50), nullable=False)
    last_name: Optional[str] = db.Column(db.String(50))
    gender: Optional[str] = db.Column(db.String(10))
    dob: Optional[date] = db.Column(db.Date)

    # ── Contact Information ──────────────────────────────────────
    phone: Optional[str] = db.Column(db.String(15), unique=True)
    email: Optional[str] = db.Column(db.String(100), unique=True)

    # ── Authentication ───────────────────────────────────────────
    password_hash: str = db.Column(db.Text, nullable=False)

    # ── Professional Information ─────────────────────────────────
    department: Optional[str] = db.Column(db.String(100))
    specialization: Optional[str] = db.Column(db.String(100))
    license_number: Optional[str] = db.Column(db.String(60))
    joining_date: Optional[date] = db.Column(db.Date)

    # ── Status ───────────────────────────────────────────────────
    status: str = db.Column(db.String(20), default='ACTIVE')

    # ── Timestamps ───────────────────────────────────────────────
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())
    updated_at: datetime = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ── Relationships ────────────────────────────────────────────
    user_roles: List['UserRole'] = db.relationship(
        'UserRole', back_populates='user',
        foreign_keys='UserRole.user_id', lazy='dynamic', passive_deletes=True
    )
    visits_as_doctor: List['Visit'] = db.relationship(
        'Visit', back_populates='doctor', lazy='dynamic'
    )
    prescriptions_written: List['Prescription'] = db.relationship(
        'Prescription', back_populates='prescriber', lazy='dynamic'
    )
    lab_requests: List['Laboratory'] = db.relationship(
        'Laboratory', back_populates='requester',
        foreign_keys='Laboratory.requested_by', lazy='dynamic'
    )
    lab_assignments: List['Laboratory'] = db.relationship(
        'Laboratory', back_populates='technician',
        foreign_keys='Laboratory.lab_technician_id', lazy='dynamic'
    )
    doctor_reports: List['DoctorReport'] = db.relationship(
        'DoctorReport', back_populates='doctor', lazy='dynamic'
    )

    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    # ── Flask-Login Integration ──────────────────────────────────
    def get_id(self) -> str:
        """Return the user_id as a string for Flask-Login."""
        return str(self.user_id)

    # ── Password Helpers ─────────────────────────────────────────
    def set_password(self, password: str) -> None:
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        return check_password_hash(self.password_hash, password)

    # ── Convenience Properties ───────────────────────────────────
    @property
    def full_name(self) -> str:
        """Return concatenated first and last name."""
        parts: List[Optional[str]] = [self.first_name, self.last_name]
        return ' '.join(p for p in parts if p)

    @property
    def role_names(self) -> List[str]:
        """Return a list of active role names for this user."""
        return [
            ur.role.role_name
            for ur in self.user_roles.filter_by(is_active=True).all()
            if ur.role
        ]

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return role_name in self.role_names

    def __repr__(self) -> str:
        return f'<User {self.employee_code} – {self.full_name}>'
