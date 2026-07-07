from app.models.doctor_report import DoctorReport
from app.dtos.report import ReportResponse, ReportCreateRequest, ReportUpdateRequest
from app.mappers.patient_mapper import PatientMapper
from app.mappers.user_mapper import UserMapper
from app.mappers.visit_mapper import VisitMapper

class ReportMapper:
    @staticmethod
    def to_dto(report: DoctorReport) -> ReportResponse:
        if not report:
            return None
        return ReportResponse(
            doctor_report_id=report.doctor_report_id,
            visit_id=report.visit_id,
            patient_id=report.patient_id,
            doctor_id=report.doctor_id,
            report_number=report.report_number,
            chief_complaint=report.chief_complaint,
            clinical_findings=report.clinical_findings,
            diagnosis=report.diagnosis,
            treatment_plan=report.treatment_plan,
            prescribed_medicines=report.prescribed_medicines,
            doctor_notes=report.doctor_notes,
            follow_up_required=report.follow_up_required,
            follow_up_date=report.follow_up_date,
            next_visit_reason=report.next_visit_reason,
            report_file=report.report_file,
            created_at=report.created_at,
            updated_at=report.updated_at,
            visit=VisitMapper.to_dto(report.visit) if hasattr(report, 'visit') and report.visit else None,
            patient=PatientMapper.to_dto(report.patient) if hasattr(report, 'patient') and report.patient else None,
            doctor=UserMapper.to_dto(report.doctor) if hasattr(report, 'doctor') and report.doctor else None
        )

    @staticmethod
    def to_model(dto: ReportCreateRequest) -> DoctorReport:
        report = DoctorReport()
        report.visit_id = dto.visit_id
        report.patient_id = dto.patient_id
        report.chief_complaint = dto.chief_complaint
        report.clinical_findings = dto.clinical_findings
        report.diagnosis = dto.diagnosis
        report.treatment_plan = dto.treatment_plan
        report.prescribed_medicines = dto.prescribed_medicines
        report.doctor_notes = dto.doctor_notes
        report.follow_up_required = bool(dto.follow_up_required)
        report.follow_up_date = dto.follow_up_date
        report.next_visit_reason = dto.next_visit_reason
        return report

    @staticmethod
    def update_model(report: DoctorReport, dto: ReportUpdateRequest) -> DoctorReport:
        report.chief_complaint = dto.chief_complaint
        report.clinical_findings = dto.clinical_findings
        report.diagnosis = dto.diagnosis
        report.treatment_plan = dto.treatment_plan
        report.prescribed_medicines = dto.prescribed_medicines
        report.doctor_notes = dto.doctor_notes
        report.follow_up_required = bool(dto.follow_up_required)
        report.follow_up_date = dto.follow_up_date
        report.next_visit_reason = dto.next_visit_reason
        return report
