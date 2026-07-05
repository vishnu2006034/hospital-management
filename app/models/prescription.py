"""Prescription database model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from app import db

if TYPE_CHECKING:
    from app.models.visit import Visit
    from app.models.inventory import Inventory
    from app.models.user import User


class Prescription(db.Model):
    """Medicine prescribed during a visit, linked to a specific inventory batch.

    Connects a patient visit to a specific medicine batch and tracks
    dosage, frequency, and duration of the prescription.
    """

    __tablename__: str = 'prescriptions'

    # Primary Key
    prescription_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # Foreign Keys
    visit_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('visits.visit_id', ondelete='CASCADE'),
        nullable=False,
    )
    inventory_id: int = db.Column(
        db.BigInteger,
        db.ForeignKey('inventory.inventory_id'),
        nullable=False,
    )
    prescribed_by: int = db.Column(
        db.BigInteger,
        db.ForeignKey('users.user_id'),
        nullable=False,
    )

    # Prescription Details
    dosage: Optional[str] = db.Column(db.String(100))
    frequency: Optional[str] = db.Column(db.String(100))
    duration: Optional[str] = db.Column(db.String(50))
    quantity: Optional[int] = db.Column(db.Integer)
    instructions: Optional[str] = db.Column(db.Text)

    # Timestamps
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())

    # Relationships
    visit: 'Visit' = db.relationship('Visit', back_populates='prescriptions')
    inventory_batch: 'Inventory' = db.relationship('Inventory', back_populates='prescriptions')
    prescriber: 'User' = db.relationship('User', back_populates='prescriptions_written')

    # Indexes
    __table_args__ = (
        db.Index('idx_prescription_visit', 'visit_id'),
    )

