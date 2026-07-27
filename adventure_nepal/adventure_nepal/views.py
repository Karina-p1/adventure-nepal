from django.shortcuts import render
from apps.treks.models import Trek


def home(request):
    featured_treks = Trek.objects.filter(is_active=True, is_featured=True).select_related("region")[:3]
    context = {
        "page_title": "Home",
        "featured_treks": featured_treks,
    }
    return render(request, "pages/home.html", context)


def about(request):
    return render(request, "pages/about.html")