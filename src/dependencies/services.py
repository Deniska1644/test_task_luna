"""Зависимости для сервисов: OrganizationService с сессией БД."""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.db import get_session
from services import OrganizationService


async def get_organization_service(
    session: AsyncSession = Depends(get_session),
) -> OrganizationService:
    """Возвращает экземпляр OrganizationService с текущей сессией."""
    return OrganizationService(session)
