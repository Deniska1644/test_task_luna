"""Геопоиск: здания и организации по радиусу или прямоугольнику."""

from fastapi import APIRouter, Depends

from dependencies import get_organization_service
from schemas import BuildingWithOrganizationsResponse
from services import OrganizationService

router = APIRouter(prefix="/area", tags=["Геопоиск"])


@router.get(
    "/radius",
    response_model=list[BuildingWithOrganizationsResponse],
    summary="Поиск по радиусу от точки",
)
async def search_by_radius(
    lat: float,
    lon: float,
    radius_km: float = 1.0,
    limit: int | None = None,
    offset: int = 0,
    service: OrganizationService = Depends(get_organization_service),
) -> list[BuildingWithOrganizationsResponse]:
    """Здания и организации в заданном радиусе (км) от точки. lat, lon обязательны, radius_km по умолчанию 1 км."""
    return await service.list_buildings_and_organizations_in_radius(
        lat, lon, radius_km, limit=limit, offset=offset
    )


@router.get(
    "/bbox",
    response_model=list[BuildingWithOrganizationsResponse],
    summary="Поиск по прямоугольной области",
)
async def search_by_bbox(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    limit: int | None = None,
    offset: int = 0,
    service: OrganizationService = Depends(get_organization_service),
) -> list[BuildingWithOrganizationsResponse]:
    """Здания и организации внутри прямоугольной области (min_lat, max_lat, min_lon, max_lon)."""
    return await service.list_buildings_and_organizations_in_bbox(
        min_lat, max_lat, min_lon, max_lon, limit=limit, offset=offset
    )
