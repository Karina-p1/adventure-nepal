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


from .models import HighlightItem, NewsletterSubscriber, SiteStatistic, Testimonial  # noqa: E402


@admin.register(SiteStatistic)
class SiteStatisticAdmin(admin.ModelAdmin):
    list_display = ("label", "value", "order", "is_active")
    list_editable = ("value", "order", "is_active")


@admin.register(HighlightItem)
class HighlightItemAdmin(admin.ModelAdmin):
    list_display = ("title", "section", "icon", "order", "is_active")
    list_filter = ("section", "is_active")
    list_editable = ("order", "is_active")


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "country", "rating", "trek", "order", "is_active")
    list_filter = ("is_active", "rating")
    search_fields = ("name", "quote")
    list_select_related = ("trek",)


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active",)
    search_fields = ("email",)
    readonly_fields = ("subscribed_at",)