from __future__ import annotations

from typing import Iterable

from .geo import haversine_km
from ..models import RoutePoint


DEFAULT_SPEED_KMPH = 60


def compute_logistics_for_points(points: Iterable[RoutePoint], speed_kmph: int = DEFAULT_SPEED_KMPH) -> tuple[float | None, int | None]:
    pts = list(points)
    if len(pts) < 2:
        return None, None

    total_km = 0.0
    segments = 0

    for a, b in zip(pts, pts[1:]):
        pa = a.poi
        pb = b.poi
        if not pa or not pb:
            continue
        if pa.latitude is None or pa.longitude is None:
            continue
        if pb.latitude is None or pb.longitude is None:
            continue

        km = haversine_km(float(pa.latitude), float(pa.longitude), float(pb.latitude), float(pb.longitude))
        total_km += km
        segments += 1

    if segments == 0:
        return None, None

    minutes = int(round((total_km / max(speed_kmph, 1)) * 60))
    return total_km, minutes


def compute_logistics_for_days(days: dict[int, list[RoutePoint]]) -> tuple[dict[int, dict], float | None, int | None]:
    day_stats: dict[int, dict] = {}
    total_km = 0.0
    total_min = 0
    any_segment = False

    for day, points in days.items():
        km, minutes = compute_logistics_for_points(points)
        day_stats[day] = {"distance_km": km, "time_minutes": minutes}

        if km is not None and minutes is not None:
            any_segment = True
            total_km += km
            total_min += minutes

    if not any_segment:
        return day_stats, None, None

    return day_stats, total_km, total_min
