from __future__ import annotations

from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Organization(Base):
    """Организация в справочнике."""

    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)

    buildings: Mapped[List["Building"]] = relationship(
        secondary="organization_buildings",
        back_populates="organizations",
    )
    activities: Mapped[List["Activity"]] = relationship(
        secondary="organization_activities",
        back_populates="organizations",
    )

