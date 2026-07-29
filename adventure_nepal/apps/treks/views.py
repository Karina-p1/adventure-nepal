from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Trek, TrekRegion


def trek_list(request):
    treks = Trek.objects.filter(is_active=True).select_related("region")

    query = request.GET.get("q", "").strip()
    region_slug = request.GET.get("region")
    difficulty = request.GET.get("difficulty")
    category = request.GET.get("category")

    if query:
        treks = treks.filter(
            Q(title__icontains=query) | Q(region__name__icontains=query)
        )
    if region_slug:
        treks = treks.filter(region__slug=region_slug)
    if difficulty:
        treks = treks.filter(difficulty=difficulty)
    if category:
        treks = treks.filter(category=category)

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
        Trek.objects.select_related("region", "guide").prefetch_related("itinerary_days", "gallery_images", "reviews"),
        slug=slug, is_active=True
    )
    return render(request, "treks/trek_detail.html", {"trek": trek})