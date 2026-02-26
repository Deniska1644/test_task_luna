"""Служебные эндпоинты: health check."""

from fastapi import APIRouter

router = APIRouter(tags=["Служебные"])


@router.get("/health", include_in_schema=False)
def health() -> dict[str, str]:
    """Проверка доступности сервиса для балансировщиков и мониторинга."""
    return {"status": "ok"}
