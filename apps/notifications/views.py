"""
Grenier Commun — Vues Notifications
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.core.models import Notification


@login_required
def liste(request):
    notifications = Notification.objects.filter(
        destinataire=request.user
    ).order_by('-cree_le')
    # Marquer les in-app comme lues
    Notification.objects.filter(
        destinataire=request.user, canal='APP', statut='ENVOYE'
    ).update(statut='LU', lu_le=timezone.now())
    return render(request, 'notifications/liste.html', {'notifications': notifications})


@login_required
def marquer_lu(request, pk):
    notif = get_object_or_404(Notification, pk=pk, destinataire=request.user)
    notif.statut = 'LU'
    notif.lu_le = timezone.now()
    notif.save(update_fields=['statut', 'lu_le'])
    return redirect('notifications:liste')
