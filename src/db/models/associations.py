from __future__ import annotations

from sqlalchemy import CheckConstraint, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ActivityOwnership(Base):
    """Кто чем владеет в дереве активностей: owner_id владеет owned_id на глубине (1=сам, 2=ребёнок, 3=внук)."""

    __tablename__ = "activity_ownership"
    __table_args__ = (
        UniqueConstraint("owner_id", "owned_id", name="uq_activity_ownership_owner_owned"),
        CheckConstraint("depth >= 1 AND depth <= 3", name="activity_ownership_depth_range"),
    )

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    owned_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    depth: Mapped[int] = mapped_column(Integer, nullable=False)


class OrganizationBuilding(Base):
    """Связь организаций и зданий (многие ко многим)."""

    __tablename__ = "organization_buildings"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    building_id: Mapped[int] = mapped_column(
        ForeignKey("buildings.id", ondelete="CASCADE"),
        primary_key=True,
    )


class OrganizationActivity(Base):
    """Связь организаций и видов деятельности (многие ко многим)."""

    __tablename__ = "organization_activities"

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"),
        primary_key=True,
    )
    activity_id: Mapped[int] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    )

