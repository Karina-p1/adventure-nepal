from decimal import Decimal

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from apps.accounts.models import (
    CustomUser,
    CustomerProfile,
    GuideProfile,
)
from apps.bookings.models import Booking
from apps.contact.models import ContactMessage, CustomTripRequest
from apps.reviews.models import Review
from apps.treks.models import Trek, TrekRegion
from .decorators import staff_required
from .forms import (
    BookingPaymentForm,
    DestinationForm,
    TrekForm,
    TrekImageFormSet,
    TrekItineraryFormSet,
    TripFAQFormSet,
    TripHighlightFormSet,
    TripInclusionFormSet,
)
from .forms import (
    BookingPaymentForm,
    DestinationForm,
    GuideAccountForm,
    GuideManagementForm,
    TrekForm,
    TrekImageFormSet,
    TrekItineraryFormSet,
    TripFAQFormSet,
    TripHighlightFormSet,
    TripInclusionFormSet,
)
# ============================================================
# HELPERS
# ============================================================

def _notify_booking_status(booking, message):
    """
    Send a booking status update to the customer.

    Email failure must not prevent the staff action from succeeding.
    """

    recipient = booking.email or booking.customer.email

    if not recipient:
        return

    try:
        send_mail(
            subject=f"Update on your booking {booking.reference}",
            message=(
                f"Hi {booking.full_name or booking.customer.first_name},\n\n"
                f"{message}\n\n"
                f"Booking reference: {booking.reference}\n"
                f"Trek: {booking.trek_title}\n"
                f"Trip date: {booking.trek_date}\n\n"
                "Adventure Nepal"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=True,
        )

    except Exception:
        # Booking management should still work even when
        # email configuration is unavailable.
        pass


# ============================================================
# DASHBOARD HOME
# ============================================================

@staff_required
def dashboard_home(request):
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

    customer_count = CustomUser.objects.filter(
        role=CustomUser.Role.CUSTOMER,
        is_active=True,
    ).count()

    guide_count = CustomUser.objects.filter(
        role=CustomUser.Role.GUIDE,
        is_active=True,
    ).count()

    active_trek_count = Trek.objects.filter(
        is_active=True
    ).count()

    pending_review_count = Review.objects.filter(
        is_approved=False
    ).count()

    unresolved_inquiry_count = ContactMessage.objects.filter(
        is_resolved=False
    ).count()

    new_custom_trip_count = CustomTripRequest.objects.filter(
        status=CustomTripRequest.Status.NEW
    ).count()

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


# ============================================================
# BOOKING LIST
# ============================================================

@staff_required
def booking_list(request):
    bookings = Booking.objects.select_related(
        "customer",
        "trek",
    ).order_by("-created_at")

    # --------------------------------------------------------
    # FILTER VALUES
    # --------------------------------------------------------

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    payment = request.GET.get("payment", "").strip()
    date = request.GET.get("date", "").strip()

    # --------------------------------------------------------
    # SEARCH
    # --------------------------------------------------------

    if search:
        bookings = bookings.filter(
            Q(reference__icontains=search)
            | Q(full_name__icontains=search)
            | Q(email__icontains=search)
            | Q(customer__username__icontains=search)
            | Q(customer__first_name__icontains=search)
            | Q(customer__last_name__icontains=search)
            | Q(trek_title__icontains=search)
        )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    valid_statuses = {
        choice[0]
        for choice in Booking.Status.choices
    }

    if status in valid_statuses:
        bookings = bookings.filter(status=status)

    # --------------------------------------------------------
    # PAYMENT STATUS
    # --------------------------------------------------------

    valid_payments = {
        choice[0]
        for choice in Booking.PaymentStatus.choices
    }

    if payment in valid_payments:
        bookings = bookings.filter(
            payment_status=payment
        )

    # --------------------------------------------------------
    # TREK DATE
    # --------------------------------------------------------

    if date:
        bookings = bookings.filter(
            trek_date=date
        )

    # --------------------------------------------------------
    # PAGINATION
    # --------------------------------------------------------

    paginator = Paginator(bookings, 20)

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "page_obj": page_obj,
        "bookings": page_obj.object_list,

        "search": search,
        "selected_status": status,
        "selected_payment": payment,
        "selected_date": date,

        "status_choices": Booking.Status.choices,
        "payment_choices": Booking.PaymentStatus.choices,

        "total_results": paginator.count,
    }

    return render(
        request,
        "dashboard/bookings/list.html",
        context,
    )


# ============================================================
# BOOKING DETAIL
# ============================================================

