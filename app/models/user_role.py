from app import db


class UserRole(db.Model):
    """Many-to-many association between User and Role with metadata."""

    __tablename__ = 'user_roles'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )

    user_role_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id', ondelete='CASCADE'),
        nullable=False,
    )
    role_id = db.Column(
        db.BigInteger,
        db.ForeignKey('roles.role_id', ondelete='CASCADE'),
        nullable=False,
    )
    assigned_by = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id', ondelete='SET NULL'),
    )
    assigned_at = db.Column(db.DateTime, server_default=db.func.now())
    is_active = db.Column(db.Boolean, default=True)

    # ------ Relationships ------
    user = db.relationship(
        'User', back_populates='user_roles', foreign_keys=[user_id]
    )
    role = db.relationship('Role', back_populates='user_roles')
    assigner = db.relationship('User', foreign_keys=[assigned_by])


