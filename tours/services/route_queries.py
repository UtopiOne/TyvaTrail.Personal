from ..models import Route, RoutePoint, RouteGeneration


def get_user_routes(user):
    return user.routes.order_by("-created_at")


def get_route_days(route: Route):
    points = (
        RoutePoint.objects
        .filter(route=route)
        .select_related("poi")
        .order_by("day_number", "order_index")
    )

    days = {}
    for point in points:
        days.setdefault(point.day_number, []).append(point)

    return days


def get_user_history(user):
    return (
        RouteGeneration.objects
        .filter(user=user)
        .select_related("route")
        .order_by("-created_at")
    )