@staff_required
def booking_detail(request, pk):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "customer",
            "trek",
            "trek__region",
        ),
        pk=pk,
    )

    payment_form = BookingPaymentForm(
        instance=booking
    )

    context = {
        "booking": booking,
        "payment_form": payment_form,
    }

    return render(
        request,
        "dashboard/bookings/detail.html",
        context,
    )


# ============================================================
# BOOKING STATUS ACTION
# ============================================================

@require_POST
@staff_required
def booking_status_action(request, pk, action):
    booking = get_object_or_404(
        Booking.objects.select_related(
            "customer",
            "trek",
        ),
        pk=pk,
    )

    # --------------------------------------------------------
    # CONFIRM
    # --------------------------------------------------------

    if action == "confirm":

        if booking.status != Booking.Status.PENDING:
            messages.error(
                request,
                "Only pending bookings can be confirmed.",
            )

            return redirect(
                "dashboard:booking_detail",
                pk=booking.pk,
            )

        booking.status = Booking.Status.CONFIRMED

        booking.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        _notify_booking_status(
            booking,
            "Your booking has been confirmed. "
            "We look forward to your trip!",
        )

        messages.success(
            request,
            f"Booking {booking.reference} has been confirmed.",
        )

    # --------------------------------------------------------
    # CANCEL
    # --------------------------------------------------------

    elif action == "cancel":

        if booking.status in (
            Booking.Status.CANCELLED,
            Booking.Status.COMPLETED,
        ):
            messages.error(
                request,
                "This booking can no longer be cancelled.",
            )

            return redirect(
                "dashboard:booking_detail",
                pk=booking.pk,
            )

        booking.status = Booking.Status.CANCELLED

        booking.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        _notify_booking_status(
            booking,
            "Your booking has been cancelled. "
            "Please contact us if you have any questions.",
        )

        messages.success(
            request,
            f"Booking {booking.reference} has been cancelled.",
        )

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    elif action == "complete":

        if booking.status != Booking.Status.CONFIRMED:
            messages.error(
                request,
                "Only confirmed bookings can be marked completed.",
            )

            return redirect(
                "dashboard:booking_detail",
                pk=booking.pk,
            )

        booking.status = Booking.Status.COMPLETED

        booking.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        _notify_booking_status(
            booking,
            "Your trip has been marked as completed. "
            "Thank you for travelling with Adventure Nepal!",
        )

        messages.success(
            request,
            f"Booking {booking.reference} has been marked completed.",
        )

    else:
        messages.error(
            request,
            "Unknown booking action.",
        )

    return redirect(
        "dashboard:booking_detail",
        pk=booking.pk,
    )


# ============================================================
# PAYMENT UPDATE
# ============================================================

@require_POST
@staff_required
def booking_payment_update(request, pk):
    booking = get_object_or_404(
        Booking,
        pk=pk,
    )

    form = BookingPaymentForm(
        request.POST,
        instance=booking,
    )

    if form.is_valid():
        form.save()

        messages.success(
            request,
            f"Payment status for {booking.reference} has been updated.",
        )

    else:
        messages.error(
            request,
            "Payment status could not be updated.",
        )

    return redirect(
        "dashboard:booking_detail",
        pk=booking.pk,
    )

# ============================================================
# TREK MANAGEMENT
# ============================================================

@staff_required
def trek_manage_list(request):
    treks = (
        Trek.objects
        .select_related("region")
        .annotate(
            booking_count=Count(
                "bookings",
                distinct=True,
            )
        )
        .order_by("-created_at")
    )

    search = request.GET.get("q", "").strip()
    category = request.GET.get("category", "").strip()
    region = request.GET.get("region", "").strip()
    status = request.GET.get("status", "").strip()

    if search:
        treks = treks.filter(
            Q(title__icontains=search)
            | Q(short_description__icontains=search)
            | Q(region__name__icontains=search)
        )

    if category:
        treks = treks.filter(
            category=category
        )

    if region:
        treks = treks.filter(
            region_id=region
        )

    if status == "active":
        treks = treks.filter(
            is_active=True
        )

    elif status == "inactive":
        treks = treks.filter(
            is_active=False
        )

    paginator = Paginator(
        treks,
        20,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "treks": page_obj.object_list,
        "page_obj": page_obj,

        "search": search,
        "selected_category": category,
        "selected_region": region,
        "selected_status": status,

        "category_choices": Trek.Category.choices,
        "regions": TrekRegion.objects.all(),

        "total_results": paginator.count,
    }

    return render(
        request,
        "dashboard/treks/list.html",
        context,
    )


