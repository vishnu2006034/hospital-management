"""Application-wide constants.

Centralizes all magic strings, numbers, and configuration values
used throughout the application. Import from here instead of hardcoding.
"""

from enum import Enum


# Database Constants
MAX_VARCHAR_LENGTH: int = 255
PATIENT_NUMBER_FORMAT: str = 'PAT{}'
EMPLOYEE_NUMBER_FORMAT: str = 'EMP{}'
LAB_REPORT_NUMBER_FORMAT: str = 'LR{}'
DOCTOR_REPORT_NUMBER_FORMAT: str = 'DR{}'


# Visit Constants
class VisitType(str, Enum):
    """Visit type enumeration."""
    OUTPATIENT = 'OUTPATIENT'
    INPATIENT = 'INPATIENT'


class VisitStatus(str, Enum):
    """Visit status enumeration."""
    OPEN = 'OPEN'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'


# User Constants
class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    SUSPENDED = 'SUSPENDED'


# Role Names
class RoleName(str, Enum):
    """Standard role names."""
    ADMINISTRATOR = 'Administrator'
    DOCTOR = 'Doctor'
    NURSE = 'Nurse'
    RECEPTIONIST = 'Receptionist'
    PHARMACIST = 'Pharmacist'
    LAB_TECHNICIAN = 'Lab Technician'
    INVENTORY_MANAGER = 'Inventory Manager'
    ACCOUNTANT = 'Accountant'
    PATIENT = 'Patient'


# Inventory Constants
class TransactionType(str, Enum):
    """Inventory transaction type."""
    IN = 'IN'
    OUT = 'OUT'
    ADJUSTMENT = 'ADJUSTMENT'


class ReferenceType(str, Enum):
    """Transaction reference type."""
    PRESCRIPTION = 'PRESCRIPTION'
    PURCHASE = 'PURCHASE'
    RETURN = 'RETURN'
    DAMAGE = 'DAMAGE'
    ADJUSTMENT = 'ADJUSTMENT'


# Lab Constants
class LabPriority(str, Enum):
    """Lab request priority."""
    NORMAL = 'NORMAL'
    URGENT = 'URGENT'
    STAT = 'STAT'


class LabStatus(str, Enum):
    """Lab test status."""
    PENDING = 'PENDING'
    SAMPLE_COLLECTED = 'SAMPLE_COLLECTED'
    IN_PROGRESS = 'IN_PROGRESS'
    COMPLETED = 'COMPLETED'
    CANCELLED = 'CANCELLED'


# Application Constants
DEFAULT_PAGE_SIZE: int = 15
MAX_PAGE_SIZE: int = 100
HOSPITAL_BED_CAPACITY: int = 100
STOCK_MARGIN_PERCENTAGE: float = 0.30
DEFAULT_PASSWORD: str = 'changeme123'
INVENTORY_EXPIRY_DAYS: int = 365


# Flash Message Categories
class FlashCategory(str, Enum):
    """Flash message categories."""
    SUCCESS = 'success'
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
