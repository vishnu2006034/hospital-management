from app import db


class InventoryTransaction(db.Model):
    """Stock movement log — IN, OUT, ADJUSTMENT, etc."""

    __tablename__ = 'inventory_transactions'

    transaction_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    inventory_id = db.Column(
        db.BigInteger,
        db.ForeignKey('inventory.inventory_id', ondelete='CASCADE'),
        nullable=False,
    )
    transaction_type = db.Column(db.String(20))          # IN / OUT / ADJUSTMENT
    quantity = db.Column(db.Integer, nullable=False)
    reference_type = db.Column(db.String(30))             # PRESCRIPTION / PURCHASE / etc.
    reference_id = db.Column(db.BigInteger)
    performed_by = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
    )
    remarks = db.Column(db.Text)
    transaction_date = db.Column(db.DateTime, server_default=db.func.now())

    # ------ Relationships ------
    inventory_batch = db.relationship(
        'Inventory', back_populates='transactions'
    )
    performer = db.relationship('User')

    # ------ Index (match SQL) ------
    __table_args__ = (
        db.Index('idx_inventory_txn', 'inventory_id'),
    )


