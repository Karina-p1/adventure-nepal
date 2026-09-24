from django.contrib import messages
from django.shortcuts import redirect, resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import NewsletterForm
from .models import NewsletterSubscriber


@require_POST
def newsletter_subscribe(request):
    target = request.POST.get("next", "")
    if not url_has_allowed_host_and_scheme(target, {request.get_host()}, request.is_secure()):
        target = resolve_url("home")
    form = NewsletterForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Enter a valid email address to subscribe.")
    elif form.cleaned_data["website"]:
        messages.success(request, "You're subscribed.")  # bot: pretend success, store nothing
    else:
        sub, created = NewsletterSubscriber.objects.get_or_create(email=form.cleaned_data["email"])
        if not created and not sub.is_active:
            sub.is_active = True
            sub.save(update_fields=["is_active"])
        messages.success(request, "You're subscribed. We'll only email you about new trips and travel tips.")
    return redirect(f"{target.split('#')[0]}#newsletter")