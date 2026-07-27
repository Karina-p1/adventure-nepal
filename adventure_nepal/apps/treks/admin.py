from django.contrib import admin
from .models import TrekRegion, Trek, TrekItineraryDay, TrekImage


@admin.register(TrekRegion)
class TrekRegionAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


class TrekItineraryDayInline(admin.TabularInline):
    model = TrekItineraryDay
    extra = 1


class TrekImageInline(admin.TabularInline):
    model = TrekImage
    extra = 1


@admin.register(Trek)
class TrekAdmin(admin.ModelAdmin):
    list_display = ("title", "region", "difficulty", "duration_days", "price_usd", "is_featured", "is_active")
    list_filter = ("difficulty", "region", "is_featured", "is_active")
    search_fields = ("title", "short_description")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [TrekItineraryDayInline, TrekImageInline]