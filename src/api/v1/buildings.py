"""Эндпоинты по зданиям."""

from fastapi import APIRouter, Depends

from dependencies import get_organization_service
from schemas import BuildingWithOrganizationsResponse
from services import OrganizationService

router = APIRouter(prefix="/buildings", tags=["Здания"])


@router.get(
    "/{building_id}/organizations",
    response_model=BuildingWithOrganizationsResponse,
    summary="Здание и список организаций в нём",
)
async def get_building_with_organizations(
    building_id: int,
    limit: int | None = None,
    offset: int = 0,
    service: OrganizationService = Depends(get_organization_service),
) -> BuildingWithOrganizationsResponse:
    """Полная информация по зданию и список организаций, которые в нём находятся."""
    return await service.get_building_with_organizations(
        building_id, limit=limit, offset=offset
    )
