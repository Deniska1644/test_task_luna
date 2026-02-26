"""Бизнес-логика организаций: возвращает Pydantic-схемы."""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from db.repo import ActivityRepo, BuildingRepo, OrganizationRepo
from exceptions import APIException, InternalError, NotFoundError
from schemas import (
    ActivityNode,
    BuildingDetail,
    BuildingWithOrganizationsResponse,
    OrganizationDetailResponse,
    OrganizationResponse,
)
from services.mixins import ActivityTreeMixin

logger = logging.getLogger(__name__)


class OrganizationService(ActivityTreeMixin):
    """Сервис организаций: список по активности, детали, поиск, геопоиск."""

    def __init__(self, session: AsyncSession) -> None:
        self._activity_repo = ActivityRepo(session)
        self._building_repo = BuildingRepo(session)
        self._org_repo = OrganizationRepo(session)

    async def list_organizations_by_activity(
        self,
        activity_id: int | None = None,
        activity_name: str | None = None,
    ) -> list[OrganizationResponse]:
        """Организации с данной активностью или потомками. Передать ровно один: activity_id или activity_name."""
        try:
            if activity_id is not None:
                if not await self._activity_repo.exists_by_id(activity_id):
                    raise NotFoundError("Activity", activity_id)
                resolved_id = activity_id
            else:
                activity = await self._activity_repo.get_by_name(activity_name)
                if activity is None:
                    raise NotFoundError("Activity", activity_name)
                resolved_id = activity.id
            owned_ids = await self._activity_repo.get_owned_ids(resolved_id)
            orgs = await self._org_repo.get_by_activity_ids(owned_ids)
            return [OrganizationResponse.model_validate(o) for o in orgs]
        except APIException:
            raise
        except Exception as e:
            logger.exception("list_organizations_by_activity failed: %s", e)
            raise InternalError("list_organizations_by_activity failed", details={"error": str(e)}) from e

    async def get_building_with_organizations(
        self, building_id: int, *, limit: int | None = None, offset: int = 0
    ) -> BuildingWithOrganizationsResponse:
        """Полная информация по зданию и организации в нём. NotFoundError, если здание не найдено."""
        try:
            building = await self._building_repo.get_by_id(building_id)
            if building is None:
                raise NotFoundError("Building", building_id)
            orgs = await self._org_repo.get_by_building_id(
                building_id, limit=limit, offset=offset
            )
            return BuildingWithOrganizationsResponse(
                building=BuildingDetail.model_validate(building),
                organizations=[OrganizationResponse.model_validate(o) for o in orgs],
            )
        except APIException:
            raise
        except Exception as e:
            logger.exception("get_building_with_organizations failed: %s", e)
            raise InternalError("get_building_with_organizations failed", details={"error": str(e)}) from e

    async def get_organization_detail(
        self, organization_id: int
    ) -> OrganizationDetailResponse:
        """Полная информация по организации с адресами и деревом активностей. NotFoundError, если не найдена."""
        try:
            org = await self._org_repo.get_by_id_with_relations(organization_id)
            if org is None:
                raise NotFoundError("Organization", organization_id)
            activity_paths = await self.get_activity_paths_with_ids(
                [a.id for a in org.activities], self._activity_repo
            )
            activity_trees = self.build_activities_tree_with_ids(activity_paths)
            activities = [ActivityNode.model_validate(n) for n in activity_trees]
            return OrganizationDetailResponse(
                id=org.id,
                name=org.name,
                phone=org.phone,
                buildings=[BuildingDetail.model_validate(b) for b in org.buildings],
                activities=activities,
            )
        except APIException:
            raise
        except Exception as e:
            logger.exception("get_organization_detail failed: %s", e)
            raise InternalError("get_organization_detail failed", details={"error": str(e)}) from e

    async def search_organizations_by_name(
        self, name: str, *, limit: int | None = None
    ) -> list[OrganizationDetailResponse]:
        """Поиск организаций по названию (подстрока, без учёта регистра). Возвращает полный объект как get_organization."""
        try:
            orgs = await self._org_repo.get_by_name_with_relations(name, limit=limit)
            result: list[OrganizationDetailResponse] = []
            for org in orgs:
                activity_paths = await self.get_activity_paths_with_ids(
                    [a.id for a in org.activities], self._activity_repo
                )
                activity_trees = self.build_activities_tree_with_ids(activity_paths)
                activities = [ActivityNode.model_validate(n) for n in activity_trees]
                result.append(
                    OrganizationDetailResponse(
                        id=org.id,
                        name=org.name,
                        phone=org.phone,
                        buildings=[BuildingDetail.model_validate(b) for b in org.buildings],
                        activities=activities,
                    )
                )
            return result
        except APIException:
            raise
        except Exception as e:
            logger.exception("search_organizations_by_name failed: %s", e)
            raise InternalError("search_organizations_by_name failed", details={"error": str(e)}) from e

    async def list_buildings_and_organizations_in_radius(
        self,
        lat: float,
        lon: float,
        radius_km: float,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[BuildingWithOrganizationsResponse]:
        """По каждому зданию в радиусе от точки — данные здания и список организаций в нём."""
        try:
            buildings = await self._building_repo.get_in_radius(
                lat, lon, radius_km, limit=limit, offset=offset
            )
            if not buildings:
                return []
            building_ids = [b.id for b in buildings]
            orgs_by_building = await self._org_repo.get_organizations_grouped_by_building(
                building_ids
            )
            return [
                BuildingWithOrganizationsResponse(
                    building=BuildingDetail.model_validate(b),
                    organizations=[
                        OrganizationResponse.model_validate(o)
                        for o in orgs_by_building.get(b.id, [])
                    ],
                )
                for b in buildings
            ]
        except APIException:
            raise
        except Exception as e:
            logger.exception("list_buildings_and_organizations_in_radius failed: %s", e)
            raise InternalError("list_buildings_and_organizations_in_radius failed", details={"error": str(e)}) from e

    async def list_buildings_and_organizations_in_bbox(
        self,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        *,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[BuildingWithOrganizationsResponse]:
        """По каждому зданию в прямоугольнике — данные здания и список организаций в нём."""
        try:
            buildings = await self._building_repo.get_in_bbox(
                min_lat, max_lat, min_lon, max_lon, limit=limit, offset=offset
            )
            if not buildings:
                return []
            building_ids = [b.id for b in buildings]
            orgs_by_building = await self._org_repo.get_organizations_grouped_by_building(
                building_ids
            )
            return [
                BuildingWithOrganizationsResponse(
                    building=BuildingDetail.model_validate(b),
                    organizations=[
                        OrganizationResponse.model_validate(o)
                        for o in orgs_by_building.get(b.id, [])
                    ],
                )
                for b in buildings
            ]
        except APIException:
            raise
        except Exception as e:
            logger.exception("list_buildings_and_organizations_in_bbox failed: %s", e)
            raise InternalError("list_buildings_and_organizations_in_bbox failed", details={"error": str(e)}) from e
