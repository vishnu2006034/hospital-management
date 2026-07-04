"""Medicine database model."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List

from app import db

if TYPE_CHECKING:
    from app.models.inventory import Inventory


class Medicine(db.Model):
    """Medicine / drug catalog entry.

    Stores information about each medicine available in the hospital
    pharmacy. Individual stock batches are tracked in the Inventory model.
    """

    __tablename__: str = 'medicines'

    # Primary Key
    medicine_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Medicine Information
    medicine_name: str = db.Column(db.String(100), nullable=False)
    generic_name: str = db.Column(db.String(100))
    category: str = db.Column(db.String(50))
    dosage_form: str = db.Column(db.String(50))
    strength: str = db.Column(db.String(50))
    manufacturer: str = db.Column(db.String(100))
    unit_price: Decimal = db.Column(db.Numeric(10, 2))

    # Timestamps
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    inventory_batches: List['Inventory'] = db.relationship(
        'Inventory', back_populates='medicine', lazy='dynamic', passive_deletes=True
    )

