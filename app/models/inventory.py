from app import db


class Inventory(db.Model):
    """Inventory batch for a medicine — tracks stock per batch."""

    __tablename__ = 'inventory'

    inventory_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    medicine_id = db.Column(
        db.BigInteger,
        db.ForeignKey('medicines.medicine_id', ondelete='CASCADE'),
        nullable=False,
    )
    batch_number = db.Column(db.String(50), nullable=False)
    expiry_date = db.Column(db.Date)
    purchase_price = db.Column(db.Numeric(10, 2))
    selling_price = db.Column(db.Numeric(10, 2))
    quantity_in_stock = db.Column(db.Integer, default=0)
    minimum_stock = db.Column(db.Integer, default=0)
    supplier = db.Column(db.String(100))
    last_updated = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # ------ Relationships ------
    medicine = db.relationship('Medicine', back_populates='inventory_batches')
    prescriptions = db.relationship(
        'Prescription', back_populates='inventory_batch', lazy='dynamic'
    )
    transactions = db.relationship(
        'InventoryTransaction', back_populates='inventory_batch', lazy='dynamic'
    )

    # ------ Index (matches SQL) ------
    __table_args__ = (
        db.Index('idx_inventory_medicine', 'medicine_id'),
    )

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.minimum_stock

    @property
    def is_expired(self):
        from datetime import date
        return self.expiry_date and self.expiry_date < date.today()

    def __repr__(self):
        return f'<Inventory batch={self.batch_number} qty={self.quantity_in_stock}>'
