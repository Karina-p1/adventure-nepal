from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def staff_required(view_func):
    """
    Allow only authenticated staff/admin users into the management dashboard.

    Django superusers are also allowed so /staff/ remains usable even if
    their custom role has not been explicitly changed to Admin.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(
                request,
                "You do not have permission to access the staff dashboard.",
            )
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper