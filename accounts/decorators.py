from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_admin_role:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Administrator privileges are required.")
        return redirect('dashboard:index')
    return _wrapped_view


def coordinator_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_coordinator_role or request.user.is_admin_role:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Club Coordinator privileges are required.")
        return redirect('dashboard:index')
    return _wrapped_view


def student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_student_role or request.user.is_admin_role:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Student account is required.")
        return redirect('dashboard:index')
    return _wrapped_view


def coordinator_or_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if request.user.is_coordinator_role or request.user.is_admin_role:
            return view_func(request, *args, **kwargs)
        messages.error(request, "Access denied. Coordinator or Admin permissions are required.")
        return redirect('dashboard:index')
    return _wrapped_view
