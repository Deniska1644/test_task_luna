"""Эндпоинты по организациям."""

from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_organization_service
from schemas import (
    OrganizationDetailResponse,
    OrganizationResponse,
)
from services import OrganizationService

router = APIRouter(prefix="/organizations", tags=["Организации"])


@router.get(
    "",
    response_model=list[OrganizationResponse],
    summary="Список организаций с фильтром по виду деятельности",
)
async def list_organizations(
    activity_id: int | None = None,
    activity_name: str | None = None,
    service: OrganizationService = Depends(get_organization_service),
) -> list[OrganizationResponse]:
    """Список организаций по виду деятельности (передать ровно один: activity_id или activity_name).
    По имени возвращаются организации по данной активности и всем вложенным (например, «Еда» — Еда, Мясная продукция и т.д.).
    """
    if (activity_id is None) == (activity_name is None):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Укажи ровно один параметр: activity_id или activity_name",
        )
    return await service.list_organizations_by_activity(
        activity_id=activity_id,
        activity_name=activity_name,
    )


@router.get(
    "/search",
    response_model=list[OrganizationDetailResponse],
    summary="Поиск организаций по названию",
)
async def search_organizations(
    name: str,
    limit: int | None = None,
    service: OrganizationService = Depends(get_organization_service),
) -> list[OrganizationDetailResponse]:
    """Поиск по названию (подстрока, без учёта регистра). Возвращает полный объект как GET /organizations/{id}."""
    return await service.search_organizations_by_name(name, limit=limit)


@router.get(
    "/{organization_id}",
    response_model=OrganizationDetailResponse,
    summary="Детальная информация по организации",
)
async def get_organization(
    organization_id: int,
    service: OrganizationService = Depends(get_organization_service),
) -> OrganizationDetailResponse:
    """Полная информация: id, название, телефон, адреса (здания), виды деятельности деревом (корень → лист)."""
    return await service.get_organization_detail(organization_id)
