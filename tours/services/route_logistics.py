from __future__ import annotations

from typing import Any

from .external_conditions import get_external_provider

def compute_logistics_for_days(days: dict[int, list[Any]]):
    provider = get_external_provider()

    day_stats: dict[int, dict[str, Any]] = {}
    total_km = 0.0
    total_min = 0

    for day, points in days.items():
        pts = []
        for p in points:
            poi = getattr(p, "poi", None)
            lat = getattr(poi, "latitude", None) if poi else None
            lon = getattr(poi, "longitude", None) if poi else None
            if lat is None or lon is None:
                continue
            pts.append((float(lat), float(lon)))

        if len(pts) < 2:
            day_stats[day] = {"distance_km": None, "time_minutes": None}
            continue

        d_km = 0.0
        t_min = 0
        for i in range(len(pts) - 1):
            lat1, lon1 = pts[i]
            lat2, lon2 = pts[i + 1]
            leg = provider.driving_leg(lat1, lon1, lat2, lon2)
            d_km += float(leg.distance_km)
            t_min += int(leg.duration_min)

        day_stats[day] = {"distance_km": d_km, "time_minutes": t_min}
        total_km += d_km
        total_min += t_min

    return day_stats, total_km, total_min
