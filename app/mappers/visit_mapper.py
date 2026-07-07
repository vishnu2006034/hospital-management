from app.models.visit import Visit
from app.dtos.visit import VisitResponse, VisitCreateRequest, VisitUpdateRequest
from app.mappers.patient_mapper import PatientMapper
from app.mappers.user_mapper import UserMapper

class VisitMapper:
    @staticmethod
    def to_dto(visit: Visit) -> VisitResponse:
        if not visit:
            return None
        return VisitResponse(
            visit_id=visit.visit_id,
            patient_id=visit.patient_id,
            doctor_id=visit.doctor_id,
            visit_type=visit.visit_type,
            visit_status=visit.visit_status,
            visit_date=visit.visit_date,
            admission_date=visit.admission_date,
            discharge_date=visit.discharge_date,
            chief_complaint=visit.chief_complaint,
            diagnosis=visit.diagnosis,
            treatment_plan=visit.treatment_plan,
            notes=visit.notes,
            height=visit.height,
            weight=visit.weight,
            temperature=visit.temperature,
            blood_pressure=visit.blood_pressure,
            pulse_rate=visit.pulse_rate,
            oxygen_level=visit.oxygen_level,
            created_at=visit.created_at,
            updated_at=visit.updated_at,
            patient=PatientMapper.to_dto(visit.patient) if hasattr(visit, 'patient') and visit.patient else None,
            doctor=UserMapper.to_dto(visit.doctor) if hasattr(visit, 'doctor') and visit.doctor else None
        )

    @staticmethod
    def to_model(dto: VisitCreateRequest) -> Visit:
        visit = Visit()
        visit.patient_id = dto.patient_id
        visit.doctor_id = dto.doctor_id
        visit.visit_type = dto.visit_type or 'OUTPATIENT'
        visit.visit_status = dto.visit_status or 'OPEN'
        visit.chief_complaint = dto.chief_complaint
        visit.diagnosis = dto.diagnosis
        visit.treatment_plan = dto.treatment_plan
        visit.notes = dto.notes
        visit.height = dto.height
        visit.weight = dto.weight
        visit.temperature = dto.temperature
        visit.blood_pressure = dto.blood_pressure
        visit.pulse_rate = dto.pulse_rate
        visit.oxygen_level = dto.oxygen_level
        if dto.admission_date:
            visit.admission_date = dto.admission_date
        return visit

    @staticmethod
    def update_model(visit: Visit, dto: VisitUpdateRequest) -> Visit:
        if dto.visit_type is not None:
            visit.visit_type = dto.visit_type
        if dto.visit_status is not None:
            visit.visit_status = dto.visit_status
        visit.chief_complaint = dto.chief_complaint
        visit.diagnosis = dto.diagnosis
        visit.treatment_plan = dto.treatment_plan
        visit.notes = dto.notes
        visit.height = dto.height
        visit.weight = dto.weight
        visit.temperature = dto.temperature
        visit.blood_pressure = dto.blood_pressure
        visit.pulse_rate = dto.pulse_rate
        visit.oxygen_level = dto.oxygen_level
        
        # None values are allowed to clear dates
        visit.admission_date = dto.admission_date
        visit.discharge_date = dto.discharge_date
        return visit
