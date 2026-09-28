from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailOrUsernameBackend(ModelBackend):
    """Lets people log in with either their username or their email (case-insensitive email).

    The login form is labelled "Username or email", so the backend has to honour that.
    Inherits permission handling from ModelBackend, so admin/permissions keep working.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        if not username or password is None:
            return None

        users = User._default_manager
        user = users.filter(username=username).first() or users.filter(email__iexact=username.strip()).first()

        if user is None:
            User().set_password(password)  # keep timing similar for unknown accounts
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None