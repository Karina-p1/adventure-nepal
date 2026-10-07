from django.contrib import admin


from .models import Booking



@admin.action(description="Mark selected bookings as Confirmed (emails the customer)")
def mark_confirmed(modeladmin, request, queryset):
    updated = 0
    for booking in queryset.exclude(status=Booking.Status.CONFIRMED):
        booking.status = Booking.Status.CONFIRMED
        booking.save(update_fields=["status", "updated_at"])
       
        updated += 1
   


@admin.action(description="Mark selected bookings as Cancelled (emails the customer)")
def mark_cancelled(modeladmin, request, queryset):
    updated = 0
    for booking in queryset.exclude(status=Booking.Status.CANCELLED):
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        
        updated += 1
   


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