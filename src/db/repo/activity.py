"""Репозиторий активностей: CRUD, проверки существования, дерево и владение."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Activity, ActivityOwnership
from db.repo.base import BaseRepo


class ActivityRepo(BaseRepo[Activity]):
    """Репозиторий видов деятельности (активностей)."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Activity)

    async def get_by_name(self, name: str) -> Activity | None:
        """Возвращает первую активность с указанным именем (без учёта регистра) или None."""
        stmt = select(Activity).where(Activity.name.ilike(name)).limit(1)
        result = await self._session.scalars(stmt)
        return result.one_or_none()

    async def get_owned_ids(self, owner_id: int) -> list[int]:
        """Все id активностей, которыми владеет owner_id (сама + потомки), из activity_ownership."""
        stmt = select(ActivityOwnership.owned_id).where(ActivityOwnership.owner_id == owner_id)
        result = await self._session.execute(stmt)
        return [row[0] for row in result.all()]

    async def fill_ownership_after_create(self, activity_id: int, parent_id: int | None) -> None:
        """Добавляет строки владения для новой активности: (id, id, 1) и (owner, id, d+1) для каждого предка."""
        self._session.add(ActivityOwnership(owner_id=activity_id, owned_id=activity_id, depth=1))
        if parent_id is None:
            await self._session.flush()
            return
        # All rows where owned_id = parent_id: each (owner_id, depth) gets (owner_id, activity_id, depth+1)
        stmt = select(ActivityOwnership).where(ActivityOwnership.owned_id == parent_id)
        result = await self._session.execute(stmt)
        for row in result.scalars().all():
            if row.depth < 3:
                self._session.add(
                    ActivityOwnership(owner_id=row.owner_id, owned_id=activity_id, depth=row.depth + 1)
                )
        await self._session.flush()

    async def create_activity(self, name: str, parent_id: int | None = None) -> Activity:
        """Создаёт активность и заполняет activity_ownership (глубина 1–3)."""
        activity = Activity(name=name)
        await self.add(activity)
        await self.fill_ownership_after_create(activity.id, parent_id)
        return activity

    async def get_paths_from_ownership(
        self, leaf_ids: list[int]
    ) -> list[list[tuple[int, str]]]:
        """Пути от корня к листу в виде списка (id, name) по каждому leaf_id из activity_ownership и activities."""
        if not leaf_ids:
            return []
        stmt = (
            select(ActivityOwnership.owned_id, ActivityOwnership.owner_id, ActivityOwnership.depth, Activity.name)
            .join(Activity, Activity.id == ActivityOwnership.owner_id)
            .where(ActivityOwnership.owned_id.in_(leaf_ids))
            .order_by(ActivityOwnership.owned_id, ActivityOwnership.depth.desc())
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        by_owned: dict[int, list[tuple[int, str]]] = {aid: [] for aid in leaf_ids}
        for owned_id, owner_id, _depth, name in rows:
            by_owned[owned_id].append((owner_id, name))
        return [by_owned[aid] for aid in leaf_ids]
