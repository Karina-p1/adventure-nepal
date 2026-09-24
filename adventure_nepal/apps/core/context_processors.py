from django.conf import settings
from django.core.cache import cache
from django.db import DatabaseError

from .models import SiteSettings


def site(request):
    """Site-wide template context: settings record, WhatsApp number, nav regions."""
    ctx = {"SITE_URL": settings.SITE_URL, "WHATSAPP_NUMBER": settings.WHATSAPP_NUMBER}
    try:
        from apps.treks.models import TrekRegion

        ctx["site"] = SiteSettings.load()
        regions = cache.get("nav_regions")
        if regions is None:
            regions = list(TrekRegion.objects.values("name", "slug"))
            cache.set("nav_regions", regions, 300)
        ctx["nav_regions"] = regions
    except DatabaseError:  # e.g. before migrations have run
        ctx["site"] = SiteSettings()
        ctx["nav_regions"] = []
    return ctx