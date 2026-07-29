from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("customer", "trek", "trek_date", "number_of_people", "status", "total_price_usd", "created_at")
    list_filter = ("status", "trek_date")
    search_fields = ("customer__username", "trek__title")
    list_editable = ("status",)