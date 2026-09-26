from django.contrib import admin

from .models import Trek, TrekImage, TrekItineraryDay, TrekRegion, TripFAQ, TripHighlight, TripInclusion


@admin.register(TrekRegion)
class TrekRegionAdmin(admin.ModelAdmin):
    list_display = ("name", "region_type", "order", "slug")
    list_editable = ("order",)
    list_filter = ("region_type",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "region_type", "order")}),
        ("Content", {"fields": ("hero_image", "description", "overview", "best_time_to_visit", "meta_description")}),
        ("Map", {"fields": ("latitude", "longitude")}),
    )


class TrekItineraryDayInline(admin.TabularInline):
    model = TrekItineraryDay
    extra = 1


class TrekImageInline(admin.TabularInline):
    model = TrekImage
    extra = 1


class TripHighlightInline(admin.TabularInline):
    model = TripHighlight
    extra = 1


class TripInclusionInline(admin.TabularInline):
    model = TripInclusion
    extra = 1


class TripFAQInline(admin.TabularInline):
    model = TripFAQ
    extra = 1


@admin.register(Trek)
class TrekAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "region", "difficulty", "duration_days", "price_usd", "is_featured", "is_popular", "is_active")
    list_filter = ("category", "difficulty", "region", "is_featured", "is_popular", "is_active")
    list_select_related = ("region",)
    search_fields = ("title", "short_description", "region__name")
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("guides",)
    inlines = [TripHighlightInline, TrekItineraryDayInline, TripInclusionInline, TripFAQInline, TrekImageInline]
    fieldsets = (
        (None, {"fields": ("title", "slug", "category", "region", "guides", "is_active")}),
        ("Content", {"fields": ("short_description", "description", "meta_description", "cover_image")}),
        ("Trip facts", {"fields": (
            "duration_days", "max_altitude_m", "difficulty", "group_size_min", "group_size_max",
            "best_season", ("season_spring", "season_summer", "season_autumn", "season_winter"),
            "accommodation_summary", "altitude_sickness_risk",
        )}),
        ("Pricing", {"fields": ("price_usd", "discount_price_usd")}),
        ("Homepage", {"fields": ("is_featured", "is_popular")}),
    )