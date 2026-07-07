from app.models.prescription import Prescription
from app.dtos.prescription import PrescriptionResponse, PrescriptionCreateRequest
from app.mappers.inventory_mapper import InventoryMapper
from app.mappers.user_mapper import UserMapper

class PrescriptionMapper:
    @staticmethod
    def to_dto(prescription: Prescription) -> PrescriptionResponse:
        if not prescription:
            return None
        return PrescriptionResponse(
            prescription_id=prescription.prescription_id,
            visit_id=prescription.visit_id,
            inventory_id=prescription.inventory_id,
            prescribed_by=prescription.prescribed_by,
            dosage=prescription.dosage,
            frequency=prescription.frequency,
            duration=prescription.duration,
            quantity=prescription.quantity,
            instructions=prescription.instructions,
            created_at=prescription.created_at,
            inventory_batch=InventoryMapper.to_dto(prescription.inventory_batch) if hasattr(prescription, 'inventory_batch') and prescription.inventory_batch else None,
            prescriber=UserMapper.to_dto(prescription.prescriber) if hasattr(prescription, 'prescriber') and prescription.prescriber else None
        )

    @staticmethod
    def to_model(dto: PrescriptionCreateRequest) -> Prescription:
        prescription = Prescription()
        prescription.visit_id = dto.visit_id
        prescription.inventory_id = dto.inventory_id
        prescription.dosage = dto.dosage
        prescription.frequency = dto.frequency
        prescription.duration = dto.duration
        prescription.quantity = dto.quantity
        prescription.instructions = dto.instructions
        if dto.prescribed_by is not None:
            prescription.prescribed_by = dto.prescribed_by
        return prescription
