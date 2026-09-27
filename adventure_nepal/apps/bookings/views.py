from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from apps.treks.models import Trek

from .forms import BookingForm
from .models import Booking


def _notify_booking_received(booking):
    """Best-effort email; a failed send should never block the booking itself."""
    try:
        context = {"booking": booking, "site": getattr(settings, "SITE_URL", "")}
        customer_body = render_to_string("bookings/email/booking_received.txt", context)
        send_mail(
            f"We received your booking request — {booking.reference}",
            customer_body, settings.DEFAULT_FROM_EMAIL, [booking.email or booking.customer.email],
            fail_silently=True,
        )
        if settings.ADMIN_NOTIFY_EMAIL:
            send_mail(
                f"New booking request — {booking.reference}",
                customer_body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_NOTIFY_EMAIL],
                fail_silently=True,
            )
    except Exception:
        pass


@login_required
def create_booking(request, slug):
    trek = get_object_or_404(Trek, slug=slug, is_active=True)
    profile = getattr(request.user, "customer_profile", None)

    if request.method == "POST":
        form = BookingForm(request.POST, trek=trek)
        if form.is_valid():
            if Booking.recent_duplicate_exists(request.user, trek, form.cleaned_data["trek_date"]):
                messages.info(request, "Looks like you just submitted this — check My Bookings.")
                return redirect("bookings:my_bookings")
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.trek = trek
            booking.save()
            _notify_booking_received(booking)
            messages.success(request, "Your booking request has been submitted!")
            return redirect("bookings:confirmation", pk=booking.pk)
    else:
        initial = {
            "full_name": request.user.get_full_name(),
            "email": request.user.email,
            "phone": request.user.phone,
            "country": getattr(profile, "country", ""),
        }
        form = BookingForm(initial=initial, trek=trek)

    return render(request, "bookings/create_booking.html", {"trek": trek, "form": form})


@login_required
def booking_confirmation(request, pk):
    booking = get_object_or_404(request.user.bookings.select_related("trek"), pk=pk)
    return render(request, "bookings/confirmation.html", {"booking": booking})


@login_required
def my_bookings(request):
    from apps.reviews.models import Review
    bookings = request.user.bookings.select_related("trek").all()
    reviewed_trek_ids = set(Review.objects.filter(customer=request.user).values_list("trek_id", flat=True))
    return render(request, "bookings/my_bookings.html", {"bookings": bookings, "reviewed_trek_ids": reviewed_trek_ids})


@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(request.user.bookings, pk=pk)
    if request.method != "POST":
        return redirect("bookings:my_bookings")
    if not booking.is_cancelable:
        messages.error(request, "This booking can no longer be cancelled online — contact us for help.")
    else:
        booking.status = Booking.Status.CANCELLED
        booking.save(update_fields=["status", "updated_at"])
        messages.success(request, f"Booking {booking.reference} has been cancelled.")
    return redirect("bookings:my_bookings")