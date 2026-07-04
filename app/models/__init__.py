"""Data models package.

All SQLAlchemy models are imported here for Flask-Migrate detection.
"""

from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.patient import Patient
from app.models.medicine import Medicine
from app.models.inventory import Inventory
from app.models.visit import Visit
from app.models.prescription import Prescription
from app.models.inventory_transaction import InventoryTransaction
from app.models.lab_test_catalog import LabTestCatalog
from app.models.laboratory import Laboratory
from app.models.lab_report import LabReport
from app.models.doctor_report import DoctorReport

__all__ = [
    'User',
    'Role',
    'UserRole',
    'Patient',
    'Medicine',
    'Inventory',
    'Visit',
    'Prescription',
    'InventoryTransaction',
    'LabTestCatalog',
    'Laboratory',
    'LabReport',
    'DoctorReport',
]
