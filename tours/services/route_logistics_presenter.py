from __future__ import annotations

from typing import Any

from .route_logistics import compute_logistics_for_days

def build_logistics_context(days: dict[int, list[Any]]) -> dict[str, Any]:
    day_stats, total_km, total_min = compute_logistics_for_days(days)

    day_blocks = []
    for day, points in days.items():
        st = day_stats.get(day) or {}
        dist = st.get("distance_km")
        tmin = st.get("time_minutes")
        day_blocks.append({
            "day": day,
            "points": points,
            "distance_km": dist,
            "time_minutes": tmin,
            "has_logistics": (dist is not None and tmin is not None),
        })

    return {
        "day_blocks": day_blocks,
        "logistics_total_km": total_km if total_km > 0 else None,
        "logistics_total_minutes": total_min if total_min > 0 else None,
    }
