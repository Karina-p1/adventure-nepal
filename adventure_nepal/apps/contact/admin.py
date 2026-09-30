from django.contrib import admin

from .models import ContactMessage, CustomTripRequest


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "trek", "is_resolved", "created_at")
    list_filter = ("is_resolved",)
    search_fields = ("name", "email", "subject", "message")
    list_select_related = ("trek",)
    # is_resolved moved off list_editable: the accounts-phase audit flagged this exact
    # pattern on bookings (a stray inline click with no record of the change).
    actions = ["mark_resolved", "mark_unresolved"]

    @admin.action(description="Mark selected messages as resolved")
    def mark_resolved(self, request, queryset):
        updated = queryset.update(is_resolved=True)
        self.message_user(request, f"{updated} message(s) marked resolved.")

    @admin.action(description="Mark selected messages as unresolved")
    def mark_unresolved(self, request, queryset):
        updated = queryset.update(is_resolved=False)
        self.message_user(request, f"{updated} message(s) marked unresolved.")


@admin.register(CustomTripRequest)
class CustomTripRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "preferred_destination", "number_of_travelers",
                     "travel_dates", "status", "created_at")
    list_filter = ("status", "difficulty_preference", "accommodation_preference")
    search_fields = ("name", "email", "phone", "message")
    list_select_related = ("preferred_destination",)
    fieldsets = (
        (None, {"fields": ("name", "email", "phone", "country", "status")}),
        ("Trip preferences", {"fields": (
            "preferred_destination", "travel_dates", "number_of_travelers", "trip_duration_days",
            "budget_usd", "difficulty_preference", "accommodation_preference",
        )}),
        ("Activities", {"fields": (
            "activity_trekking", "activity_mountaineering", "activity_peak_climbing", "activity_rafting",
            "activity_jungle_safari", "activity_cultural_tour", "activity_photography", "activity_helicopter_tour",
        )}),
        ("Message", {"fields": ("message", "created_at")}),
    )
    readonly_fields = ("created_at",)