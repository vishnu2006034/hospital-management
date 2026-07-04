"""Custom exception classes.

Provides a hierarchy of application-specific exceptions for
clearer error handling and debugging.
"""

from typing import Any, Optional


class AppError(Exception):
    """Base exception for all application errors."""

    def __init__(
        self,
        message: str = 'An unexpected error occurred',
        code: int = 500,
        payload: Optional[dict] = None,
    ) -> None:
        self.message: str = message
        self.code: int = code
        self.payload: dict = payload or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to dictionary for API responses."""
        return {
            'error': self.__class__.__name__,
            'message': self.message,
            **self.payload,
        }


class NotFoundError(AppError):
    """Raised when a requested resource is not found."""

    def __init__(
        self,
        resource: str = 'Resource',
        resource_id: Any = None,
    ) -> None:
        message = f'{resource} not found'
        if resource_id is not None:
            message = f'{resource} with id {resource_id} not found'
        super().__init__(message=message, code=404)


class ValidationError(AppError):
    """Raised when data validation fails."""

    def __init__(
        self,
        message: str = 'Validation failed',
        errors: Optional[dict] = None,
    ) -> None:
        super().__init__(message=message, code=422)
        self.payload['errors'] = errors or {}


class AuthenticationError(AppError):
    """Raised when authentication fails."""

    def __init__(self, message: str = 'Authentication failed') -> None:
        super().__init__(message=message, code=401)


class AuthorizationError(AppError):
    """Raised when authorization fails."""

    def __init__(self, message: str = 'You do not have permission to perform this action') -> None:
        super().__init__(message=message, code=403)


class ConflictError(AppError):
    """Raised when a resource conflict occurs."""

    def __init__(self, message: str = 'Resource already exists') -> None:
        super().__init__(message=message, code=409)


class BusinessRuleError(AppError):
    """Raised when a business rule is violated."""

    def __init__(self, message: str = 'Business rule violation') -> None:
        super().__init__(message=message, code=422)


class InsufficientStockError(BusinessRuleError):
    """Raised when inventory stock is insufficient."""

    def __init__(
        self,
        medicine_name: str = 'Medicine',
        requested: int = 0,
        available: int = 0,
    ) -> None:
        message = (
            f'Insufficient stock for {medicine_name}: '
            f'requested {requested}, available {available}'
        )
        super().__init__(message=message)
        self.payload['medicine_name'] = medicine_name
        self.payload['requested'] = requested
        self.payload['available'] = available


class DuplicateResourceError(ConflictError):
    """Raised when trying to create a duplicate resource."""

    def __init__(self, resource: str = 'Resource', value: Any = None) -> None:
        message = f'{resource} already exists'
        if value is not None:
            message = f'{resource} with value "{value}" already exists'
        super().__init__(message=message)
