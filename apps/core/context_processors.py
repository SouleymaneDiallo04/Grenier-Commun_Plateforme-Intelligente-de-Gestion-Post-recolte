def grenier_commun_context(request):
    context = {'app_name': 'Grenier Commun'}
    if request.user.is_authenticated:
        from apps.core.models import Notification
        context['notifications_non_lues'] = Notification.objects.filter(
            destinataire=request.user,
            statut__in=['EN_ATTENTE', 'ENVOYE'],
            canal='APP'
        ).count()
    return context