def _trek_formsets(
    request=None,
    instance=None,
):
    if request and request.method == "POST":

        return {
            "itinerary": TrekItineraryFormSet(
                request.POST,
                instance=instance,
                prefix="itinerary",
            ),

            "highlights": TripHighlightFormSet(
                request.POST,
                instance=instance,
                prefix="highlights",
            ),

            "inclusions": TripInclusionFormSet(
                request.POST,
                instance=instance,
                prefix="inclusions",
            ),

            "faqs": TripFAQFormSet(
                request.POST,
                instance=instance,
                prefix="faqs",
            ),

            "gallery": TrekImageFormSet(
                request.POST,
                request.FILES,
                instance=instance,
                prefix="gallery",
            ),
        }

    return {
        "itinerary": TrekItineraryFormSet(
            instance=instance,
            prefix="itinerary",
        ),

        "highlights": TripHighlightFormSet(
            instance=instance,
            prefix="highlights",
        ),

        "inclusions": TripInclusionFormSet(
            instance=instance,
            prefix="inclusions",
        ),

        "faqs": TripFAQFormSet(
            instance=instance,
            prefix="faqs",
        ),

        "gallery": TrekImageFormSet(
            instance=instance,
            prefix="gallery",
        ),
    }


@staff_required
def trek_create(request):
    trek = Trek()

    if request.method == "POST":

        form = TrekForm(
            request.POST,
            request.FILES,
            instance=trek,
        )

        formsets = _trek_formsets(
            request=request,
            instance=trek,
        )

        formsets_valid = all(
            formset.is_valid()
            for formset in formsets.values()
        )

        if form.is_valid() and formsets_valid:

            with transaction.atomic():

                trek = form.save()

                for formset in formsets.values():
                    formset.instance = trek
                    formset.save()

            messages.success(
                request,
                f"{trek.title} has been created.",
            )

            return redirect(
                "dashboard:trek_edit",
                pk=trek.pk,
            )

    else:

        form = TrekForm(
            instance=trek,
        )

        formsets = _trek_formsets(
            instance=trek,
        )

    return render(
        request,
        "dashboard/treks/form.html",
        {
            "form": form,
            "formsets": formsets,
            "trek": None,
            "is_create": True,
        },
    )


@staff_required
def trek_edit(request, pk):
    trek = get_object_or_404(
        Trek,
        pk=pk,
    )

    if request.method == "POST":

        form = TrekForm(
            request.POST,
            request.FILES,
            instance=trek,
        )

        formsets = _trek_formsets(
            request=request,
            instance=trek,
        )

        formsets_valid = all(
            formset.is_valid()
            for formset in formsets.values()
        )

        if form.is_valid() and formsets_valid:

            with transaction.atomic():

                form.save()

                for formset in formsets.values():
                    formset.save()

            messages.success(
                request,
                f"{trek.title} has been updated.",
            )

            return redirect(
                "dashboard:trek_edit",
                pk=trek.pk,
            )

    else:

        form = TrekForm(
            instance=trek,
        )

        formsets = _trek_formsets(
            instance=trek,
        )

    return render(
        request,
        "dashboard/treks/form.html",
        {
            "form": form,
            "formsets": formsets,
            "trek": trek,
            "is_create": False,
        },
    )


@require_POST
@staff_required
def trek_toggle_active(request, pk):
    trek = get_object_or_404(
        Trek,
        pk=pk,
    )

    trek.is_active = not trek.is_active

    trek.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if trek.is_active:
        messages.success(
            request,
            f"{trek.title} is now active.",
        )

    else:
        messages.warning(
            request,
            f"{trek.title} has been hidden from customers.",
        )

    return redirect(
        "dashboard:trek_list"
    )
# ============================================================
# DESTINATION MANAGEMENT
# ============================================================

@staff_required
def destination_manage_list(request):
    destinations = (
        TrekRegion.objects
        .annotate(
            trek_count=Count(
                "treks",
                distinct=True,
            ),
            active_trek_count=Count(
                "treks",
                filter=Q(
                    treks__is_active=True
                ),
                distinct=True,
            ),
        )
        .order_by(
            "order",
            "name",
        )
    )

    search = request.GET.get(
        "q",
        "",
    ).strip()

    region_type = request.GET.get(
        "type",
        "",
    ).strip()

    if search:
        destinations = destinations.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(overview__icontains=search)
        )

    if region_type:
        destinations = destinations.filter(
            region_type=region_type
        )

    return render(
        request,
        "dashboard/destinations/list.html",
        {
            "destinations": destinations,
            "search": search,
            "selected_type": region_type,
            "type_choices": TrekRegion.RegionType.choices,
        },
    )


