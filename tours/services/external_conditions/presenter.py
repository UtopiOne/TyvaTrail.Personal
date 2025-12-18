from __future__ import annotations

from django.utils import timezone

from .factory import get_external_conditions_provider
from ...models import Route, RoutePoint


def build_external_conditions_context(*, route: Route) -> dict:
    points = list(RoutePoint.objects.filter(route=route).select_related("poi").order_by("day_number", "order_index", "id"))
    provider = get_external_conditions_provider()
    data = provider.get_conditions(route=route, points=points)

    return {
        "external_conditions": data,
        "external_conditions_updated_at": timezone.localtime(timezone.now()),
    }
