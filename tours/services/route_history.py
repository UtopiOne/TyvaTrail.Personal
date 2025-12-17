from ..models import RouteGeneration

def log_route_generation(*, user, route, days_count: int, max_budget):
    RouteGeneration.objects.create(
        user=user,
        route=route,
        days_count=days_count,
        max_budget=max_budget,
    )