@staff_required
def destination_create(request):

    if request.method == "POST":

        form = DestinationForm(
            request.POST,
            request.FILES,
        )

        if form.is_valid():

            destination = form.save()

            messages.success(
                request,
                f"{destination.name} has been created.",
            )

            return redirect(
                "dashboard:destination_list"
            )

    else:

        form = DestinationForm()

    return render(
        request,
        "dashboard/destinations/form.html",
        {
            "form": form,
            "destination": None,
            "is_create": True,
        },
    )


@staff_required
def destination_edit(request, pk):
    destination = get_object_or_404(
        TrekRegion,
        pk=pk,
    )

    if request.method == "POST":

        form = DestinationForm(
            request.POST,
            request.FILES,
            instance=destination,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                f"{destination.name} has been updated.",
            )

            return redirect(
                "dashboard:destination_edit",
                pk=destination.pk,
            )

    else:

        form = DestinationForm(
            instance=destination,
        )

    return render(
        request,
        "dashboard/destinations/form.html",
        {
            "form": form,
            "destination": destination,
            "is_create": False,
        },
    )

# ============================================================
# CUSTOMER MANAGEMENT
# ============================================================

@staff_required
def customer_list(request):
    customers = (
        CustomUser.objects
        .filter(role=CustomUser.Role.CUSTOMER)
        .select_related("customer_profile")
        .annotate(
            booking_count=Count(
                "bookings",
                distinct=True,
            ),
            review_count=Count(
                "reviews",
                distinct=True,
            ),
            saved_count=Count(
                "saved_trips",
                distinct=True,
            ),
        )
        .order_by("-date_joined")
    )

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    country = request.GET.get("country", "").strip()

    if search:
        customers = customers.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(phone__icontains=search)
        )

    if status == "active":
        customers = customers.filter(
            is_active=True
        )

    elif status == "inactive":
        customers = customers.filter(
            is_active=False
        )

    if country:
        customers = customers.filter(
            customer_profile__country__iexact=country
        )

    countries = (
        CustomerProfile.objects
        .exclude(country="")
        .values_list("country", flat=True)
        .distinct()
        .order_by("country")
    )

    paginator = Paginator(
        customers,
        20,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    context = {
        "customers": page_obj.object_list,
        "page_obj": page_obj,

        "search": search,
        "selected_status": status,
        "selected_country": country,

        "countries": countries,

        "total_results": paginator.count,
    }

    return render(
        request,
        "dashboard/customers/list.html",
        context,
    )


@staff_required
def customer_detail(request, pk):
    customer = get_object_or_404(
        CustomUser.objects.select_related(
            "customer_profile",
        ),
        pk=pk,
        role=CustomUser.Role.CUSTOMER,
    )

    profile = getattr(
        customer,
        "customer_profile",
        None,
    )

    bookings = (
        customer.bookings
        .select_related("trek")
        .order_by("-created_at")
    )

    reviews = (
        Review.objects
        .filter(customer=customer)
        .select_related("trek")
        .order_by("-created_at")
    )

    saved_trips = (
        customer.saved_trips
        .select_related(
            "trek",
            "trek__region",
        )
        .order_by("-created_at")
    )

    booking_totals = bookings.aggregate(
        total=Sum("total_price_usd")
    )

    context = {
        "customer": customer,
        "profile": profile,

        "bookings": bookings[:10],
        "reviews": reviews[:10],
        "saved_trips": saved_trips[:10],

        "booking_count": bookings.count(),
        "review_count": reviews.count(),
        "saved_count": saved_trips.count(),

        "booking_value": (
            booking_totals["total"]
            or Decimal("0.00")
        ),
    }

    return render(
        request,
        "dashboard/customers/detail.html",
        context,
    )


@require_POST
@staff_required
def customer_toggle_active(request, pk):
    customer = get_object_or_404(
        CustomUser,
        pk=pk,
        role=CustomUser.Role.CUSTOMER,
    )

    customer.is_active = not customer.is_active

    customer.save(
        update_fields=[
            "is_active",
        ]
    )

    if customer.is_active:
        messages.success(
            request,
            f"{customer} has been reactivated.",
        )

    else:
        messages.warning(
            request,
            f"{customer} has been deactivated.",
        )

    return redirect(
        "dashboard:customer_detail",
        pk=customer.pk,
    )

# ============================================================
# GUIDE MANAGEMENT
# ============================================================

@staff_required
def guide_manage_list(request):
    guides = (
        CustomUser.objects
        .filter(role=CustomUser.Role.GUIDE)
        .select_related("guide_profile")
        .annotate(
            trek_count=Count(
                "guided_treks",
                distinct=True,
            )
        )
        .order_by(
            "first_name",
            "username",
        )
    )

    search = request.GET.get("q", "").strip()
    status = request.GET.get("status", "").strip()
    visibility = request.GET.get("visibility", "").strip()

    if search:
        guides = guides.filter(
            Q(username__icontains=search)
            | Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
            | Q(guide_profile__position__icontains=search)
            | Q(guide_profile__specialization__icontains=search)
        )

    if status == "active":
        guides = guides.filter(
            is_active=True
        )

    elif status == "inactive":
        guides = guides.filter(
            is_active=False
        )

    if visibility == "public":
        guides = guides.filter(
            guide_profile__is_public=True
        )

    elif visibility == "hidden":
        guides = guides.filter(
            guide_profile__is_public=False
        )

    paginator = Paginator(
        guides,
        20,
    )

    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "dashboard/guides/list.html",
        {
            "guides": page_obj.object_list,
            "page_obj": page_obj,

            "search": search,
            "selected_status": status,
            "selected_visibility": visibility,

            "total_results": paginator.count,
        },
    )


