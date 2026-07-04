"""Laboratory service for business logic."""

from typing import Dict, List, Optional, Any

from app.models.laboratory import Laboratory
from app.models.lab_report import LabReport
from app.models.lab_test_catalog import LabTestCatalog
from app.repositories.laboratory_repository import (
    laboratory_repository,
    lab_report_repository,
    lab_test_catalog_repository,
)


class LaboratoryService:
    """Service layer for Laboratory business operations."""

    @staticmethod
    def get_all_lab_requests(
        page: int = 1,
        per_page: int = 15,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ):
        """Get paginated list of lab requests.

        Args:
            page: Page number.
            per_page: Items per page.
            status: Optional status filter.
            search: Optional search term.

        Returns:
            Paginated lab request results.
        """
        return laboratory_repository.search(
            search, status=status, page=page, per_page=per_page
        )

    @staticmethod
    def get_lab_by_id(lab_id: int) -> Laboratory:
        """Get a lab request by ID.

        Args:
            lab_id: The lab request's ID.

        Returns:
            The laboratory entity.

        Raises:
            404: If lab request not found.
        """
        return laboratory_repository.get_by_id(lab_id)

    @staticmethod
    def create_lab_request(data: Dict[str, Any], requested_by: int) -> Laboratory:
        """Create a new lab request.

        Args:
            data: Lab request data dictionary.
            requested_by: ID of the requesting doctor.

        Returns:
            The created laboratory entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        lab: Laboratory = Laboratory(
            visit_id=cleaned['visit_id'],
            patient_id=cleaned['patient_id'],
            requested_by=requested_by,
            lab_technician_id=cleaned.get('lab_technician_id'),
            priority=cleaned.get('priority') or 'NORMAL',
            sample_type=cleaned.get('sample_type'),
            remarks=cleaned.get('remarks'),
        )
        laboratory_repository.add(lab)
        laboratory_repository.commit()
        return lab

    @staticmethod
    def update_lab_request(lab: Laboratory, data: Dict[str, Any]) -> Laboratory:
        """Update an existing lab request.

        Args:
            lab: The laboratory entity to update.
            data: Updated lab request data.

        Returns:
            The updated laboratory entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        lab.test_status = cleaned.get('test_status') or lab.test_status
        lab.priority = cleaned.get('priority') or lab.priority
        lab.lab_technician_id = cleaned.get('lab_technician_id')
        lab.sample_type = cleaned.get('sample_type')
        lab.remarks = cleaned.get('remarks')
        if cleaned.get('sample_collected_at'):
            lab.sample_collected_at = cleaned['sample_collected_at']
        laboratory_repository.update_completion_time(lab)
        laboratory_repository.commit()
        return lab

    @staticmethod
    def generate_report_number() -> str:
        """Generate a new lab report number.

        Returns:
            A unique report number.
        """
        return laboratory_repository.generate_report_number()

    @staticmethod
    def add_report(lab: Laboratory, data: Dict[str, Any]) -> LabReport:
        """Add a report to a lab request.

        Args:
            lab: The laboratory entity.
            data: Report data dictionary.

        Returns:
            The created lab report entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        report_number: str = laboratory_repository.generate_report_number()
        report: LabReport = LabReport(
            lab_id=lab.lab_id,
            test_id=cleaned['test_id'],
            patient_id=lab.patient_id,
            doctor_id=lab.requested_by,
            report_number=report_number,
            result=cleaned['result'],
            unit=cleaned.get('unit'),
            reference_range=cleaned.get('reference_range'),
            is_abnormal=bool(cleaned.get('is_abnormal')),
            remarks=cleaned.get('remarks'),
        )
        lab_report_repository.add(report)
        lab_report_repository.commit()
        return report

    @staticmethod
    def get_lab_reports(lab: Laboratory) -> List[LabReport]:
        """Get all reports for a lab request.

        Args:
            lab: The laboratory entity.

        Returns:
            List of lab reports.
        """
        return laboratory_repository.get_lab_reports(lab)

    @staticmethod
    def get_all_catalog_tests(
        page: int = 1, per_page: int = 15, search: Optional[str] = None
    ):
        """Get paginated list of catalog tests.

        Args:
            page: Page number.
            per_page: Items per page.
            search: Optional search term.

        Returns:
            Paginated catalog test results.
        """
        return lab_test_catalog_repository.search(
            search, page=page, per_page=per_page
        )

    @staticmethod
    def get_catalog_test_by_id(test_id: int) -> LabTestCatalog:
        """Get a catalog test by ID.

        Args:
            test_id: The test's ID.

        Returns:
            The lab test catalog entity.

        Raises:
            404: If test not found.
        """
        return lab_test_catalog_repository.get_by_id(test_id)

    @staticmethod
    def create_catalog_test(data: Dict[str, Any]) -> LabTestCatalog:
        """Create a new catalog test.

        Args:
            data: Test data dictionary.

        Returns:
            The created lab test catalog entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        test: LabTestCatalog = LabTestCatalog(
            test_code=cleaned['test_code'],
            test_name=cleaned['test_name'],
            category=cleaned.get('category'),
            sample_type=cleaned.get('sample_type'),
            unit=cleaned.get('unit'),
            reference_range=cleaned.get('reference_range'),
            normal_min=cleaned.get('normal_min'),
            normal_max=cleaned.get('normal_max'),
            default_price=cleaned.get('default_price'),
            description=cleaned.get('description'),
        )
        lab_test_catalog_repository.add(test)
        lab_test_catalog_repository.commit()
        return test

    @staticmethod
    def update_catalog_test(
        test: LabTestCatalog, data: Dict[str, Any]
    ) -> LabTestCatalog:
        """Update an existing catalog test.

        Args:
            test: The lab test catalog entity to update.
            data: Updated test data.

        Returns:
            The updated lab test catalog entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}

        test.test_code = cleaned['test_code']
        test.test_name = cleaned['test_name']
        test.category = cleaned.get('category')
        test.sample_type = cleaned.get('sample_type')
        test.unit = cleaned.get('unit')
        test.reference_range = cleaned.get('reference_range')
        test.normal_min = cleaned.get('normal_min')
        test.normal_max = cleaned.get('normal_max')
        test.default_price = cleaned.get('default_price')
        test.description = cleaned.get('description')
        test.is_active = bool(cleaned.get('is_active'))
        lab_test_catalog_repository.commit()
        return test

    @staticmethod
    def get_recent_visits(limit: int = 50) -> List:
        """Get recent visits.

        Args:
            limit: Maximum number of visits.

        Returns:
            List of recent visits.
        """
        return laboratory_repository.get_recent_visits(limit)

    @staticmethod
    def get_all_patients() -> List:
        """Get all patients.

        Returns:
            List of all patients.
        """
        return laboratory_repository.get_all_patients()

    @staticmethod
    def get_all_technicians() -> List:
        """Get all active technicians.

        Returns:
            List of active users.
        """
        return laboratory_repository.get_all_technicians()
