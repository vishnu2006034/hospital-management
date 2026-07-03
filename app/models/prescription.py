from app import db


class Prescription(db.Model):
    """Medicine prescribed during a visit, linked to a specific inventory batch."""

    __tablename__ = 'prescriptions'

    prescription_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    visit_id = db.Column(
        db.BigInteger,
        db.ForeignKey('visits.visit_id', ondelete='CASCADE'),
        nullable=False,
    )
    inventory_id = db.Column(
        db.BigInteger,
        db.ForeignKey('inventory.inventory_id'),
        nullable=False,
    )
    prescribed_by = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
        nullable=False,
    )
    dosage = db.Column(db.String(100))
    frequency = db.Column(db.String(100))
    duration = db.Column(db.String(50))
    quantity = db.Column(db.Integer)
    instructions = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # ------ Relationships ------
    visit = db.relationship('Visit', back_populates='prescriptions')
    inventory_batch = db.relationship('Inventory', back_populates='prescriptions')
    prescriber = db.relationship('User', back_populates='prescriptions_written')

    # ------ Index (match SQL) ------
    __table_args__ = (
        db.Index('idx_prescription_visit', 'visit_id'),
    )


