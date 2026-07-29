from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.treks.models import Trek
from apps.bookings.models import Booking
from .forms import ReviewForm
from .models import Review


@login_required
def add_review(request, slug):
    trek = get_object_or_404(Trek, slug=slug, is_active=True)

    already_reviewed = Review.objects.filter(customer=request.user, trek=trek).exists()
    eligible_booking = Booking.objects.filter(
        customer=request.user, trek=trek, status=Booking.Status.COMPLETED
    ).first()

    if already_reviewed:
        messages.info(request, "You've already reviewed this trek.")
        return redirect("treks:detail", slug=trek.slug)

    if not eligible_booking:
        messages.error(request, "You can only review treks you've completed.")
        return redirect("treks:detail", slug=trek.slug)

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.customer = request.user
            review.trek = trek
            review.booking = eligible_booking
            review.save()
            messages.success(request, "Thanks for your review!")
            return redirect("treks:detail", slug=trek.slug)
    else:
        form = ReviewForm()

    context = {"trek": trek, "form": form}
    return render(request, "reviews/add_review.html", context)