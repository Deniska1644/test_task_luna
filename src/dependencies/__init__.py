"""Зависимости FastAPI: сессия БД и сервисы."""

from .db import get_session
from .services import get_organization_service

__all__ = ["get_session", "get_organization_service"]
