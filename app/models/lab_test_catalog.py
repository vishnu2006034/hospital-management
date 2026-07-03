from app import db


class LabTestCatalog(db.Model):
    """Master catalog of available laboratory tests."""

    __tablename__ = 'lab_test_catalog'

    test_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    test_code = db.Column(db.String(20), unique=True, nullable=False)
    test_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    sample_type = db.Column(db.String(50))
    unit = db.Column(db.String(30))
    reference_range = db.Column(db.String(100))
    normal_min = db.Column(db.Numeric(10, 2))
    normal_max = db.Column(db.Numeric(10, 2))
    default_price = db.Column(db.Numeric(10, 2))
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # ------ Relationships ------
    lab_reports = db.relationship(
        'LabReport', back_populates='test', lazy='dynamic'
    )


