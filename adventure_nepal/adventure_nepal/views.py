from django.db.models import Count, F, Q
from django.shortcuts import render

from apps.core.models import HighlightItem, SiteStatistic, Testimonial
from apps.accounts.models import CustomUser
from apps.reviews.models import Review
from apps.treks.forms import DURATION_CHOICES
from apps.treks.models import Trek, TrekRegion

ACTIVITY_ICONS = {
    "trekking": "bi-tsunami", "tour": "bi-bus-front", "sightseeing": "bi-binoculars",
    "climbing": "bi-triangle", "cultural": "bi-bank", "safari": "bi-tree",
    "rafting": "bi-water", "adventure": "bi-lightning-charge",
}


def _reviewer_name(user):
    last = f" {user.last_name[0]}." if user.last_name else ""
    return f"{user.first_name or user.username}{last}"


def home(request):
    treks = Trek.objects.active().select_related("region").with_rating()

    featured = list(treks.filter(is_featured=True)[:6])
    featured_ids = [t.pk for t in featured]
    popular_qs = treks.exclude(pk__in=featured_ids)
    popular = list(popular_qs.filter(is_popular=True)[:6]) or list(
        popular_qs.order_by(F("avg_rating").desc(nulls_last=True), "-created_at")[:6]
    )

    destinations = TrekRegion.objects.annotate(
        trek_count=Count("treks", filter=Q(treks__is_active=True))
    ).filter(trek_count__gt=0)[:6]

    # Trust numbers: manual entries win; otherwise show counts computed from the database.
    stats = [{"value": s.value, "label": s.label} for s in SiteStatistic.objects.filter(is_active=True)]
    if not stats:
        stats = [
            {"value": Trek.objects.active().count(), "label": "Trips"},
            {"value": TrekRegion.objects.count(), "label": "Destinations"},
            {"value": CustomUser.objects.filter(role="guide", is_active=True).count(), "label": "Guides"},
        ]

    testimonials = [
        {"quote": r.comment, "name": _reviewer_name(r.customer), "meta": r.trek.title, "rating": r.rating}
        for r in Review.objects.filter(is_approved=True, rating__gte=4).select_related("customer", "trek")[:6]
    ] + [
        {"quote": t.quote, "name": t.name, "meta": t.country, "rating": t.rating}
        for t in Testimonial.objects.filter(is_active=True)[:6]
    ]

    counts = dict(Trek.objects.active().values_list("category").annotate(n=Count("id")))
    activities = [
        {"value": v, "label": label, "icon": ACTIVITY_ICONS.get(v, "bi-compass"), "count": counts[v]}
        for v, label in Trek.Category.choices if counts.get(v)
    ]

    highlights = HighlightItem.objects.filter(is_active=True)
    context = {
        "page_title": "Adventure Nepal — Trek the Himalayas",
        "featured_treks": featured,
        "popular_treks": popular,
        "destinations": destinations,
        "stats": stats,
        "testimonials": testimonials,
        "activities": activities,
        "why_items": [h for h in highlights if h.section == "why"],
        "responsible_items": [h for h in highlights if h.section == "responsible"],
        "blog_posts": [],  # filled in Phase 6
        # search form choices
        "regions": TrekRegion.objects.all(),
        "categories": Trek.Category.choices,
        "difficulties": Trek.Difficulty.choices,
        "durations": DURATION_CHOICES,
    }
    return render(request, "pages/home.html", context)


def about(request):
    return render(request, "pages/about.html")