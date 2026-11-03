from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def user_has_role(user, role):
    if not user.is_authenticated:
        return False
    if role == "admin" and user.is_superuser:
        return True
    return user.role_assignments.filter(role=role).exists()


def role_required(role):
    """Protect a view using a server-side role check."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path())
            if not user_has_role(request.user, role):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
