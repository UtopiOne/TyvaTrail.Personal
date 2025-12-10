from typing import Optional

from ..models import (
    Poi,
    Route,
    RoutePoint,
    UserProfile,
    PhysicalLevel,
    PriceLevel,
    Season,
)


def build_route_for_user(
        user,
        days_count: int,
        max_budget: Optional[int] = None,
) -> Route:
    profile: UserProfile = user.profile

    qs = Poi.objects.all()
    qs = qs.filter(season__in=[profile.preferred_season, Season.YEAR_ROUND])

    if profile.physical_level == PhysicalLevel.EASY:
        qs = qs.exclude(physical_level=PhysicalLevel.HARD)

    if profile.budget_level == PriceLevel.LOW:
        qs = qs.filter(price_level__in=[PriceLevel.LOW, PriceLevel.MEDIUM])
    elif profile.budget_level == PriceLevel.MEDIUM:
        qs = qs.filter(price_level__in=[PriceLevel.LOW, PriceLevel.MEDIUM, PriceLevel.HIGH])

    qs = qs.order_by("-avg_rating", "base_cost")

    route = Route.objects.create(
        user=user,
        name="Индивидуальный маршрут по Тыве",
        days_count=days_count,
    )

    current_day = 1
    current_hours = 0.0
    order_index = 1
    total_cost = 0

    for poi in qs:
        visit_hours = float(poi.visit_duration_hours or 2.0)

        if current_hours + visit_hours > 8.0:
            current_day += 1
            current_hours = 0.0
            order_index = 1
            if current_day > days_count:
                break

        RoutePoint.objects.create(
            route=route,
            poi=poi,
            day_number=current_day,
            order_index=order_index,
            visit_time_estimate=visit_hours,
        )
        current_hours += visit_hours
        order_index += 1

        if poi.base_cost:
            total_cost += poi.base_cost

        if max_budget is not None and total_cost > max_budget:
            break

    route.total_duration_hours = int((current_day - 1) * 8 + current_hours)
    route.total_cost = total_cost or None
    route.save()

    return route
