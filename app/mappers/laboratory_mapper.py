from app.models.laboratory import Laboratory
from app.models.lab_report import LabReport
from app.models.lab_test_catalog import LabTestCatalog
from app.dtos.laboratory import (
    LaboratoryResponse,
    LaboratoryCreateRequest,
    LaboratoryUpdateRequest,
    LabReportResponse,
    LabReportCreateRequest,
    LabTestCatalogResponse,
    LabTestCatalogCreateRequest,
    LabTestCatalogUpdateRequest,
)
from app.mappers.patient_mapper import PatientMapper
from app.mappers.user_mapper import UserMapper
from app.mappers.visit_mapper import VisitMapper

class LaboratoryMapper:
    @staticmethod
    def to_dto(lab: Laboratory) -> LaboratoryResponse:
        if not lab:
            return None
        return LaboratoryResponse(
            lab_id=lab.lab_id,
            visit_id=lab.visit_id,
            patient_id=lab.patient_id,
            requested_by=lab.requested_by,
            lab_technician_id=lab.lab_technician_id,
            priority=lab.priority,
            sample_type=lab.sample_type,
            sample_collected_at=lab.sample_collected_at,
            test_status=lab.test_status,
            remarks=lab.remarks,
            created_at=lab.created_at,
            completed_at=lab.completed_at,
            visit=VisitMapper.to_dto(lab.visit) if hasattr(lab, 'visit') and lab.visit else None,
            patient=PatientMapper.to_dto(lab.patient) if hasattr(lab, 'patient') and lab.patient else None,
            requester=UserMapper.to_dto(lab.requester) if hasattr(lab, 'requester') and lab.requester else None,
            technician=UserMapper.to_dto(lab.technician) if hasattr(lab, 'technician') and lab.technician else None,
            reports=[LaboratoryMapper.to_report_dto(r) for r in lab.reports] if hasattr(lab, 'reports') and lab.reports else []
        )

    @staticmethod
    def to_model(dto: LaboratoryCreateRequest) -> Laboratory:
        lab = Laboratory()
        lab.visit_id = dto.visit_id
        lab.patient_id = dto.patient_id
        lab.lab_technician_id = dto.lab_technician_id
        lab.priority = dto.priority or "NORMAL"
        lab.sample_type = dto.sample_type
        lab.remarks = dto.remarks
        lab.test_status = "PENDING"
        if dto.requested_by is not None:
            lab.requested_by = dto.requested_by
        return lab

    @staticmethod
    def update_model(lab: Laboratory, dto: LaboratoryUpdateRequest) -> Laboratory:
        if dto.test_status is not None:
            lab.test_status = dto.test_status
        if dto.priority is not None:
            lab.priority = dto.priority
        if dto.lab_technician_id is not None:
            lab.lab_technician_id = dto.lab_technician_id
        if dto.sample_type is not None:
            lab.sample_type = dto.sample_type
        if dto.remarks is not None:
            lab.remarks = dto.remarks
        if dto.sample_collected_at is not None:
            lab.sample_collected_at = dto.sample_collected_at
        return lab

    @staticmethod
    def to_report_dto(report: LabReport) -> LabReportResponse:
        if not report:
            return None
        return LabReportResponse(
            lab_report_id=report.lab_report_id,
            lab_id=report.lab_id,
            test_id=report.test_id,
            patient_id=report.patient_id,
            doctor_id=report.doctor_id,
            verified_by=report.verified_by,
            report_number=report.report_number,
            result=report.result,
            unit=report.unit,
            reference_range=report.reference_range,
            is_abnormal=report.is_abnormal,
            remarks=report.remarks,
            verified_at=report.verified_at,
            report_file=report.report_file,
            created_at=report.created_at,
            test=LaboratoryMapper.to_catalog_dto(report.test) if hasattr(report, 'test') and report.test else None,
            patient=PatientMapper.to_dto(report.patient) if hasattr(report, 'patient') and report.patient else None,
            doctor=UserMapper.to_dto(report.doctor) if hasattr(report, 'doctor') and report.doctor else None,
            verifier=UserMapper.to_dto(report.verifier) if hasattr(report, 'verifier') and report.verifier else None
        )

    @staticmethod
    def to_report_model(dto: LabReportCreateRequest) -> LabReport:
        report = LabReport()
        report.test_id = dto.test_id
        report.result = dto.result
        report.unit = dto.unit
        report.reference_range = dto.reference_range
        report.is_abnormal = bool(dto.is_abnormal)
        report.remarks = dto.remarks
        if dto.lab_id is not None:
            report.lab_id = dto.lab_id
        if dto.patient_id is not None:
            report.patient_id = dto.patient_id
        if dto.doctor_id is not None:
            report.doctor_id = dto.doctor_id
        if dto.report_number is not None:
            report.report_number = dto.report_number
        return report

    @staticmethod
    def to_catalog_dto(catalog: LabTestCatalog) -> LabTestCatalogResponse:
        if not catalog:
            return None
        return LabTestCatalogResponse(
            test_id=catalog.test_id,
            test_code=catalog.test_code,
            test_name=catalog.test_name,
            category=catalog.category,
            sample_type=catalog.sample_type,
            unit=catalog.unit,
            reference_range=catalog.reference_range,
            normal_min=catalog.normal_min,
            normal_max=catalog.normal_max,
            default_price=catalog.default_price,
            description=catalog.description,
            is_active=catalog.is_active,
            created_at=catalog.created_at
        )

    @staticmethod
    def to_catalog_model(dto: LabTestCatalogCreateRequest) -> LabTestCatalog:
        catalog = LabTestCatalog()
        catalog.test_code = dto.test_code
        catalog.test_name = dto.test_name
        catalog.category = dto.category
        catalog.sample_type = dto.sample_type
        catalog.unit = dto.unit
        catalog.reference_range = dto.reference_range
        catalog.normal_min = dto.normal_min
        catalog.normal_max = dto.normal_max
        catalog.default_price = dto.default_price
        catalog.description = dto.description
        catalog.is_active = True
        return catalog

    @staticmethod
    def update_catalog_model(catalog: LabTestCatalog, dto: LabTestCatalogUpdateRequest) -> LabTestCatalog:
        catalog.test_code = dto.test_code
        catalog.test_name = dto.test_name
        catalog.category = dto.category
        catalog.sample_type = dto.sample_type
        catalog.unit = dto.unit
        catalog.reference_range = dto.reference_range
        catalog.normal_min = dto.normal_min
        catalog.normal_max = dto.normal_max
        catalog.default_price = dto.default_price
        catalog.description = dto.description
        catalog.is_active = dto.is_active
        return catalog
