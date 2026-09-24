from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from .models import Trek, TrekRegion

DURATION_RANGES = {"1-3": (1, 3), "4-7": (4, 7), "8-14": (8, 14), "15+": (15, None)}
DURATION_CHOICES = [("1-3", "1–3 days"), ("4-7", "4–7 days"), ("8-14", "8–14 days"), ("15+", "15+ days")]


def trek_list(request):
    treks = Trek.objects.active().select_related("region").with_rating()

    query = request.GET.get("q", "").strip()
    region_slug = request.GET.get("region")
    difficulty = request.GET.get("difficulty")
    category = request.GET.get("category")
    duration = request.GET.get("duration")

    if query:
        treks = treks.filter(Q(title__icontains=query) | Q(region__name__icontains=query))
    if region_slug:
        treks = treks.filter(region__slug=region_slug)
    if difficulty:
        treks = treks.filter(difficulty=difficulty)
    if category:
        treks = treks.filter(category=category)
    if duration in DURATION_RANGES:
        low, high = DURATION_RANGES[duration]
        treks = treks.filter(duration_days__gte=low)
        if high:
            treks = treks.filter(duration_days__lte=high)

    context = {
        "treks": treks,
        "regions": TrekRegion.objects.all(),
        "difficulties": Trek.Difficulty.choices,
        "categories": Trek.Category.choices,
        "selected_region": region_slug,
        "selected_difficulty": difficulty,
        "selected_category": category,
        "query": query,
    }
    return render(request, "treks/trek_list.html", context)


def trek_detail(request, slug):
    trek = get_object_or_404(
        Trek.objects.select_related("region", "guide")
        .prefetch_related("itinerary_days", "gallery_images", "reviews")
        .with_rating(),
        slug=slug, is_active=True,
    )
    return render(request, "treks/trek_detail.html", {"trek": trek})