"""Repositories package.

Data access layer implementations for each domain entity.
"""

from app.repositories.base_repository import BaseRepository
from app.repositories.patient_repository import PatientRepository, patient_repository
from app.repositories.user_repository import UserRepository, user_repository
from app.repositories.visit_repository import VisitRepository, visit_repository
from app.repositories.medicine_repository import MedicineRepository, medicine_repository
from app.repositories.inventory_repository import InventoryRepository, inventory_repository
from app.repositories.prescription_repository import PrescriptionRepository, prescription_repository
from app.repositories.laboratory_repository import (
    LaboratoryRepository,
    LabReportRepository,
    LabTestCatalogRepository,
    laboratory_repository,
    lab_report_repository,
    lab_test_catalog_repository,
)
from app.repositories.report_repository import ReportRepository, report_repository

__all__ = [
    # Base
    'BaseRepository',
    # Repositories
    'PatientRepository',
    'UserRepository',
    'VisitRepository',
    'MedicineRepository',
    'InventoryRepository',
    'PrescriptionRepository',
    'LaboratoryRepository',
    'LabReportRepository',
    'LabTestCatalogRepository',
    'ReportRepository',
    # Singletons
    'patient_repository',
    'user_repository',
    'visit_repository',
    'medicine_repository',
    'inventory_repository',
    'prescription_repository',
    'laboratory_repository',
    'lab_report_repository',
    'lab_test_catalog_repository',
    'report_repository',
]
