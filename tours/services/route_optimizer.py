from __future__ import annotations

from django.db import transaction

from .geo import haversine_km
from ..models import Route, RoutePoint


def _has_geo(rp: RoutePoint) -> bool:
    poi = rp.poi
    return poi and poi.latitude is not None and poi.longitude is not None


def _dist_km(a: RoutePoint, b: RoutePoint) -> float:
    pa, pb = a.poi, b.poi
    return haversine_km(float(pa.latitude), float(pa.longitude), float(pb.latitude), float(pb.longitude))


def _nearest_neighbor_order(points_geo: list[RoutePoint]) -> list[RoutePoint]:
    if len(points_geo) <= 2:
        return points_geo

    start = points_geo[0]
    ordered = [start]
    remaining = points_geo[1:]

    cur = start
    while remaining:
        best_i = 0
        best_d = float("inf")
        for i, cand in enumerate(remaining):
            d = _dist_km(cur, cand)
            if d < best_d:
                best_d = d
                best_i = i
        cur = remaining.pop(best_i)
        ordered.append(cur)

    return ordered


def _optimize_day(points: list[RoutePoint]) -> list[RoutePoint]:
    geo_points = [rp for rp in points if _has_geo(rp)]
    if len(geo_points) <= 2:
        return points

    ordered_geo = _nearest_neighbor_order(geo_points)
    it = iter(ordered_geo)

    out: list[RoutePoint] = []
    for rp in points:
        out.append(next(it) if _has_geo(rp) else rp)
    return out


@transaction.atomic
def optimize_route_points(route: Route) -> Route:
    qs = (
        RoutePoint.objects.select_for_update()
        .select_related("poi")
        .filter(route=route)
        .order_by("day_number", "order_index", "id")
    )

    by_day: dict[int, list[RoutePoint]] = {}
    for rp in qs:
        by_day.setdefault(rp.day_number, []).append(rp)

    for day, points in by_day.items():
        new_points = _optimize_day(points)
        for idx, rp in enumerate(new_points, start=1):
            if rp.order_index != idx:
                rp.order_index = idx
                rp.save(update_fields=["order_index"])

    return route
