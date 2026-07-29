from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.treks.models import Trek
from .forms import BookingForm


@login_required
def create_booking(request, slug):
    trek = get_object_or_404(Trek, slug=slug, is_active=True)

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.trek = trek
            booking.save()
            messages.success(request, "Your booking request has been submitted!")
            return redirect("bookings:confirmation", pk=booking.pk)
    else:
        form = BookingForm()

    context = {"trek": trek, "form": form}
    return render(request, "bookings/create_booking.html", context)


@login_required
def booking_confirmation(request, pk):
    booking = get_object_or_404(request.user.bookings, pk=pk)
    return render(request, "bookings/confirmation.html", {"booking": booking})


@login_required
def my_bookings(request):
    bookings = request.user.bookings.select_related("trek").all()
    return render(request, "bookings/my_bookings.html", {"bookings": bookings})