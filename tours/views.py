from django.contrib.auth.decorators import login_required
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

    context = {
        "route": route,
        "days": days,
    }
    return render(request, "tours/route_detail.html", context)
