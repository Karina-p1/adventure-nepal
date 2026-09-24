from django.core.cache import cache
from django.db import models


class SiteSettings(models.Model):
    """Single editable record: contact details and social links shown site-wide."""

    site_name = models.CharField(max_length=100, default="Adventure Nepal")
    tagline = models.CharField(max_length=200, blank=True, default="Trekking and travel across the Himalayas, guided by locals who know the trails.")
    phone = models.CharField(max_length=30, blank=True, default="+977 9800000000")
    email = models.EmailField(blank=True, default="info@adventurenepal.com")
    address = models.CharField(max_length=255, blank=True, default="Thamel, Kathmandu, Nepal")
    opening_hours = models.CharField(max_length=200, blank=True, default="Sun–Fri, 9:00–18:00 (NPT)")
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Site settings"
        verbose_name_plural = "Site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        cache.delete("site_settings")

    @classmethod
    def load(cls):
        obj = cache.get("site_settings")
        if obj is None:
            obj, _ = cls.objects.get_or_create(pk=1)
            cache.set("site_settings", obj, 300)
        return obj