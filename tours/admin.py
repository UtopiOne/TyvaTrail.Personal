from django.contrib import admin
from .models import (
    Poi,
    PoiPhoto,
    UserProfile,
    Route,
    RoutePoint,
    Review,
)


class PoiPhotoInline(admin.TabularInline):
    model = PoiPhoto
    extra = 1


@admin.register(Poi)
class PoiAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "region", "season", "price_level")
    list_filter = ("type", "region", "season", "price_level")
    search_fields = ("name", "region")
    inlines = [PoiPhotoInline]
    readonly_fields = ("created_at", "updated_at", "avg_rating")


@admin.register(PoiPhoto)
class PoiPhotoAdmin(admin.ModelAdmin):
    list_display = ("poi", "image_url", "created_at")
    search_fields = ("poi__name",)
    readonly_fields = ("created_at",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "travel_style", "budget_level", "physical_level")
    search_fields = ("user__username",)


class RoutePointInline(admin.TabularInline):
    model = RoutePoint
    extra = 0


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "days_count", "total_cost", "created_at")
    search_fields = ("name", "user__username")
    inlines = [RoutePointInline]
    readonly_fields = ("created_at",)


@admin.register(RoutePoint)
class RoutePointAdmin(admin.ModelAdmin):
    list_display = ("route", "poi", "day_number", "order_index")
    list_filter = ("day_number", "route")
    search_fields = ("route__name", "poi__name")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("poi", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("poi__name", "user__username")
    readonly_fields = ("created_at",)
