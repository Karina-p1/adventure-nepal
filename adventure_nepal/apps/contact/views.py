from django.contrib import messages
from django.shortcuts import redirect, render

from apps.treks.models import Trek

from .forms import ContactForm, CustomTripRequestForm


def contact_view(request):
    trek = None

    trek_slug = (
        request.GET.get("trek")
        or request.POST.get("trek_slug")
    )

    if trek_slug:
        trek = Trek.objects.filter(
            slug=trek_slug,
            is_active=True,
        ).first()

    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Thanks for reaching out — we'll get back to you soon!"
            )

            return redirect("contact:contact")

    else:
        initial = {}

        if request.user.is_authenticated:
            initial["name"] = request.user.get_full_name()
            initial["email"] = request.user.email

        if trek:
            initial["subject"] = (
                request.GET.get("subject")
                or f"Question about {trek.title}"
            )

            initial["trek"] = trek.pk

        form = ContactForm(
            initial=initial
        )

    return render(
        request,
        "contact/contact.html",
        {
            "form": form,
            "trek": trek,
        },
    )


def custom_trip_view(request):
    if request.method == "POST":
        form = CustomTripRequestForm(
            request.POST
        )

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Thanks! We're designing your trip and will be in touch soon."
            )

            return redirect(
                "contact:custom_trip"
            )

    else:
        initial = {}

        if request.user.is_authenticated:
            initial["name"] = request.user.get_full_name()
            initial["email"] = request.user.email

        form = CustomTripRequestForm(
            initial=initial
        )

    return render(
        request,
        "contact/custom_trip.html",
        {
            "form": form,
        },
    )