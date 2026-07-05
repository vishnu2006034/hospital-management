"""Medicine repository for database operations."""

from typing import List, Optional

from flask_sqlalchemy.pagination import Pagination

from app import db
from app.models.medicine import Medicine
from app.repositories.base_repository import BaseRepository


class MedicineRepository(BaseRepository[Medicine]):
    """Repository for Medicine entity database operations."""

    def __init__(self) -> None:
        super().__init__(Medicine)
    
    def search(
        self, search: Optional[str], page: int = 1, per_page: int = 15
    )->Pagination[Medicine]:
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
        return query.paginate(page=page, per_page=per_page, error_out=False)


medicine_repository: MedicineRepository = MedicineRepository()
