from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db


class User(UserMixin, db.Model):
    """Staff / system user — doctors, nurses, admins, etc."""

    __tablename__ = 'users'

    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    employee_code = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50))
    gender = db.Column(db.String(10))
    dob = db.Column(db.Date)
    phone = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(100), unique=True)
    password_hash = db.Column(db.Text, nullable=False)
    department = db.Column(db.String(100))
    specialization = db.Column(db.String(100))
    license_number = db.Column(db.String(60))
    joining_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='ACTIVE')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ------ Relationships ------
    user_roles = db.relationship(
        'UserRole', back_populates='user',
        foreign_keys='UserRole.user_id', lazy='dynamic'
    )
    visits_as_doctor = db.relationship(
        'Visit', back_populates='doctor', lazy='dynamic'
    )
    prescriptions_written = db.relationship(
        'Prescription', back_populates='prescriber', lazy='dynamic'
    )
    lab_requests = db.relationship(
        'Laboratory', back_populates='requester',
        foreign_keys='Laboratory.requested_by', lazy='dynamic'
    )
    lab_assignments = db.relationship(
        'Laboratory', back_populates='technician',
        foreign_keys='Laboratory.lab_technician_id', lazy='dynamic'
    )
    doctor_reports = db.relationship(
        'DoctorReport', back_populates='doctor', lazy='dynamic'
    )

    # ---- Flask-Login integration ----
    def get_id(self):
        """Return the user_id as a string for Flask-Login."""
        return str(self.user_id)

    # ---- Password helpers ----
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    # ---- Convenience ----
    @property
    def full_name(self):
        parts = [self.first_name, self.last_name]
        return ' '.join(p for p in parts if p)

    @property
    def role_names(self):
        """Return a list of active role names for this user."""
        return [
            ur.role.role_name
            for ur in self.user_roles.filter_by(is_active=True).all()
            if ur.role
        ]

    def has_role(self, role_name):
        return role_name in self.role_names

    def __repr__(self):
        return f'<User {self.employee_code} – {self.full_name}>'
