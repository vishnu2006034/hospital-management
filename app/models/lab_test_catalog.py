"""LabTestCatalog database model."""

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from app import db

if TYPE_CHECKING:
    from app.models.lab_report import LabReport


class LabTestCatalog(db.Model):
    """Master catalog of available laboratory tests.

    Defines all laboratory tests that can be ordered, including
    reference ranges, sample types, and default pricing.
    """

    __tablename__: str = 'lab_test_catalog'

    # ── Primary Key ──────────────────────────────────────────────
    test_id: int = db.Column(db.BigInteger, primary_key=True, autoincrement=True)

    # ── Test Identification ──────────────────────────────────────
    test_code: str = db.Column(db.String(20), unique=True, nullable=False)
    test_name: str = db.Column(db.String(100), nullable=False)

    # ── Test Details ─────────────────────────────────────────────
    category: Optional[str] = db.Column(db.String(50))
    sample_type: Optional[str] = db.Column(db.String(50))
    unit: Optional[str] = db.Column(db.String(30))
    reference_range: Optional[str] = db.Column(db.String(100))
    normal_min: Optional[Decimal] = db.Column(db.Numeric(10, 2))
    normal_max: Optional[Decimal] = db.Column(db.Numeric(10, 2))

    # ── Pricing ──────────────────────────────────────────────────
    default_price: Optional[Decimal] = db.Column(db.Numeric(10, 2))

    # ── Description ──────────────────────────────────────────────
    description: Optional[str] = db.Column(db.Text)

    # ── Status ───────────────────────────────────────────────────
    is_active: bool = db.Column(db.Boolean, default=True)

    # ── Timestamps ───────────────────────────────────────────────
    created_at: datetime = db.Column(db.DateTime, server_default=db.func.now())

    # ── Relationships ────────────────────────────────────────────
    lab_reports: List['LabReport'] = db.relationship(
        'LabReport', back_populates='test', lazy='dynamic'
    )

    def __repr__(self) -> str:
        return f'<LabTestCatalog {self.test_code} – {self.test_name}>'
