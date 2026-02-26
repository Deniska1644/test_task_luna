"""Репозиторий зданий: CRUD, проверка существования и геозапросы."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Building
from db.repo.base import BaseRepo


class BuildingRepo(BaseRepo[Building]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Building)

    async def get_in_radius(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Building]:
        """Здания с координатами в радиусе radius_km от точки (lat, lon). Формула Хаверсина."""
        dlat_rad = func.radians((Building.latitude - lat) / 2)
        dlon_rad = func.radians((Building.longitude - lon) / 2)
        a = (
            func.power(func.sin(dlat_rad), 2)
            + func.cos(func.radians(lat))
            * func.cos(func.radians(Building.latitude))
            * func.power(func.sin(dlon_rad), 2)
        )
        dist_km = 6371.0 * 2 * func.asin(func.sqrt(a))
        stmt = (
            select(Building)
            .where(
                Building.latitude.isnot(None),
                Building.longitude.isnot(None),
                dist_km <= radius_km,
            )
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.scalars(stmt)
        return list(result.all())

    async def get_in_bbox(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Building]:
        """Здания с координатами внутри заданного прямоугольника (bbox)."""
        stmt = (
            select(Building)
            .where(
                Building.latitude.isnot(None),
                Building.longitude.isnot(None),
                Building.latitude >= min_lat,
                Building.latitude <= max_lat,
                Building.longitude >= min_lon,
                Building.longitude <= max_lon,
            )
            .offset(offset)
        )
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self._session.scalars(stmt)
        return list(result.all())
