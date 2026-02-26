from __future__ import annotations

from typing import TYPE_CHECKING, List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .organization import Organization


class Activity(Base):
    """Вид деятельности организации; дерево. Родитель/потомки и глубина (1–3) хранятся в activity_ownership."""

    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    organizations: Mapped[List["Organization"]] = relationship(
        secondary="organization_activities",
        back_populates="activities",
    )

