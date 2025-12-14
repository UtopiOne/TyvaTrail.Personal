import json

from django.db.models import Q
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
from django.core.paginator import Paginator
from .models import Poi, PoiPhoto, Review
from .forms import PoiFilterForm



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


def poi_list(request):
    form = PoiFilterForm(request.GET or None)
    qs = Poi.objects.all()

    if form.is_valid():
        q = form.cleaned_data.get("q")
        poi_type = form.cleaned_data.get("type")
        region = form.cleaned_data.get("region")
        season = form.cleaned_data.get("season")
        price_level = form.cleaned_data.get("price_level")
        physical_level = form.cleaned_data.get("physical_level")

        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(short_description__icontains=q))
        if poi_type:
            qs = qs.filter(type=poi_type)
        if region:
            qs = qs.filter(region__icontains=region)
        if season:
            qs = qs.filter(season=season)
        if price_level:
            qs = qs.filter(price_level=price_level)
        if physical_level:
            qs = qs.filter(physical_level=physical_level)

    qs = qs.order_by("-avg_rating", "base_cost", "name")

    paginator = Paginator(qs, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)
    base_qs = params.urlencode()

    return render(
        request,
        "tours/poi_list.html",
        {"form": form, "page_obj": page_obj, "base_qs": base_qs},
    )


def poi_detail(request, pk: int):
    poi = get_object_or_404(Poi, pk=pk)
    photos = PoiPhoto.objects.filter(poi=poi).order_by("-created_at")
    reviews = Review.objects.filter(poi=poi).select_related("user").order_by("-created_at")

    map_point = None
    if poi.latitude is not None and poi.longitude is not None:
        map_point = {
            "lat": float(poi.latitude),
            "lng": float(poi.longitude),
            "name": poi.name,
        }

    context = {
        "poi": poi,
        "photos": photos,
        "reviews": reviews,
        "map_point_json": json.dumps(map_point, cls=DjangoJSONEncoder) if map_point else "",
        "yandex_maps_api_key": settings.YANDEX_MAPS_API_KEY,
    }
    return render(request, "tours/poi_detail.html", context)


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
