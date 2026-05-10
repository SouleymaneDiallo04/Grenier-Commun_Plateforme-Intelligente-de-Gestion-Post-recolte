"""
Grenier Commun — Décorateurs de contrôle d'accès par rôle
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """
    Décorateur qui vérifie que l'utilisateur connecté possède l'un des rôles autorisés.
    Usage : @role_required('AGRICULTEUR', 'ADMIN_GC')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:connexion')
            if request.user.role not in roles and not request.user.is_superuser:
                messages.error(request, "Vous n'avez pas accès à cette section.")
                return redirect(request.user.get_dashboard_url())
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
