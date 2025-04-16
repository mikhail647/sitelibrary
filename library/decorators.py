# library/decorators.py
from django.http import HttpResponseForbidden
from functools import wraps
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Требуется авторизация")

            if not hasattr(request.user, 'role') or request.user.role not in allowed_roles:
                return HttpResponseForbidden("Доступ запрещен")

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator

def group_required(group_names, login_url='login', raise_exception=False):
    """
    Requires user membership in at least one of the roles passed in.
    (Note: Renamed from group_required to role_required conceptually)
    """
    def check_perms(user):
        if isinstance(group_names, str):
            roles = [group_names] # Treat group_names as roles
        else:
            roles = group_names

        if user.is_authenticated and hasattr(user, 'role') and user.role in roles:
            return True

        if raise_exception:
            # Optional: Raise an exception or return a specific response
            pass # Replace with specific action if needed
        elif user.is_authenticated:
            # User is logged in but doesn't have the right role
            messages.error(user.request, "You do not have permission to access this page.")
            # Redirect to a default page or show an error
            # For now, redirecting to login, but a dedicated 'unauthorized' page might be better
            # Or redirect based on role?
            # return redirect('user_dashboard') # Example redirect

        # Default: Redirect to login
        return False

    return user_passes_test(check_perms, login_url=login_url)

def staff_required(function=None, login_url='login'):
    actual_decorator = group_required(['staff', 'admin'], login_url=login_url)
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_required(function=None, login_url='login'):
    actual_decorator = group_required('admin', login_url=login_url)
    if function:
        return actual_decorator(function)
    return actual_decorator

# Example usage in views.py:
# from .decorators import staff_required, admin_required
#
# @login_required
# def user_view(request):
#     ...
#
# @staff_required
# def staff_view(request):
#     ...
#
# @admin_required
# def admin_view(request):
#     ...