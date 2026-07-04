"""Visit service for business logic."""

from typing import Dict, List, Optional, Any

from app.models.visit import Visit
from app.repositories.visit_repository import visit_repository


class VisitService:
    """Service layer for Visit business operations."""

    @staticmethod
    def get_all_visits(
        page: int = 1,
        per_page: int = 15,
        status: Optional[str] = None,
        search: Optional[str] = None,
    ):
        """Get paginated list of visits.

        Args:
            page: Page number.
            per_page: Items per page.
            status: Optional status filter.
            search: Optional search term.

        Returns:
            Paginated visit results.
        """
        return visit_repository.search(
            search, status=status, page=page, per_page=per_page
        )

    @staticmethod
    def get_visit_by_id(visit_id: int) -> Visit:
        """Get a visit by ID.

        Args:
            visit_id: The visit's ID.

        Returns:
            The visit entity.

        Raises:
            404: If visit not found.
        """
        return visit_repository.get_by_id(visit_id)

    @staticmethod
    def create_visit(
        data: Dict[str, Any], admission_date: Optional[str] = None
    ) -> Visit:
        """Create a new visit.

        Args:
            data: Visit data dictionary.
            performed_by: Optional user ID for initial stock entry.

        Returns:
            The created visit entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}
        admission_date = admission_date if (admission_date and admission_date.strip()) else None

        visit: Visit = Visit(
            patient_id=cleaned['patient_id'],
            doctor_id=cleaned['doctor_id'],
            visit_type=cleaned.get('visit_type') or 'OUTPATIENT',
            visit_status='OPEN',
            chief_complaint=cleaned.get('chief_complaint'),
            diagnosis=cleaned.get('diagnosis'),
            treatment_plan=cleaned.get('treatment_plan'),
            notes=cleaned.get('notes'),
            height=cleaned.get('height'),
            weight=cleaned.get('weight'),
            temperature=cleaned.get('temperature'),
            blood_pressure=cleaned.get('blood_pressure'),
            pulse_rate=cleaned.get('pulse_rate'),
            oxygen_level=cleaned.get('oxygen_level'),
        )
        if admission_date:
            visit.admission_date = admission_date
        visit_repository.add(visit)
        visit_repository.commit()
        return visit

    @staticmethod
    def update_visit(
        visit: Visit,
        data: Dict[str, Any],
        admission_date: Optional[str] = None,
        discharge_date: Optional[str] = None,
    ) -> Visit:
        """Update an existing visit.

        Args:
            visit: The visit entity to update.
            data: Updated visit data.
            admission_date: Optional admission date.
            discharge_date: Optional discharge date.

        Returns:
            The updated visit entity.
        """
        cleaned = {k: (None if (isinstance(v, str) and not v.strip()) else v) for k, v in data.items()}
        admission_date = admission_date if (admission_date and admission_date.strip()) else None
        discharge_date = discharge_date if (discharge_date and discharge_date.strip()) else None

        visit.visit_type = cleaned.get('visit_type') or visit.visit_type
        visit.visit_status = cleaned.get('visit_status') or visit.visit_status
        visit.chief_complaint = cleaned.get('chief_complaint')
        visit.diagnosis = cleaned.get('diagnosis')
        visit.treatment_plan = cleaned.get('treatment_plan')
        visit.notes = cleaned.get('notes')
        visit.height = cleaned.get('height')
        visit.weight = cleaned.get('weight')
        visit.temperature = cleaned.get('temperature')
        visit.blood_pressure = cleaned.get('blood_pressure')
        visit.pulse_rate = cleaned.get('pulse_rate')
        visit.oxygen_level = cleaned.get('oxygen_level')
        
        # Update admission/discharge dates (even if None)
        visit.admission_date = admission_date
        visit.discharge_date = discharge_date

        visit_repository.commit()
        return visit

    @staticmethod
    def delete_visit(visit: Visit) -> None:
        """Delete a visit.

        Args:
            visit: The visit entity to delete.
        """
        visit_repository.delete(visit)
        visit_repository.commit()

    @staticmethod
    def get_all_patients() -> List:
        """Get all patients.

        Returns:
            List of all patients.
        """
        return visit_repository.get_all_patients()

    @staticmethod
    def get_all_doctors() -> List:
        """Get all doctors.

        Returns:
            List of doctor users.
        """
        return visit_repository.get_all_doctors()

    @staticmethod
    def get_visit_details(visit: Visit) -> Dict[str, List]:
        """Get all related entities for a visit.

        Args:
            visit: The visit entity.

        Returns:
            Dictionary with prescriptions, lab_requests, and doctor_reports.
        """
        return visit_repository.get_visit_details(visit)
