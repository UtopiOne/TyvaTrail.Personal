from ..models import Route, RoutePoint


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
