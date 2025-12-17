from django.contrib import admin
import uuid

from .models import RouteGeneration
from .models import Poi, PoiPhoto, UserProfile, Route, RoutePoint, Review


class PoiPhotoInline(admin.TabularInline):
    model = PoiPhoto
    extra = 1


@admin.register(Poi)
class PoiAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "region", "season", "price_level", "base_cost", "avg_rating", "has_coords")
    list_filter = ("type", "region", "season", "price_level", "physical_level")
    search_fields = ("name", "region", "short_description")
    ordering = ("-avg_rating", "name")
    inlines = [PoiPhotoInline]
    readonly_fields = ("created_at", "updated_at", "avg_rating")
    list_select_related = False

    @admin.display(boolean=True, description="Координаты")
    def has_coords(self, obj: Poi):
        return obj.latitude is not None and obj.longitude is not None


@admin.register(PoiPhoto)
class PoiPhotoAdmin(admin.ModelAdmin):
    list_display = ("poi", "image_url", "created_at")
    search_fields = ("poi__name",)
    readonly_fields = ("created_at",)
    autocomplete_fields = ("poi",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "travel_style", "budget_level", "physical_level")
    search_fields = ("user__username",)
    autocomplete_fields = ("user",)


class RoutePointInline(admin.TabularInline):
    model = RoutePoint
    extra = 0
    autocomplete_fields = ("poi",)
    ordering = ("day_number", "order_index")
    fields = ("day_number", "order_index", "poi", "visit_time_estimate", "note")


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "days_count", "total_duration_hours", "total_cost", "is_shared", "created_at", "short_share_uuid")
    list_filter = ("is_shared", "days_count", "created_at")
    search_fields = ("name", "user__username")
    inlines = [RoutePointInline]
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)
    actions = ("enable_sharing", "disable_sharing", "regenerate_share_uuid")

    @admin.display(description="UUID (short)")
    def short_share_uuid(self, obj: Route):
        return str(obj.share_uuid)[:8]

    @admin.action(description="Включить доступ по ссылке")
    def enable_sharing(self, request, queryset):
        queryset.update(is_shared=True)

    @admin.action(description="Отключить доступ по ссылке")
    def disable_sharing(self, request, queryset):
        queryset.update(is_shared=False)

    @admin.action(description="Перегенерировать UUID ссылки")
    def regenerate_share_uuid(self, request, queryset):
        for r in queryset:
            r.share_uuid = uuid.uuid4()
            r.save(update_fields=["share_uuid"])


@admin.register(RoutePoint)
class RoutePointAdmin(admin.ModelAdmin):
    list_display = ("route", "poi", "day_number", "order_index")
    list_filter = ("day_number", "route")
    search_fields = ("route__name", "poi__name")
    autocomplete_fields = ("route", "poi")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("poi", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("poi__name", "user__username")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("poi", "user")

@admin.register(RouteGeneration)
class RouteGenerationAdmin(admin.ModelAdmin):
    list_display = ("user", "route", "days_count", "max_budget", "created_at")
    search_fields = ("user__username", "route__name")
    readonly_fields = ("created_at",)
