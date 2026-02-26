"""Custom exceptions for business logic; map to HTTP via exception handler."""

from .base import APIException
from .errors import (
    AccessDeniedError,
    ConflictError,
    InternalError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    "APIException",
    "NotFoundError",
    "AccessDeniedError",
    "ValidationError",
    "ConflictError",
    "InternalError",
]
