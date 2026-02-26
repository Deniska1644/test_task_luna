"""Репозиторий организаций: CRUD и запросы по активности и зданиям."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models import Organization, OrganizationActivity, OrganizationBuilding
from db.repo.base import BaseRepo


class OrganizationRepo(BaseRepo[Organization]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Organization)

    async def get_by_id_with_relations(self, org_id: int) -> Organization | None:
        stmt = (
            select(Organization)
            .where(Organization.id == org_id)
            .options(
                selectinload(Organization.buildings),
                selectinload(Organization.activities),
            )
        )
        result = await self._session.scalars(stmt)
        return result.unique().one_or_none()

    async def get_by_name_with_relations(
        self, name: str, *, limit: int | None = None
    ) -> list[Organization]:
        """Организации, в названии которых есть подстрока (без учёта регистра), с загрузкой зданий и активностей."""
        stmt = (
            select(Organization)
            .where(Organization.name.ilike(f"%{name}%"))
            .options(
                selectinload(Organization.buildings),
                selectinload(Organization.activities),
            )
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.scalars(stmt)
        return list(result.unique().all())

    async def get_by_activity_id(
        self,
        activity_id: int,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Organization]:
        stmt = (
            select(Organization)
            .join(OrganizationActivity, Organization.id == OrganizationActivity.organization_id)
            .where(OrganizationActivity.activity_id == activity_id)
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.scalars(stmt)
        return list(result.unique().all())

    async def get_by_activity_ids(
        self,
        activity_ids: list[int],
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Organization]:
        """Организации, у которых есть хотя бы одна из указанных активностей (без дублей)."""
        if not activity_ids:
            return []
        stmt = (
            select(Organization)
            .join(OrganizationActivity, Organization.id == OrganizationActivity.organization_id)
            .where(OrganizationActivity.activity_id.in_(activity_ids))
            .distinct()
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.scalars(stmt)
        return list(result.unique().all())

    async def get_by_building_id(
        self,
        building_id: int,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Organization]:
        """Организации, расположенные в указанном здании."""
        stmt = (
            select(Organization)
            .join(OrganizationBuilding, Organization.id == OrganizationBuilding.organization_id)
            .where(OrganizationBuilding.building_id == building_id)
            .distinct()
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.scalars(stmt)
        return list(result.unique().all())

    async def get_by_building_ids(
        self,
        building_ids: list[int],
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Organization]:
        """Организации, у которых есть хотя бы одно здание из списка (без дублей)."""
        if not building_ids:
            return []
        stmt = (
            select(Organization)
            .join(OrganizationBuilding, Organization.id == OrganizationBuilding.organization_id)
            .where(OrganizationBuilding.building_id.in_(building_ids))
            .distinct()
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.scalars(stmt)
        return list(result.unique().all())

    async def get_organizations_grouped_by_building(
        self, building_ids: list[int]
    ) -> dict[int, list[Organization]]:
        """Один запрос: для каждого building_id из списка — список организаций в этом здании."""
        if not building_ids:
            return {}
        stmt = (
            select(Organization, OrganizationBuilding.building_id)
            .select_from(Organization)
            .join(
                OrganizationBuilding,
                Organization.id == OrganizationBuilding.organization_id,
            )
            .where(OrganizationBuilding.building_id.in_(building_ids))
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        grouped: dict[int, list[Organization]] = {bid: [] for bid in building_ids}
        for org, building_id in rows:
            grouped[building_id].append(org)
        return grouped
