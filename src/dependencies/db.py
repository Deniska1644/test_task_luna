"""Зависимости для доступа к БД: сессия SQLAlchemy."""

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Возвращает асинхронную сессию БД из контекста приложения."""
    async with request.app.state.async_session_maker() as session:
        yield session
