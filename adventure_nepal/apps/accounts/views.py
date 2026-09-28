from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme

from apps.bookings.models import Booking  # noqa: F401  (kept for parity with earlier phases)
from apps.reviews.models import Review

from .forms import CustomerProfileForm, GuideSelfEditForm, ProfileForm, SignupForm
from .models import CustomerProfile, GuideProfile, SavedTrip


def _safe_next(request, default="home"):
    target = request.POST.get("next") or request.GET.get("next") or ""
    if url_has_allowed_host_and_scheme(target, {request.get_host()}, request.is_secure()):
        return target
    return resolve_url(default)


class SiteLoginView(auth_views.LoginView):
    """Django's LoginView injects its own `site` (a RequestSite) and `site_name` into the template
    context. That shadows the `site` settings object from our context processor, so base.html's
    {{ site.site_name }} crashed with VariableDoesNotExist. Dropping Django's copies lets the
    context processor's `site` through."""

    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.pop("site", None)
        context.pop("site_name", None)
        return context


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="apps.accounts.backends.EmailOrUsernameBackend")
            messages.success(request, f"Welcome, {user.first_name or user.username}!")
            return redirect(_safe_next(request))
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form, "next": request.GET.get("next", "")})


@login_required
def edit_profile(request):
    user = request.user

    if user.is_guide:
        profile, _ = GuideProfile.objects.get_or_create(user=user)
        ProfileFormClass, RoleFormClass = ProfileForm, GuideSelfEditForm
    else:
        profile, _ = CustomerProfile.objects.get_or_create(user=user)
        ProfileFormClass, RoleFormClass = ProfileForm, CustomerProfileForm

    if request.method == "POST":
        user_form = ProfileFormClass(request.POST, request.FILES, instance=user)
        role_form = RoleFormClass(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and role_form.is_valid():
            user_form.save()
            role_form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:edit_profile")
    else:
        user_form = ProfileFormClass(instance=user)
        role_form = RoleFormClass(instance=profile)

    return render(request, "accounts/edit_profile.html", {"user_form": user_form, "profile_form": role_form})


@login_required
def dashboard(request):
    user = request.user
    bookings = user.bookings.select_related("trek").all()[:5]
    reviews = Review.objects.filter(customer=user).select_related("trek")[:5]
    saved = SavedTrip.objects.filter(user=user).select_related("trek")[:6]
    return render(request, "accounts/dashboard.html", {
        "recent_bookings": bookings, "recent_reviews": reviews, "saved_trips": saved,
        "booking_count": user.bookings.count(),
    })


@login_required
def saved_trips(request):
    saved = SavedTrip.objects.filter(user=request.user).select_related("trek", "trek__region")
    return render(request, "accounts/saved_trips.html", {"saved": saved})


@login_required
def toggle_saved_trip(request, slug):
    if request.method != "POST":
        return redirect("treks:detail", slug=slug)
    from apps.treks.models import Trek
    trek = get_object_or_404(Trek, slug=slug, is_active=True)
    obj, created = SavedTrip.objects.get_or_create(user=request.user, trek=trek)
    if not created:
        obj.delete()
        messages.info(request, "Removed from your saved trips.")
    else:
        messages.success(request, "Saved. You'll find it under Saved trips in your account menu.")
    # _safe_next blocks open redirects (the old code redirected to any 'next' value).
    return redirect(_safe_next(request, default=trek.get_absolute_url()))