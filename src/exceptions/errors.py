"""Исключения API для бизнес-логики."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status

from .base import APIException


def _identifier_detail(value: Any) -> str | list[str]:
    """Normalize identifier for JSON-safe detail."""
    if isinstance(value, (list, tuple, set)):
        return [str(x) for x in value]
    return str(value)


class NotFoundError(APIException):
    """Ресурс не найден (404)."""

    def __init__(
        self,
        resource: str,
        identifier: Any,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.resource = resource
        self.identifier = _identifier_detail(identifier)
        self.extra = details or {}
        super().__init__(f"{resource} not found: {self.identifier}")

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"{self.resource} not found",
                "identifier": self.identifier,
                **self.extra,
            },
        )


class AccessDeniedError(APIException):
    """Forbidden (403)."""

    def __init__(
        self,
        reason: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.reason = reason
        self.extra = details or {}
        super().__init__(reason)

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Access denied",
                "reason": self.reason,
                **self.extra,
            },
        )


class ValidationError(APIException):
    """Validation / unprocessable entity (422)."""

    def __init__(
        self,
        field: str,
        message: str,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.field = field
        self.message = message
        self.extra = details or {}
        super().__init__(f"Validation error on {field}: {message}")

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": "Validation error",
                "field": self.field,
                "message": self.message,
                **self.extra,
            },
        )


class ConflictError(APIException):
    """Conflict (409)."""

    def __init__(
        self,
        resource: str,
        reason: str | None = None,
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.resource = resource
        self.reason = reason or "Conflict"
        self.extra = details or {}
        super().__init__(f"{resource}: {self.reason}")

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": f"{self.resource} conflict",
                "reason": self.reason,
                **self.extra,
            },
        )


class InternalError(APIException):
    """Internal server error (500)."""

    def __init__(
        self,
        message: str = "Internal error",
        *,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message = message
        self.extra = details or {}
        super().__init__(message)

    def to_http_exception(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "reason": self.message,
                **self.extra,
            },
        )
