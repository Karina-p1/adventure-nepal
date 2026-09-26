from django.core.paginator import Paginator
from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404, render

from apps.accounts.models import CustomUser
from apps.bookings.models import Booking
from apps.reviews.models import Review

from .forms import DURATION_RANGES, TrekFilterForm
from .models import Trek, TrekImage, TrekItineraryDay, TripFAQ, TripHighlight, TripInclusion

PER_PAGE = 12


def _sort(qs, key):
    return {
        "price_asc": qs.order_by("price_usd"),
        "price_desc": qs.order_by("-price_usd"),
        "duration_asc": qs.order_by("duration_days"),
        "newest": qs.order_by("-created_at"),
        "rating": qs.order_by(("-avg_rating")),
    }.get(key, qs)  # "recommended" / unknown -> model default ordering


def trek_list(request):
    form = TrekFilterForm(request.GET or None)
    form.is_valid()
    data = form.cleaned_data if form.is_valid() else {}

    treks = Trek.objects.active().select_related("region").with_rating()

    if data.get("q"):
        treks = treks.filter(Q(title__icontains=data["q"]) | Q(region__name__icontains=data["q"]))
    if data.get("region"):
        treks = treks.filter(region__slug=data["region"])
    if data.get("category"):
        treks = treks.filter(category=data["category"])
    if data.get("difficulty"):
        treks = treks.filter(difficulty=data["difficulty"])
    if data.get("duration") in DURATION_RANGES:
        low, high = DURATION_RANGES[data["duration"]]
        treks = treks.filter(duration_days__gte=low)
        if high:
            treks = treks.filter(duration_days__lte=high)
    if data.get("price_min") is not None:
        treks = treks.filter(price_usd__gte=data["price_min"])
    if data.get("price_max") is not None:
        treks = treks.filter(price_usd__lte=data["price_max"])

    treks = _sort(treks, data.get("sort"))

    paginator = Paginator(treks, PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))

    active_filters = sum(1 for k in ("q", "region", "category", "difficulty", "duration", "price_min", "price_max") if data.get(k))

    context = {
        "form": form,
        "page_obj": page_obj,
        "treks": page_obj.object_list,
        "active_filters": active_filters,
        "querystring": request.GET.urlencode(),
    }
    return render(request, "treks/trek_list.html", context)


def trek_detail(request, slug):
    trek = get_object_or_404(
        Trek.objects.select_related("region")
        .prefetch_related(
            "guides__guide_profile",
            Prefetch("itinerary_days", queryset=TrekItineraryDay.objects.all()),
            Prefetch("gallery_images", queryset=TrekImage.objects.all()),
            Prefetch("highlights", queryset=TripHighlight.objects.all()),
            Prefetch("inclusions", queryset=TripInclusion.objects.all()),
            Prefetch("faqs", queryset=TripFAQ.objects.all()),
            Prefetch(
                "reviews",
                queryset=Review.objects.filter(is_approved=True).select_related("customer", "customer__customer_profile"),
                to_attr="approved_reviews",
            ),
        )
        .with_rating(),
        slug=slug, is_active=True,
    )

    can_review = False
    if request.user.is_authenticated:
        already = Review.objects.filter(customer=request.user, trek=trek).exists()
        eligible = Booking.objects.filter(customer=request.user, trek=trek, status=Booking.Status.COMPLETED).exists()
        can_review = eligible and not already

    related = (
        Trek.objects.active().exclude(pk=trek.pk).filter(Q(region=trek.region) | Q(category=trek.category))
        .select_related("region").with_rating()[:3]
    )

    return render(request, "treks/trek_detail.html", {
        "trek": trek,
        "can_review": can_review,
        "included": [i for i in trek.inclusions.all() if i.is_included],
        "excluded": [i for i in trek.inclusions.all() if not i.is_included],
        "related_treks": related,
    })