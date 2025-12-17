from __future__ import annotations

from typing import Iterable, Optional

from ..models import (
    Route,
    RoutePoint,
    PoiType,
    PhysicalLevel,
    Season,
    UserProfile,
)


def _uniq(items: list[str]) -> list[str]:
    seen = set()
    out = []
    for x in items:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out


def build_equipment(*, points: Iterable[RoutePoint], profile: Optional[UserProfile]) -> str:
    base = [
        "Паспорт/документы, банковская карта, немного наличных",
        "Телефон + powerbank, зарядка",
        "Вода, перекус",
        "Аптечка (минимум: пластыри, обезболивающее, антисептик)",
    ]

    has_nature = False
    has_guesthouse = False
    has_food = False
    has_hard = False

    seasons: set[str] = set()

    for rp in points:
        poi = getattr(rp, "poi", None)
        if not poi:
            continue

        if poi.season and poi.season != Season.YEAR_ROUND:
            seasons.add(poi.season)

        if poi.type == PoiType.NATURE:
            has_nature = True
        if poi.type == PoiType.GUESTHOUSE:
            has_guesthouse = True
        if poi.type == PoiType.FOOD:
            has_food = True

        if poi.physical_level == PhysicalLevel.HARD:
            has_hard = True

    if not seasons and profile:
        seasons.add(profile.preferred_season)

    items = base[:]

    if Season.WINTER in seasons:
        items += ["Тёплая одежда слоями, термобельё", "Перчатки/шапка, тёплые носки"]
    elif Season.SPRING in seasons or Season.AUTUMN in seasons:
        items += ["Ветровка/дождевик", "Тёплый слой (флиска/кофта)"]
    else:
        items += ["Головной убор", "Солнцезащитный крем", "Репеллент (комары/клещи)"]

    if has_nature or has_hard:
        items += ["Удобная треккинговая обувь", "Небольшой рюкзак", "Фонарик/налобник"]

    if has_guesthouse:
        items += ["Сменная одежда", "Тапочки/домашняя обувь"]

    if profile and getattr(profile, "with_children", False):
        items += ["Детские перекусы/вода", "Детская аптечка/влажные салфетки"]

    items = _uniq(items)
    return "\n".join(f"• {x}" for x in items)


def update_route_equipment(route: Route) -> None:
    points = RoutePoint.objects.filter(route=route).select_related("poi")
    profile = getattr(route.user, "profile", None)

    route.equipment = build_equipment(points=points, profile=profile)
    route.save(update_fields=["equipment"])
