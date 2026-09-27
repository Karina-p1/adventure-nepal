from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from apps.accounts.models import CustomerProfile, CustomUser, GuideProfile, SavedTrip


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_email_verified", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_email_verified")
    fieldsets = UserAdmin.fieldsets + (
        ("Role & contact", {"fields": ("role", "phone", "avatar", "is_email_verified")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role & contact", {"fields": ("email", "role", "phone")}),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "country", "address", "date_of_birth")
    search_fields = ("user__username", "user__email", "country")
    list_select_related = ("user",)


@admin.register(GuideProfile)
class GuideProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "position", "experience_years", "is_public", "order")
    list_filter = ("is_public",)
    list_editable = ("order",)
    search_fields = ("user__username", "specialization")
    list_select_related = ("user",)
    prepopulated_fields = {}  # slug is derived from the user's name, not hand-edited
    fieldsets = (
        (None, {"fields": ("user", "slug", "position", "photo", "is_public", "order")}),
        ("Public profile", {"fields": ("bio", "experience_years", "languages", "specialization")}),
        ("Trust & credentials (verify before publishing)", {"fields": ("certifications",)}),
        ("Social", {"fields": ("facebook_url", "instagram_url", "linkedin_url")}),
    )


@admin.register(SavedTrip)
class SavedTripAdmin(admin.ModelAdmin):
    list_display = ("user", "trek", "created_at")
    list_select_related = ("user", "trek")
    search_fields = ("user__username", "trek__title")