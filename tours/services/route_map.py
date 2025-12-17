from __future__ import annotations

import json

from django.core.serializers.json import DjangoJSONEncoder

from ..models import Route, RoutePoint


def get_route_map_points(route: Route) -> list[dict]:
    qs = (
        RoutePoint.objects
        .filter(
            route=route,
            poi__latitude__isnull=False,
            poi__longitude__isnull=False,
        )
        .select_related("poi")
        .order_by("day_number", "order_index", "id")
    )

    points: list[dict] = []
    for rp in qs:
        poi = rp.poi
        points.append(
            {
                "lat": float(poi.latitude),
                "lng": float(poi.longitude),
                "name": poi.name,
                "day": rp.day_number,
                "order": rp.order_index,
            }
        )
    return points


def get_route_map_points_json(route: Route) -> str:
    return json.dumps(get_route_map_points(route), cls=DjangoJSONEncoder)
