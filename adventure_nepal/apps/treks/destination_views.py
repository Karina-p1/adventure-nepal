from django.shortcuts import get_object_or_404, render

from .models import Trek, TrekRegion


def destination_list(request):
    destinations = TrekRegion.objects.all()
    return render(request, "destinations/destination_list.html", {"destinations": destinations})


def destination_detail(request, slug):
    destination = get_object_or_404(TrekRegion, slug=slug)
    treks = (
        Trek.objects.active().filter(region=destination)
        .select_related("region").with_rating()
        .order_by("-is_featured", "title")
    )
    return render(request, "destinations/destination_detail.html", {
        "destination": destination,
        "treks": treks,
    })