from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from apps.treks.models import Trek

from .forms import ContactForm, CustomTripRequestForm


def _notify_admin(subject, template, context):
    if not settings.ADMIN_NOTIFY_EMAIL:
        return
    try:
        body = render_to_string(template, context)
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [settings.ADMIN_NOTIFY_EMAIL], fail_silently=True)
    except Exception:
        pass


def contact_view(request):
    trek = None
    trek_slug = request.GET.get("trek") or request.POST.get("trek_slug")
    if trek_slug:
        trek = Trek.objects.filter(slug=trek_slug, is_active=True).first()

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            _notify_admin(
                f"New contact inquiry — {contact_message.subject}",
                "contact/email/new_inquiry.txt", {"contact_message": contact_message},
            )
            messages.success(request, "Thanks for reaching out — we'll get back to you soon!")
            return redirect("contact:contact")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial["name"] = request.user.get_full_name()
            initial["email"] = request.user.email
        if trek:
            initial["subject"] = request.GET.get("subject") or f"Question about {trek.title}"
            initial["trek"] = trek.pk
        form = ContactForm(initial=initial)

    return render(request, "contact/contact.html", {"form": form, "trek": trek})


def custom_trip_view(request):
    if request.method == "POST":
        form = CustomTripRequestForm(request.POST)
        if form.is_valid():
            trip_request = form.save()
            _notify_admin(
                f"New custom trip request — {trip_request.name}",
                "contact/email/new_custom_trip.txt", {"trip_request": trip_request},
            )
            messages.success(request, "Thanks! We're designing your trip and will be in touch soon.")
            return redirect("contact:custom_trip")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial["name"] = request.user.get_full_name()
            initial["email"] = request.user.email
        form = CustomTripRequestForm(initial=initial)

    return render(request, "contact/custom_trip.html", {"form": form})