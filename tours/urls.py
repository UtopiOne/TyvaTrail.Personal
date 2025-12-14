from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile_view, name="profile"),
    path("my-routes/", views.my_routes, name="my_routes"),
    path("routes/<int:pk>/", views.route_detail, name="route_detail"),
    path("places/", views.poi_list, name="poi_list"),
    path("places/<int:pk>/", views.poi_detail, name="poi_detail"),
]
