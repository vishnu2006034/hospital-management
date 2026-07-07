"""Medicine repository for database operations."""

from typing import List, Optional, Any

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.medicine import Medicine
from app.repositories.base_repository import BaseRepository
from app.repositories.interfaces.medicine_repository_interface import IMedicineRepository
from app.mappers.medicine_mapper import MedicineMapper
from app.dtos.medicine import MedicineResponse, MedicineCreateRequest


class MedicineRepository(BaseRepository[Medicine], IMedicineRepository):
    """Repository for Medicine entity database operations."""

    def __init__(self) -> None:
        super().__init__(Medicine)

    def get_by_id(self, id_value: int) -> Optional[MedicineResponse]:
        model = db.session.get(Medicine, id_value)
        return MedicineMapper.to_dto(model) if model else None

    def add(self, entity_dto: MedicineCreateRequest) -> MedicineResponse:
        model = MedicineMapper.to_model(entity_dto)
        db.session.add(model)
        db.session.flush()
        return MedicineMapper.to_dto(model)

    def delete(self, entity_id: int) -> None:
        model = db.session.get(Medicine, entity_id)
        if model:
            db.session.delete(model)
    
    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    ) -> Pagination:
        """Search medicine with pagination."""
        query = Medicine.query
        if search:
            query = query.filter(
                db.or_(
                    Medicine.medicine_name.ilike(f'%{search}%'),
                    Medicine.generic_name.ilike(f'%{search}%'),
                    Medicine.category.ilike(f'%{search}%'),
                )
            )
        query = query.order_by(Medicine.medicine_name)
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        pagination.items = [MedicineMapper.to_dto(m) for m in pagination.items]
        return pagination


medicine_repository: MedicineRepository = MedicineRepository()
