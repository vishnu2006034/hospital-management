"""Base repository with generic CRUD operations."""

from typing import TypeVar, Generic, Type, List, Optional

from app import db

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Generic base repository providing common CRUD operations.

    This class encapsulates all database interaction patterns that are
    common across different entity repositories. Subclass this for
    entity-specific repositories.

    Type Parameters:
        T: The SQLAlchemy model class this repository manages.
    """

    def __init__(self, model: Type[T]) -> None:
        """Initialize the repository with a specific model class.

        Args:
            model: The SQLAlchemy model class to operate on.
        """
        self.model: Type[T] = model

    def get_by_id(self, id_value: int) -> Optional[T]:
        """Retrieve an entity by its primary key.

        Args:
            id_value: The primary key value to search for.

        Returns:
            The entity if found, None otherwise.
        """
        return db.session.get(self.model, id_value)

    def get_all(self) -> List[T]:
        """Retrieve all entities of this type.

        Returns:
            A list of all entities.
        """
        return self.model.query.all()

    def add(self, entity: T) -> T:
        """Add a new entity to the session.

        Args:
            entity: The entity instance to add.

        Returns:
            The added entity (with any generated fields populated).
        """
        db.session.add(entity)
        db.session.flush()
        return entity

    def update(self) -> None:
        """Flush changes to the database without committing."""
        db.session.flush()

    def delete(self, entity: T) -> None:
        """Delete an entity from the session.

        Args:
            entity: The entity instance to delete.
        """
        db.session.delete(entity)

    def commit(self) -> None:
        """Commit the current transaction."""
        db.session.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        db.session.rollback()

    def filter_by(self, **kwargs) -> List[T]:
        """Filter entities by keyword arguments.

        Args:
            **kwargs: Column name-value pairs to filter by.

        Returns:
            A list of matching entities.
        """
        return self.model.query.filter_by(**kwargs).all()

    def filter_by_first(self, **kwargs) -> Optional[T]:
        """Filter entities by keyword arguments and return the first match.

        Args:
            **kwargs: Column name-value pairs to filter by.

        Returns:
            The first matching entity, or None.
        """
        return self.model.query.filter_by(**kwargs).first()

    def exists(self, **kwargs) -> bool:
        """Check if an entity exists matching the given criteria.

        Args:
            **kwargs: Column name-value pairs to filter by.

        Returns:
            True if at least one matching entity exists.
        """
        return self.model.query.filter_by(**kwargs).first() is not None

    def count(self) -> int:
        """Count all entities of this type.

        Returns:
            The total number of entities.
        """
        return self.model.query.count()

    def paginate(self, query, page: int = 1, per_page: int = 15):
        """Execute a paginated query.

        Args:
            query: The SQLAlchemy query to paginate.
            page: The page number (1-indexed).
            per_page: Number of items per page.

        Returns:
            A pagination object.
        """
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def ilike_filter(self, column, search_term: str):
        """Create an ILIKE filter for case-insensitive search.

        Args:
            column: The database column to search.
            search_term: The search term to match.

        Returns:
            A SQLAlchemy ILIKE filter expression.
        """
        return column.ilike(f'%{search_term}%')
