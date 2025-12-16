from __future__ import annotations

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.db.models import Max

from ..models import Route, RoutePoint


def delete_route_point(*, user, route_pk: int, point_pk: int) -> Route:
    route = get_object_or_404(Route, pk=route_pk, user=user)
    point = get_object_or_404(RoutePoint, pk=point_pk, route=route)
    day = point.day_number

    with transaction.atomic():
        point.delete()
        _reindex_day(route, day)
        _recalc_route_totals(route)

    return route


def move_route_point_up(*, user, route_pk: int, point_pk: int) -> Route:
    route = get_object_or_404(Route, pk=route_pk, user=user)
    point = get_object_or_404(RoutePoint, pk=point_pk, route=route)

    neighbor = (
        RoutePoint.objects.filter(
            route=route,
            day_number=point.day_number,
            order_index__lt=point.order_index,
        )
        .order_by("-order_index", "-id")
        .first()
    )
    if not neighbor:
        return route

    with transaction.atomic():
        point.order_index, neighbor.order_index = neighbor.order_index, point.order_index
        point.save(update_fields=["order_index"])
        neighbor.save(update_fields=["order_index"])

    return route


def move_route_point_down(*, user, route_pk: int, point_pk: int) -> Route:
    route = get_object_or_404(Route, pk=route_pk, user=user)
    point = get_object_or_404(RoutePoint, pk=point_pk, route=route)

    neighbor = (
        RoutePoint.objects.filter(
            route=route,
            day_number=point.day_number,
            order_index__gt=point.order_index,
        )
        .order_by("order_index", "id")
        .first()
    )
    if not neighbor:
        return route

    with transaction.atomic():
        point.order_index, neighbor.order_index = neighbor.order_index, point.order_index
        point.save(update_fields=["order_index"])
        neighbor.save(update_fields=["order_index"])

    return route


def add_route_point(*, user, route_pk: int, poi, day_number: int, note: str = "") -> Route:
    route = get_object_or_404(Route, pk=route_pk, user=user)

    # нормализуем день
    day_number = max(1, min(int(day_number), route.days_count))

    next_order = (
        RoutePoint.objects
        .filter(route=route, day_number=day_number)
        .aggregate(m=Max("order_index"))["m"] or 0
    ) + 1

    with transaction.atomic():
        RoutePoint.objects.create(
            route=route,
            poi=poi,
            day_number=day_number,
            order_index=next_order,
            note=note or "",
            visit_time_estimate=poi.visit_duration_hours,
        )
        # эти хелперы пусть остаются внутри сервиса
        _reindex_day(route, day_number)
        _recalc_route_totals(route)

    return route


def _reindex_day(route: Route, day_number: int) -> None:
    points = (
        RoutePoint.objects.filter(route=route, day_number=day_number)
        .order_by("order_index", "id")
    )
    for idx, p in enumerate(points, start=1):
        if p.order_index != idx:
            p.order_index = idx
            p.save(update_fields=["order_index"])


def _recalc_route_totals(route: Route) -> None:
    points = RoutePoint.objects.filter(route=route).select_related("poi")

    total_hours = 0.0
    total_cost = 0

    for p in points:
        total_hours += float(p.visit_time_estimate or 0)
        if p.poi.base_cost:
            total_cost += int(p.poi.base_cost)

    route.total_duration_hours = int(total_hours)
    route.total_cost = total_cost or None
    route.save(update_fields=["total_duration_hours", "total_cost"])
