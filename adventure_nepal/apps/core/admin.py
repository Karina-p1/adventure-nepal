from django.contrib import admin
from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Brand", {"fields": ("site_name", "tagline")}),
        ("Contact", {"fields": ("phone", "email", "address", "opening_hours")}),
        ("Social", {"fields": ("facebook_url", "instagram_url", "youtube_url", "tiktok_url")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False