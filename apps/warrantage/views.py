"""
Grenier Commun — Vues Warrantage
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.core.models import WarrantageCredit


@login_required
def detail_demande(request, pk):
    if request.user.role == 'ADMIN_GC':
        w = get_object_or_404(WarrantageCredit, pk=pk)
    else:
        w = get_object_or_404(WarrantageCredit, pk=pk, agriculteur=request.user)
    return render(request, 'warrantage/detail.html', {'warrantage': w})
