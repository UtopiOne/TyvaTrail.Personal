import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RouteRequestForm, UserProfileForm
from .models import Route
from .services.route_builder import build_route_for_user
from .services.route_queries import get_user_routes, get_route_days


def home(request):
    if not request.user.is_authenticated:
        return render(request, "tours/home.html", {"form": None})

    if request.method == "POST":
        form = RouteRequestForm(request.POST)
        if form.is_valid():
            days_count = form.cleaned_data["days_count"]
            max_budget = form.cleaned_data["max_budget"]
            route = build_route_for_user(
                user=request.user,
                days_count=days_count,
                max_budget=max_budget,
            )
            return redirect("route_detail", pk=route.pk)
    else:
        form = RouteRequestForm()

    return render(request, "tours/home.html", {"form": form})


@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile")
    else:
        form = UserProfileForm(instance=profile)
    return render(request, "tours/profile.html", {"form": form})


@login_required
def my_routes(request):
    routes = get_user_routes(request.user)
    return render(request, "tours/my_routes.html", {"routes": routes})


@login_required
def route_detail(request, pk: int):
    route = get_object_or_404(Route, pk=pk, user=request.user)

    days = get_route_days(route)

    all_points = []
    for day_points in days.values():
        all_points.extend(day_points)

    map_points = []
    for point in all_points:
        poi = point.poi
        if poi.latitude is None or poi.longitude is None:
            continue
        map_points.append(
            {
                "lat": float(poi.latitude),
                "lng": float(poi.longitude),
                "name": poi.name,
                "day": point.day_number,
                "order": point.order_index,
            }
        )

    context = {
        "route": route,
        "days": days,
        "map_points_json": json.dumps(map_points, cls=DjangoJSONEncoder),
        "yandex_maps_api_key": settings.YANDEX_MAPS_API_KEY,
    }
    return render(request, "tours/route_detail.html", context)


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/signup.html", {"form": form})
