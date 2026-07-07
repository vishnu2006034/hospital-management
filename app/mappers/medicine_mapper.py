from app.models.medicine import Medicine
from app.dtos.medicine import MedicineResponse, MedicineCreateRequest, MedicineUpdateRequest

class MedicineMapper:
    @staticmethod
    def to_dto(medicine: Medicine) -> MedicineResponse:
        if not medicine:
            return None
        return MedicineResponse(
            medicine_id=medicine.medicine_id,
            medicine_name=medicine.medicine_name,
            generic_name=medicine.generic_name,
            category=medicine.category,
            dosage_form=medicine.dosage_form,
            strength=medicine.strength,
            manufacturer=medicine.manufacturer,
            unit_price=medicine.unit_price,
            created_at=medicine.created_at
        )

    @staticmethod
    def to_model(dto: MedicineCreateRequest) -> Medicine:
        medicine = Medicine()
        medicine.medicine_name = dto.medicine_name
        medicine.generic_name = dto.generic_name
        medicine.category = dto.category
        medicine.dosage_form = dto.dosage_form
        medicine.strength = dto.strength
        medicine.manufacturer = dto.manufacturer
        medicine.unit_price = dto.unit_price
        return medicine

    @staticmethod
    def update_model(medicine: Medicine, dto: MedicineUpdateRequest) -> Medicine:
        medicine.medicine_name = dto.medicine_name
        medicine.generic_name = dto.generic_name
        medicine.category = dto.category
        medicine.dosage_form = dto.dosage_form
        medicine.strength = dto.strength
        medicine.manufacturer = dto.manufacturer
        medicine.unit_price = dto.unit_price
        return medicine
