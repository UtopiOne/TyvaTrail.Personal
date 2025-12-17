import json

from django.db.models import Q
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Avg
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.urls import reverse
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.utils import timezone

from .models import  RoutePoint
from .forms import RouteRequestForm, UserProfileForm
from .models import Route
from .models import Poi, PoiPhoto, Review
from .forms import PoiFilterForm
from .forms import ReviewForm
from .forms import RoutePointAddForm

from .services.route_builder import build_route_for_user
from .services.route_queries import get_user_routes, get_route_days
from .services.route_editing import (
    add_route_point as svc_add_route_point,
    delete_route_point as svc_delete_route_point,
    move_route_point_up as svc_move_route_point_up,
    move_route_point_down as svc_move_route_point_down,
)


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

    user_review = None
    if request.user.is_authenticated:
        user_review = Review.objects.filter(poi=poi, user=request.user).first()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect("login")

        form = ReviewForm(request.POST, instance=user_review)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.poi = poi
            review.save()

            poi.avg_rating = Review.objects.filter(poi=poi).aggregate(v=Avg("rating"))["v"]
            poi.save(update_fields=["avg_rating"])

            return redirect("poi_detail", pk=poi.pk)
    else:
        form = ReviewForm(instance=user_review)

    photos = PoiPhoto.objects.filter(poi=poi).order_by("-created_at")
    reviews = Review.objects.filter(poi=poi).select_related("user").order_by("-created_at")

    map_point = None
    if poi.latitude is not None and poi.longitude is not None:
        map_point = {"lat": float(poi.latitude), "lng": float(poi.longitude), "name": poi.name}

    context = {
        "poi": poi,
        "photos": photos,
        "reviews": reviews,
        "review_form": form,
        "user_review": user_review,  # <-- ВАЖНО
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

    add_point_form = RoutePointAddForm(initial={"day_number": 1})

    share_url = None
    if route.is_shared:
        share_url = request.build_absolute_uri(
            reverse("route_share_detail", args=[route.share_uuid])
        )

    context = {
        "route": route,
        "days": days,
        "map_points_json": json.dumps(map_points, cls=DjangoJSONEncoder),
        "yandex_maps_api_key": settings.YANDEX_MAPS_API_KEY,
        "add_point_form": add_point_form,
        "share_url": share_url,
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


@login_required
@require_POST
def route_point_delete(request, route_pk: int, point_pk: int):
    route = svc_delete_route_point(user=request.user, route_pk=route_pk, point_pk=point_pk)
    return redirect("route_detail", pk=route.pk)


@login_required
@require_POST
def route_point_move_up(request, route_pk: int, point_pk: int):
    route = svc_move_route_point_up(user=request.user, route_pk=route_pk, point_pk=point_pk)
    return redirect("route_detail", pk=route.pk)


@login_required
@require_POST
def route_point_move_down(request, route_pk: int, point_pk: int):
    route = svc_move_route_point_down(user=request.user, route_pk=route_pk, point_pk=point_pk)
    return redirect("route_detail", pk=route.pk)


@login_required
@require_POST
def route_point_add(request, route_pk: int):
    form = RoutePointAddForm(request.POST)
    if form.is_valid():
        svc_add_route_point(
            user=request.user,
            route_pk=route_pk,
            poi=form.cleaned_data["poi"],
            day_number=form.cleaned_data["day_number"],
            note=form.cleaned_data.get("note", ""),
        )

    return redirect("route_detail", pk=route_pk)

@login_required
def route_print(request, pk: int):
    route = get_object_or_404(Route, pk=pk, user=request.user)
    days = get_route_days(route)

    context = {
        "route": route,
        "days": days,
    }
    return render(request, "tours/route_print.html", context)

@login_required
@require_POST
def route_share_toggle(request, pk: int):
    route = get_object_or_404(Route, pk=pk, user=request.user)
    route.is_shared = not route.is_shared
    route.save(update_fields=["is_shared"])
    return redirect("route_detail", pk=route.pk)


def route_share_detail(request, share_uuid):
    route = get_object_or_404(Route, share_uuid=share_uuid, is_shared=True)

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
    return render(request, "tours/route_share.html", context)


@staff_member_required
def admin_stats(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    total_poi = Poi.objects.count()
    total_routes = Route.objects.count()
    total_reviews = Review.objects.count()
    shared_routes = Route.objects.filter(is_shared=True).count()

    routes_7d = Route.objects.filter(created_at__gte=week_ago).count()
    reviews_7d = Review.objects.filter(created_at__gte=week_ago).count()

    top_poi_by_usage = (
        RoutePoint.objects
        .values("poi__id", "poi__name")
        .annotate(uses=Count("id"))
        .order_by("-uses")[:10]
    )

    top_poi_by_rating = (
        Poi.objects
        .exclude(avg_rating__isnull=True)
        .order_by("-avg_rating")[:10]
    )

    return render(request, "tours/admin_stats.html", {
        "total_poi": total_poi,
        "total_routes": total_routes,
        "total_reviews": total_reviews,
        "shared_routes": shared_routes,
        "routes_7d": routes_7d,
        "reviews_7d": reviews_7d,
        "top_poi_by_usage": top_poi_by_usage,
        "top_poi_by_rating": top_poi_by_rating,
    })