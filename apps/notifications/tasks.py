"""
Grenier Commun — Tâches Celery : Notifications
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('apps.notifications')


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def envoyer_notification(self, user_id, canal, contenu, titre=''):
    """Envoie une notification à un utilisateur via le canal spécifié."""
    try:
        from django.contrib.auth import get_user_model
        from apps.core.models import Notification
        from apps.traduction.services import traduire_sms

        User = get_user_model()
        user = User.objects.get(pk=user_id)

        contenu_traduit = contenu
        langue_envoi = user.langue_preferee

        if canal == 'SMS' and langue_envoi != 'fr':
            contenu_traduit = traduire_sms(contenu, langue_envoi, user)

        notif = Notification.objects.create(
            destinataire=user,
            canal=canal,
            titre=titre,
            contenu=contenu,
            contenu_traduit=contenu_traduit,
            langue_envoi=langue_envoi,
        )

        if canal == 'SMS':
            succes = _envoyer_sms(user, contenu_traduit)
        else:
            succes = True  # Notifications in-app : toujours OK

        notif.statut = 'ENVOYE' if succes else 'ECHEC'
        notif.envoye_le = timezone.now()
        notif.save(update_fields=['statut', 'envoye_le'])

        return {'notif_id': notif.pk, 'succes': succes}

    except Exception as exc:
        logger.error(f"Erreur envoi notification user {user_id}: {exc}")
        raise self.retry(exc=exc)


def _envoyer_sms(user, contenu):
    """Envoie un SMS via Twilio."""
    from django.conf import settings
    if not settings.TWILIO_ACCOUNT_SID:
        logger.info(f"[SMS SIMULÉ] → {user.telephone}: {contenu[:80]}")
        return True
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=contenu,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=str(user.telephone),
        )
        return True
    except Exception as e:
        logger.error(f"Erreur Twilio: {e}")
        return False
