from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("profile/", views.profile_view, name="profile"),
    path("my-routes/", views.my_routes, name="my_routes"),
    path("routes/<int:pk>/", views.route_detail, name="route_detail"),
    path("routes/<int:pk>/print/", views.route_print, name="route_print"),
    path("routes/<int:pk>/share-toggle/", views.route_share_toggle, name="route_share_toggle"),
    path("routes/share/<uuid:share_uuid>/", views.route_share_detail, name="route_share_detail"),
    path("dashboard/", views.admin_stats, name="admin_stats"),
    path("history/", views.history_view, name="history"),
    path("routes/<int:pk>/optimize/", views.route_optimize, name="route_optimize"),

    path("places/", views.poi_list, name="poi_list"),
    path("places/<int:pk>/", views.poi_detail, name="poi_detail"),

    path("routes/<int:route_pk>/points/add/",
         views.route_point_add,
         name="route_point_add"),

    path(
        "routes/<int:route_pk>/points/<int:point_pk>/delete/",
        views.route_point_delete,
        name="route_point_delete",
    ),
    path(
        "routes/<int:route_pk>/points/<int:point_pk>/move-up/",
        views.route_point_move_up,
        name="route_point_move_up",
    ),
    path(
        "routes/<int:route_pk>/points/<int:point_pk>/move-down/",
        views.route_point_move_down,
        name="route_point_move_down",
    ),
]
