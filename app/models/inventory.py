"""Inventory database model."""

from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List

from app import db

if TYPE_CHECKING:
    from app.models.medicine import Medicine
    from app.models.prescription import Prescription
    from app.models.inventory_transaction import InventoryTransaction


class Inventory(db.Model):
    """Inventory batch for a medicine — tracks stock per batch.

    Each medicine can have multiple inventory batches with different
    batch numbers, expiry dates, and stock levels. This model tracks
    the actual physical stock available.
    """

    __tablename__: str = 'inventory'

    # Primary Key
    inventory_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    medicine_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('medicines.medicine_id', ondelete='CASCADE'),
        nullable=False,
    )

    # Batch Information
    batch_number: str = db.Column(db.String(50), nullable=False)
    expiry_date: date = db.Column(db.Date)

    # Pricing
    purchase_price: Decimal = db.Column(db.Numeric(10, 2))
    selling_price: Decimal = db.Column(db.Numeric(10, 2))

    # Stock Levels
    quantity_in_stock: int = db.Column(db.Integer, default=0)
    minimum_stock: int = db.Column(db.Integer, default=0)

    # Supplier Information
    supplier: str = db.Column(db.String(100))

    # Timestamps
    last_updated: datetime = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
    )

    # Relationships
    medicine: 'Medicine' = db.relationship('Medicine', back_populates='inventory_batches')
    prescriptions: List['Prescription'] = db.relationship(
        'Prescription', back_populates='inventory_batch', lazy='dynamic'
    )
    transactions: List['InventoryTransaction'] = db.relationship(
        'InventoryTransaction', back_populates='inventory_batch',
        lazy='dynamic', passive_deletes=True
    )

    # Indexes
    __table_args__ = (
        db.Index('idx_inventory_medicine', 'medicine_id'),
    )

    # Computed Properties
    @property
    def is_low_stock(self) -> bool:
        """Check if stock is at or below minimum threshold."""
        return self.quantity_in_stock <= self.minimum_stock

    @property
    def is_expired(self) -> bool:
        """Check if this batch has expired."""
        return self.expiry_date is not None and self.expiry_date < date.today()

