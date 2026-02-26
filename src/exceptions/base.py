"""Базовое исключение API: доменные ошибки, преобразуемые в HTTP-ответы."""

from __future__ import annotations

from fastapi import HTTPException


class APIException(Exception):
    """Базовый класс для бизнес/API-ошибок; преобразование в HTTP через to_http_exception()."""

    def to_http_exception(self) -> HTTPException:
        """Создаёт HTTPException для ответа FastAPI."""
        raise NotImplementedError("Подклассы должны реализовать to_http_exception")
