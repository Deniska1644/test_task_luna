"""Базовый репозиторий: общий CRUD для асинхронных сессий SQLAlchemy."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepo(Generic[ModelT]):
    """Базовый репозиторий с get_by_id, get_all, add, delete, exists_by_id."""

    def __init__(self, session: AsyncSession, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    async def get_by_id(self, id: int) -> ModelT | None:
        """Возвращает сущность по первичному ключу или None."""
        return await self._session.get(self._model, id)

    async def get_all(
        self,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[ModelT]:
        """Список сущностей с опциональными limit и offset."""
        stmt = select(self._model).offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.scalars(stmt)
        return list(result.all())

    async def add(self, entity: ModelT) -> ModelT:
        """Сохраняет сущность и возвращает её (id проставляется после flush)."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        """Удаляет сущность."""
        await self._session.delete(entity)
        await self._session.flush()

    async def exists_by_id(self, id: int) -> bool:
        """Возвращает True, если сущность с данным id существует."""
        stmt = select(self._model).where(self._model.id == id)
        result = await self._session.scalar(stmt)
        return result is not None
