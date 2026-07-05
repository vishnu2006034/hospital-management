"""Base repository with generic CRUD operations."""

from typing import TypeVar, Generic, Type, Optional, Any

from app import db

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Generic base repository providing common CRUD operations.

    This class encapsulates all database interaction patterns that are
    common across different entity repositories. Subclass this for
    entity-specific repositories.
    """

    def __init__(self, model: Type[T]) -> None:
        self.model: Type[T] = model

    def get_by_id(self, id_value: int) -> Optional[T]:
        return db.session.get(self.model, id_value)

    def add(self, entity: T) -> T:
        db.session.add(entity)
        db.session.flush()
        return entity

    def delete(self, entity: T) -> None:
        db.session.delete(entity)

    def commit(self) -> None:
        db.session.commit()

    def exists(self, **kwargs: Any) -> bool:
        return self.model.query.filter_by(**kwargs).first() is not None

    def rollback(self) -> None:
        self.session.rollback()

    def refresh(self, entity: T) -> None:
        self.session.refresh(entity)