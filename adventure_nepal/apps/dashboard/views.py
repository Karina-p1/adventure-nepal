from decimal import Decimal

from django.db.models import Sum
from django.shortcuts import render

from apps.accounts.models import CustomUser
from apps.bookings.models import Booking
from apps.contact.models import ContactMessage, CustomTripRequest
from apps.reviews.models import Review
from apps.treks.models import Trek

from .decorators import staff_required


@staff_required
def dashboard_home(request):
    # ---------------------------------------------------------
    # BOOKINGS
    # ---------------------------------------------------------
    bookings = Booking.objects.select_related(
        "customer",
        "trek",
    )

    total_bookings = bookings.count()

    pending_bookings = bookings.filter(
        status=Booking.Status.PENDING
    ).count()

    confirmed_bookings = bookings.filter(
        status=Booking.Status.CONFIRMED
    ).count()

    completed_bookings = bookings.filter(
        status=Booking.Status.COMPLETED
    ).count()

    booking_value = (
        bookings
        .exclude(status=Booking.Status.CANCELLED)
        .aggregate(total=Sum("total_price_usd"))
        ["total"]
        or Decimal("0.00")
    )

    # ---------------------------------------------------------
    # USERS
    # ---------------------------------------------------------
    customer_count = CustomUser.objects.filter(
        role=CustomUser.Role.CUSTOMER,
        is_active=True,
    ).count()

    guide_count = CustomUser.objects.filter(
        role=CustomUser.Role.GUIDE,
        is_active=True,
    ).count()

    # ---------------------------------------------------------
    # TREKS
    # ---------------------------------------------------------
    active_trek_count = Trek.objects.filter(
        is_active=True
    ).count()

    # ---------------------------------------------------------
    # REVIEWS
    # ---------------------------------------------------------
    pending_review_count = Review.objects.filter(
        is_approved=False
    ).count()

    # ---------------------------------------------------------
    # CONTACT / CUSTOM TRIPS
    # ---------------------------------------------------------
    unresolved_inquiry_count = ContactMessage.objects.filter(
        is_resolved=False
    ).count()

    new_custom_trip_count = CustomTripRequest.objects.filter(
        status=CustomTripRequest.Status.NEW
    ).count()

    # ---------------------------------------------------------
    # RECENT ACTIVITY
    # ---------------------------------------------------------
    recent_bookings = bookings.order_by(
        "-created_at"
    )[:5]

    recent_inquiries = (
        ContactMessage.objects
        .select_related("trek")
        .order_by("-created_at")[:5]
    )

    recent_custom_trips = (
        CustomTripRequest.objects
        .select_related("preferred_destination")
        .order_by("-created_at")[:5]
    )

    context = {
        "total_bookings": total_bookings,
        "pending_bookings": pending_bookings,
        "confirmed_bookings": confirmed_bookings,
        "completed_bookings": completed_bookings,
        "booking_value": booking_value,

        "customer_count": customer_count,
        "guide_count": guide_count,
        "active_trek_count": active_trek_count,

        "pending_review_count": pending_review_count,
        "unresolved_inquiry_count": unresolved_inquiry_count,
        "new_custom_trip_count": new_custom_trip_count,

        "recent_bookings": recent_bookings,
        "recent_inquiries": recent_inquiries,
        "recent_custom_trips": recent_custom_trips,
    }

    return render(
        request,
        "dashboard/dashboard.html",
        context,
    )