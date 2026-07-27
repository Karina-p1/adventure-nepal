from django.shortcuts import render, get_object_or_404
from .models import Trek, TrekRegion


def trek_list(request):
    treks = Trek.objects.filter(is_active=True).select_related("region")

    region_slug = request.GET.get("region")
    difficulty = request.GET.get("difficulty")

    if region_slug:
        treks = treks.filter(region__slug=region_slug)
    if difficulty:
        treks = treks.filter(difficulty=difficulty)

    context = {
        "treks": treks,
        "regions": TrekRegion.objects.all(),
        "difficulties": Trek.Difficulty.choices,
        "selected_region": region_slug,
        "selected_difficulty": difficulty,
    }
    return render(request, "treks/trek_list.html", context)


def trek_detail(request, slug):
    trek = get_object_or_404(
        Trek.objects.select_related("region", "guide").prefetch_related("itinerary_days", "gallery_images"),
        slug=slug, is_active=True
    )
    context = {"trek": trek}
    return render(request, "treks/trek_detail.html", context)