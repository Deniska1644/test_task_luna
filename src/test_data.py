"""
Seed script: create test activities tree, buildings, and ~100 organizations with links.
Run from project root: python -m src.test_data
Or from src: python test_data.py (with PYTHONPATH=.. or run from parent)
"""

import asyncio
import random
import sys
from pathlib import Path

# ensure src (and project root) on path when run as script
if __name__ == "__main__":
    src_dir = str(Path(__file__).resolve().parent)
    root_dir = str(Path(__file__).resolve().parent.parent)
    for d in (src_dir, root_dir):
        if d not in sys.path:
            sys.path.insert(0, d)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from db.models import (
    Activity,
    ActivityOwnership,
    Building,
    Organization,
    OrganizationActivity,
    OrganizationBuilding,
)
from db.repo.activity import ActivityRepo

ENGINE = create_async_engine(settings.get_url_pg)
ASYNC_SESSION = sessionmaker(
    ENGINE, class_=AsyncSession, expire_on_commit=False
)


def _activity_tree() -> list[tuple[str | None, str]]:
    """(parent_name, name) for tree; None parent = root."""
    return [
        (None, "Еда"),
        ("Еда", "Мясная продукция"),
        ("Еда", "Молочная продукция"),
        (None, "Автомобили"),
        ("Автомобили", "Грузовые"),
        ("Автомобили", "Легковые"),
        ("Легковые", "Запчасти"),
        ("Легковые", "Аксессуары"),
        (None, "Услуги"),
        ("Услуги", "Ремонт"),
        ("Услуги", "Доставка"),
        (None, "Торговля"),
        ("Торговля", "Оптовая"),
        ("Торговля", "Розничная"),
    ]


def _building_rows() -> list[dict]:
    """Predefined building address parts."""
    cities = [
        ("Россия", "Новосибирская обл.", "Новосибирск"),
        ("Россия", "Новосибирская обл.", "Бердск"),
        ("Россия", "Новосибирская обл.", "Кольцово"),
        ("Россия", None, "Москва"),
        ("Россия", None, "Санкт-Петербург"),
    ]
    streets = [
        "Ленина", "Мира", "Советская", "Гагарина", "Победы",
        "Центральная", "Молодёжная", "Садовая", "Лесная", "Речная",
        "Блюхера", "Красный проспект", "Кирова", "Гоголя",
    ]
    rows = []
    for country, region, city in cities:
        for i, street in enumerate(streets[:10]):
            rows.append({
                "country": country,
                "region": region or "",
                "city": city,
                "street": f"ул. {street}",
                "house_number": f"{random.randint(1, 120)}/{random.randint(1, 5)}",
                "latitude": round(55.0 + random.uniform(0, 2), 6),
                "longitude": round(82.0 + random.uniform(0, 4), 6),
            })
    return rows


def _company_names(count: int) -> list[str]:
    """Generate ~count company names."""
    bases = [
        "Рога и Копыта", "СтройИнвест", "Молоко Сибири", "АвтоМир",
        "СибирьТорг", "ТехСервис", "Северный ветер", "Альфа",
        "Бета Плюс", "Гамма", "Дельта Сервис", "Омега", "Агро",
        "ТрансЛогистик", "МясоПром", "ХлебДар", "Чистый дом",
    ]
    forms = ["ООО", "ООО", "АО", "ИП"]
    out = []
    for i in range(count):
        base = random.choice(bases)
        form = random.choice(forms)
        if i < len(bases) * 2:
            out.append(f'{form} "{base}"')
        else:
            out.append(f'{form} "{base}" {i + 1}')
    random.shuffle(out)
    return out[:count]


def _phone() -> str:
    """Random phone string."""
    a = random.randint(100, 999)
    b = random.randint(10, 99)
    c = random.randint(10, 99)
    return f"8-{a}-{b}-{c}"


async def _get_leaf_ids(session: AsyncSession) -> list[int]:
    """Return activity ids that have no children (leaf nodes), using activity_ownership."""
    all_ids = [r[0] for r in (await session.execute(select(Activity.id))).all()]
    parent_ids = {
        r[0]
        for r in (
            await session.execute(
                select(ActivityOwnership.owner_id).where(ActivityOwnership.depth == 2).distinct()
            )
        ).all()
    }
    return [aid for aid in all_ids if aid not in parent_ids]


async def _ensure_activities(session: AsyncSession) -> list[int]:
    """Create activity tree and activity_ownership; return list of leaf activity ids."""
    existing = (await session.scalars(select(Activity))).all()
    if existing:
        return await _get_leaf_ids(session)
    repo = ActivityRepo(session)
    name_to_id: dict[str, int] = {}
    for parent_name, name in _activity_tree():
        parent_id = name_to_id.get(parent_name) if parent_name else None
        a = await repo.create_activity(name, parent_id)
        name_to_id[name] = a.id
    await session.commit()
    return await _get_leaf_ids(session)


async def _ensure_buildings(session: AsyncSession) -> list[int]:
    """Create buildings; return list of building ids."""
    existing = (await session.scalars(select(Building))).all()
    if existing:
        return [b.id for b in existing]
    for row in _building_rows():
        b = Building(**row)
        session.add(b)
    await session.flush()
    r = await session.scalars(select(Building.id))
    ids = list(r.all())
    await session.commit()
    return ids


async def _ensure_organizations(
    session: AsyncSession,
    building_ids: list[int],
    leaf_activity_ids: list[int],
    count: int = 100,
) -> None:
    """Create organizations and link to buildings and leaf activities."""
    existing = (await session.scalars(select(Organization))).all()
    if len(existing) >= count:
        return
    to_create = count - len(existing)
    names = _company_names(to_create)
    for name in names:
        org = Organization(name=name, phone=_phone())
        session.add(org)
        await session.flush()
        n_b = random.randint(1, min(3, len(building_ids)))
        n_a = random.randint(1, min(3, len(leaf_activity_ids)))
        for bid in random.sample(building_ids, n_b):
            session.add(OrganizationBuilding(organization_id=org.id, building_id=bid))
        for aid in random.sample(leaf_activity_ids, n_a):
            session.add(OrganizationActivity(organization_id=org.id, activity_id=aid))
    await session.commit()


async def run() -> None:
    """Create engine, run migrations assumption: tables exist; seed data."""
    async with ASYNC_SESSION() as session:
        leaf_ids = await _ensure_activities(session)
        building_ids = await _ensure_buildings(session)
        await _ensure_organizations(session, building_ids, leaf_ids, count=100)
    await ENGINE.dispose()
    print("Test data seeded: activities, buildings, 100 organizations.")


if __name__ == "__main__":
    asyncio.run(run())
