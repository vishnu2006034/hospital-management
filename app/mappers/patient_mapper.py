from app.models.patient import Patient
from app.dtos.patient import PatientResponse, PatientCreateRequest, PatientUpdateRequest

class PatientMapper:
    @staticmethod
    def to_dto(patient: Patient) -> PatientResponse:
        if not patient:
            return None
        # Handle potential tuple bug where patient_number might have been stored as a tuple
        pat_num = patient.patient_number
        if isinstance(pat_num, tuple) and pat_num:
            pat_num = pat_num[0]
        return PatientResponse(
            patient_id=patient.patient_id,
            patient_number=pat_num,
            first_name=patient.first_name,
            last_name=patient.last_name,
            gender=patient.gender,
            dob=patient.dob,
            blood_group=patient.blood_group,
            phone=patient.phone,
            email=patient.email,
            address=patient.address,
            emergency_contact_name=patient.emergency_contact_name,
            emergency_contact_phone=patient.emergency_contact_phone,
            allergies=patient.allergies,
            medical_history=patient.medical_history,
            created_at=patient.created_at,
            updated_at=patient.updated_at,
            full_name=patient.full_name
        )

    @staticmethod
    def to_model(dto: PatientCreateRequest) -> Patient:
        patient = Patient()
        patient.first_name = dto.first_name
        patient.last_name = dto.last_name
        patient.gender = dto.gender
        patient.dob = dto.dob
        patient.blood_group = dto.blood_group
        patient.phone = dto.phone
        patient.email = dto.email
        patient.address = dto.address
        patient.emergency_contact_name = dto.emergency_contact_name
        patient.emergency_contact_phone = dto.emergency_contact_phone
        patient.allergies = dto.allergies
        patient.medical_history = dto.medical_history
        return patient

    @staticmethod
    def update_model(patient: Patient, dto: PatientUpdateRequest) -> Patient:
        patient.first_name = dto.first_name
        patient.last_name = dto.last_name
        patient.gender = dto.gender
        patient.dob = dto.dob
        patient.blood_group = dto.blood_group
        patient.phone = dto.phone
        patient.email = dto.email
        patient.address = dto.address
        patient.emergency_contact_name = dto.emergency_contact_name
        patient.emergency_contact_phone = dto.emergency_contact_phone
        patient.allergies = dto.allergies
        patient.medical_history = dto.medical_history
        return patient
