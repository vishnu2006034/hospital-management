from app import db


class Role(db.Model):
    """System role — Administrator, Doctor, Nurse, etc."""

    __tablename__ = 'roles'

    role_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # ------ Relationships ------
    user_roles = db.relationship('UserRole', back_populates='role', lazy='dynamic', passive_deletes=True)

    def __repr__(self):
        return f'<Role {self.role_name}>'
