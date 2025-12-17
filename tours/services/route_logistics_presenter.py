from __future__ import annotations

from .route_logistics import compute_logistics_for_days


def build_logistics_context(days: dict) -> dict:
    day_stats, total_km, total_min = compute_logistics_for_days(days)

    day_blocks = []
    for day, points in days.items():
        st = day_stats.get(day) or {}
        day_blocks.append(
            {
                "day": day,
                "points": points,
                "distance_km": st.get("distance_km"),
                "time_minutes": st.get("time_minutes"),
            }
        )

    return {
        "day_blocks": day_blocks,
        "logistics_total_km": total_km,
        "logistics_total_minutes": total_min,
    }
