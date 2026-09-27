from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

from .models import Booking


def _notify_status_change(booking, message):
    try:
        send_mail(
            f"Update on your booking {booking.reference}",
            f"Hi {booking.full_name or booking.customer.first_name},\n\n{message}\n\n"
            f"Reference: {booking.reference}\nTrek: {booking.trek_title}\n",
            settings.DEFAULT_FROM_EMAIL, [booking.email or booking.customer.email], fail_silently=True,
        )
    except Exception:
        pass


@admin.action(description="Mark selected bookings as Confirmed (emails the customer)")
def mark_confirmed(modeladmin, request, queryset):
    updated = 0
    for booking in queryset.exclude(status=Booking.Status.CONFIRMED):
        booking.status = Booking.Status.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])
        _notify_status_change(booking, "Your booking has been confirmed. We look forward to your trip!")
        updated += 1
    modeladmin.message_user(request, f"{updated} booking(s) confirmed and emailed.")


@admin.action(description="Mark selected bookings as Cancelled (emails the customer)")
def mark_cancelled(modeladmin, request, queryset):
    updated = 0
    for booking in queryset.exclude(status=Booking.Status.CANCELLED):
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        _notify_status_change(booking, "Your booking has been cancelled. Contact us with any questions.")
        updated += 1
    modeladmin.message_user(request, f"{updated} booking(s) cancelled and emailed.")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("reference", "customer", "trek_title", "trek_date", "number_of_people",
                     "status", "payment_status", "total_price_usd", "created_at")
    list_filter = ("status", "payment_status", "trek_date")
    search_fields = ("reference", "customer__username", "customer__email", "trek_title", "full_name")
    list_select_related = ("customer", "trek")
    actions = [mark_confirmed, mark_cancelled]
    readonly_fields = ("reference", "trek_title", "price_per_person_usd", "total_price_usd", "created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("reference", "customer", "trek", "trek_title", "status", "payment_status")}),
        ("Trip", {"fields": ("trek_date", "number_of_people", "special_requests")}),
        ("Contact", {"fields": ("full_name", "email", "phone", "country")}),
        ("Pricing", {"fields": ("price_per_person_usd", "total_price_usd")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )