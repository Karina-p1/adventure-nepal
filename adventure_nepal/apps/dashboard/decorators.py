from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect

from apps.accounts.models import CustomUser


def staff_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())

        allowed_roles = {
            CustomUser.Role.STAFF,
            CustomUser.Role.ADMIN,
        }

        if request.user.role not in allowed_roles:
            messages.error(
                request,
                "You do not have permission to access the management dashboard.",
            )
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper