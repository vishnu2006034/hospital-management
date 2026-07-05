"""InventoryTransaction database model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app import db

if TYPE_CHECKING:
    from app.models.inventory import Inventory
    from app.models.user import User


class InventoryTransaction(db.Model):
    """Stock movement log — IN, OUT, ADJUSTMENT, etc.

    Records every stock movement for audit trail purposes.
    Transaction types include:
    - IN: Stock received (purchase, return)
    - OUT: Stock dispensed (prescription, damaged)
    - ADJUSTMENT: Manual stock correction
    """

    __tablename__: str = 'inventory_transactions'

    # Primary Key
    transaction_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    inventory_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('inventory.inventory_id', ondelete='CASCADE'),
        nullable=False,
    )
    performed_by: Optional[int] = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
    )

    # Transaction Information
    transaction_type: str = db.Column(db.String(20))  # IN / OUT / ADJUSTMENT
    quantity: int = db.Column(db.Integer, nullable=False)
    reference_type: str = db.Column(db.String(30))  # PRESCRIPTION / PURCHASE / etc.
    reference_id: Optional[int] = db.Column(db.BigInteger)
    remarks: str = db.Column(db.Text)

    # Timestamps
    transaction_date: datetime = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    inventory_batch: 'Inventory' = db.relationship(
        'Inventory', back_populates='transactions'
    )
    performer: Optional['User'] = db.relationship('User')

    # Indexes
    __table_args__ = (
        db.Index('idx_inventory_txn', 'inventory_id'),
    )