@staff_required
def guide_manage_detail(request, pk):
    guide = get_object_or_404(
        CustomUser,
        pk=pk,
        role=CustomUser.Role.GUIDE,
    )

    profile, _ = GuideProfile.objects.get_or_create(
        user=guide
    )

    assigned_treks = (
        guide.guided_treks
        .select_related("region")
        .order_by("title")
    )

    return render(
        request,
        "dashboard/guides/detail.html",
        {
            "guide": guide,
            "profile": profile,
            "assigned_treks": assigned_treks,
            "trek_count": assigned_treks.count(),
        },
    )


@staff_required
def guide_manage_edit(request, pk):
    guide = get_object_or_404(
        CustomUser,
        pk=pk,
        role=CustomUser.Role.GUIDE,
    )

    profile, _ = GuideProfile.objects.get_or_create(
        user=guide
    )

    if request.method == "POST":

        account_form = GuideAccountForm(
            request.POST,
            request.FILES,
            instance=guide,
        )

        profile_form = GuideManagementForm(
            request.POST,
            request.FILES,
            instance=profile,
        )

        if (
            account_form.is_valid()
            and profile_form.is_valid()
        ):

            with transaction.atomic():
                account_form.save()
                profile_form.save()

            messages.success(
                request,
                f"{guide} has been updated.",
            )

            return redirect(
                "dashboard:guide_detail",
                pk=guide.pk,
            )

    else:

        account_form = GuideAccountForm(
            instance=guide,
        )

        profile_form = GuideManagementForm(
            instance=profile,
        )

    return render(
        request,
        "dashboard/guides/form.html",
        {
            "guide": guide,
            "profile": profile,
            "account_form": account_form,
            "profile_form": profile_form,
        },
    )


@require_POST
@staff_required
def guide_toggle_active(request, pk):
    guide = get_object_or_404(
        CustomUser,
        pk=pk,
        role=CustomUser.Role.GUIDE,
    )

    guide.is_active = not guide.is_active

    guide.save(
        update_fields=[
            "is_active",
        ]
    )

    if guide.is_active:

        messages.success(
            request,
            f"{guide} has been activated.",
        )

    else:

        messages.warning(
            request,
            f"{guide} has been deactivated.",
        )

    return redirect(
        "dashboard:guide_detail",
        pk=guide.pk,
    )


@require_POST
@staff_required
def guide_toggle_public(request, pk):
    guide = get_object_or_404(
        CustomUser,
        pk=pk,
        role=CustomUser.Role.GUIDE,
    )

    profile, _ = GuideProfile.objects.get_or_create(
        user=guide
    )

    profile.is_public = not profile.is_public

    profile.save(
        update_fields=[
            "is_public",
            "updated_at",
        ]
    )

    if profile.is_public:

        messages.success(
            request,
            f"{guide} is now visible on the public guides page.",
        )

    else:

        messages.warning(
            request,
            f"{guide} has been hidden from the public guides page.",
        )

    return redirect(
        "dashboard:guide_detail",
        pk=guide.pk,
    )