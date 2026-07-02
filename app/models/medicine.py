from app import db


class Medicine(db.Model):
    """Medicine / drug catalog entry."""

    __tablename__ = 'medicines'

    medicine_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    medicine_name = db.Column(db.String(100), nullable=False)
    generic_name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    dosage_form = db.Column(db.String(50))
    strength = db.Column(db.String(50))
    manufacturer = db.Column(db.String(100))
    unit_price = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # ------ Relationships ------
    inventory_batches = db.relationship(
        'Inventory', back_populates='medicine', lazy='dynamic'
    )

    def __repr__(self):
        return f'<Medicine {self.medicine_name}>'
