"""Схемы запросов и ответов для организаций и зданий."""

from __future__ import annotations

from .base import BaseSchema


class ActivityNode(BaseSchema):
    """Узел дерева активностей: id, название и вложенные дочерние узлы."""

    id: int
    name: str
    children: list[ActivityNode] = []


class OrganizationResponse(BaseSchema):
    """Организация в списковых ответах."""

    id: int
    name: str
    phone: str


class BuildingDetail(BaseSchema):
    """Адрес и координаты здания."""

    id: int
    country: str
    region: str | None = None
    city: str
    street: str
    house_number: str
    latitude: float | None = None
    longitude: float | None = None


class BuildingWithOrganizationsResponse(BaseSchema):
    """Полная информация по зданию и список организаций в нём."""

    building: BuildingDetail
    organizations: list[OrganizationResponse]


class OrganizationDetailResponse(BaseSchema):
    """Полная организация: id, название, телефон, адреса (здания), активности деревом (id, name, children)."""

    id: int
    name: str
    phone: str
    buildings: list[BuildingDetail]
    activities: list[ActivityNode]
