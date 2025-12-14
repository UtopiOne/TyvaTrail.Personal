from django.contrib import admin
from django.urls import include, path

from tours import views as tours_views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/signup/", tours_views.signup, name="signup"),
    path("accounts/", include("django.contrib.auth.urls")),

    path("", include("tours.urls")),
]
