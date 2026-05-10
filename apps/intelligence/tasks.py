"""
Grenier Commun — Tâches IA Métier
Price Predictor · Credit Scorer · Early Warning System
"""
import logging
from celery import shared_task
from django.utils import timezone

logger = logging.getLogger('apps.intelligence')


@shared_task
def generer_recommandations_vente():
    """
    Génère les recommandations de vente hebdomadaires pour chaque denrée.
    Phase MVP : règles expertes basées sur historique de prix.
    Phase V2 : modèle ML (XGBoost) entraîné sur données réelles.
    """
    from apps.silos.models import Denree
    from apps.core.models import PrixMarche, RecommandationVente
    from django.db.models import Avg
    from datetime import timedelta, date

    denrees = Denree.objects.filter(actif=True)
    generees = 0

    for denree in denrees:
        prix_recents = PrixMarche.objects.filter(
            denree=denree
        ).order_by('-date_maj')[:8]  # 8 dernières semaines

        if prix_recents.count() < 2:
            continue

        prix_actuel = float(prix_recents.first().prix_kg_fcfa)
        prix_moyen = float(prix_recents.aggregate(avg=Avg('prix_kg_fcfa'))['avg'] or 0)

        if not prix_moyen:
            continue

        variation = ((prix_actuel - prix_moyen) / prix_moyen) * 100

        # Logique de recommandation MVP (règles expertes)
        if variation >= 15:
            action = 'VENDRE'
            msg_fr = f"Le prix de {denree.nom} est {variation:.1f}% au-dessus de la moyenne des 8 dernières semaines. C'est une bonne période pour vendre."
            msg_en = f"The price of {denree.nom} is {variation:.1f}% above the 8-week average. This is a good time to sell."
            msg_wo = f"{denree.nom_wolof or denree.nom} dafa saf ci kàddu. Yégël la sell."
        elif variation <= -10:
            action = 'ATTENDRE'
            msg_fr = f"Le prix de {denree.nom} est en dessous de la moyenne. Attendez encore 3 à 6 semaines avant de vendre."
            msg_en = f"The price of {denree.nom} is below average. Wait 3 to 6 more weeks before selling."
            msg_wo = f"{denree.nom_wolof or denree.nom} dafa dul saf ci kàddu. Xaar 3 wala 6 ay ayu mbis."
        else:
            action = 'ATTENDRE'
            msg_fr = f"Le prix de {denree.nom} est stable. Attendez une hausse de marché avant de vendre."
            msg_en = f"The price of {denree.nom} is stable. Wait for a market increase before selling."
            msg_wo = f"{denree.nom_wolof or denree.nom} dafa am prix bu baax. Xaar progression bi."

        # Prix prévu (estimation simple : tendance linéaire MVP)
        if prix_recents.count() >= 4:
            old_avg = float(prix_recents[4:].aggregate(avg=Avg('prix_kg_fcfa'))['avg'] or prix_actuel)
            tendance = (prix_actuel - old_avg) / 4  # variation par semaine
            prix_prevu_4 = max(prix_actuel + tendance * 4, 50)
            prix_prevu_8 = max(prix_actuel + tendance * 8, 50)
        else:
            prix_prevu_4 = prix_actuel
            prix_prevu_8 = prix_actuel

        RecommandationVente.objects.create(
            denree=denree,
            action_recommandee=action,
            message_fr=msg_fr,
            message_en=msg_en,
            message_wo=msg_wo,
            prix_actuel_fcfa=prix_actuel,
            prix_prevu_4sem_fcfa=round(prix_prevu_4, 2),
            prix_prevu_8sem_fcfa=round(prix_prevu_8, 2),
            validee_par_admin=False,  # Admin doit valider avant publication
            valide_jusqu_au=date.today() + timedelta(days=7),
        )
        generees += 1

    logger.info(f"Recommandations générées: {generees} denrées")
    return {'generees': generees}


@shared_task
def calculer_score_credit(profil_agriculteur_id):
    """
    Calcule le score de crédit d'un agriculteur basé sur son historique.
    Phase MVP : règles expertes pondérées.
    Phase V2 : modèle de régression logistique entraîné.
    """
    from apps.core.models import ProfilAgriculteur, WarrantageCredit
    from apps.silos.models import Depot

    try:
        profil = ProfilAgriculteur.objects.get(pk=profil_agriculteur_id)
        user = profil.user
    except ProfilAgriculteur.DoesNotExist:
        return

    score = 50  # Score de base

    # 1. Ancienneté dans le système (max +15 pts)
    from django.utils import timezone
    anciennete_mois = (timezone.now() - user.date_joined).days / 30
    score += min(anciennete_mois * 1.5, 15)

    # 2. Nombre de dépôts historiques (max +15 pts)
    nb_depots = Depot.objects.filter(agriculteur=user).count()
    score += min(nb_depots * 2, 15)

    # 3. Historique de remboursement (max +20 pts, -20 si défaut)
    warrantages = WarrantageCredit.objects.filter(agriculteur=user)
    rembourses = warrantages.filter(statut='REMBOURSE').count()
    en_defaut = warrantages.filter(statut='EN_DEFAUT').count()
    score += min(rembourses * 5, 20)
    score -= en_defaut * 20

    # 4. Volume moyen stocké (max +10 pts)
    from django.db.models import Avg
    vol_moyen = Depot.objects.filter(agriculteur=user).aggregate(
        avg=Avg('quantite_initiale_kg')
    )['avg'] or 0
    if vol_moyen >= 1000:
        score += 10
    elif vol_moyen >= 500:
        score += 5
    elif vol_moyen >= 100:
        score += 2

    # Bornes
    score = max(0, min(100, int(score)))

    profil.score_credit = score
    profil.score_calcule_le = timezone.now()
    profil.save(update_fields=['score_credit', 'score_calcule_le'])

    logger.info(f"Score crédit calculé: {user.nom_complet} → {score}/100")
    return {'user': str(user), 'score': score}


@shared_task
def verifier_conditions_silos():
    """
    Vérifie les conditions de conservation de tous les silos actifs.
    Génère des alertes si les seuils sont dépassés.
    """
    from apps.silos.models import Silo, Depot, AlerteSilo

    silos = Silo.objects.filter(statut='ACTIF').prefetch_related('depots')
    alertes_generees = 0

    for silo in silos:
        if not silo.derniere_mesure:
            continue

        # Pour chaque denrée stockée dans le silo
        denrees_en_stock = Depot.objects.filter(
            silo=silo,
            statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
        ).select_related('denree').values_list(
            'denree__humidite_max',
            'denree__temperature_max',
            'denree__temperature_min',
        ).distinct()

        for humidite_max, temp_max, temp_min in denrees_en_stock:
            # Vérif humidité
            if silo.humidite_pourcent and humidite_max:
                if float(silo.humidite_pourcent) > float(humidite_max):
                    niveau = 'ROUGE' if float(silo.humidite_pourcent) > float(humidite_max) * 1.15 else 'ORANGE'
                    AlerteSilo.objects.get_or_create(
                        silo=silo,
                        type_alerte='HUMIDITE',
                        est_acquittee=False,
                        defaults={
                            'niveau': niveau,
                            'message': f"Humidité {silo.humidite_pourcent}% dépasse le seuil de {humidite_max}%. Risque de moisissure.",
                            'valeur_mesuree': f"{silo.humidite_pourcent}%",
                            'valeur_seuil': f"{humidite_max}%",
                        }
                    )
                    alertes_generees += 1

            # Vérif température
            if silo.temperature_celsius and temp_max:
                if float(silo.temperature_celsius) > float(temp_max):
                    niveau = 'ROUGE' if float(silo.temperature_celsius) > float(temp_max) + 5 else 'ORANGE'
                    AlerteSilo.objects.get_or_create(
                        silo=silo,
                        type_alerte='TEMPERATURE',
                        est_acquittee=False,
                        defaults={
                            'niveau': niveau,
                            'message': f"Température {silo.temperature_celsius}°C dépasse le seuil de {temp_max}°C. Risque de fermentation.",
                            'valeur_mesuree': f"{silo.temperature_celsius}°C",
                            'valeur_seuil': f"{temp_max}°C",
                        }
                    )
                    alertes_generees += 1

        # Mise à jour santé globale du silo
        alertes_actives = silo.alertes.filter(est_acquittee=False)
        if alertes_actives.filter(niveau='ROUGE').exists():
            silo.sante = 'ROUGE'
        elif alertes_actives.filter(niveau='ORANGE').exists():
            silo.sante = 'ORANGE'
        else:
            silo.sante = 'VERT'
        silo.save(update_fields=['sante'])

    logger.info(f"Vérification silos: {alertes_generees} alertes générées")
    return {'alertes_generees': alertes_generees}


@shared_task
def calculer_loyers_stockage():
    """
    Calcule et facture les loyers de stockage mensuels.
    1.5% de la valeur du stock par mois.
    """
    from apps.silos.models import Depot
    from django.conf import settings

    depots = Depot.objects.filter(
        statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
    ).select_related('agriculteur', 'denree')

    total_facture = 0
    nb_depots = 0

    for depot in depots:
        if depot.valeur_estimee_fcfa:
            loyer = depot.valeur_estimee_fcfa * settings.GC_TAUX_LOCATION_MENSUEL
            total_facture += loyer
            nb_depots += 1

            # Notification à l'agriculteur
            from apps.notifications.tasks import envoyer_notification
            envoyer_notification.delay(
                user_id=depot.agriculteur.pk,
                canal='SMS',
                contenu=f"Grenier Commun: Loyer de stockage du mois pour votre dépôt {depot.numero_recu}: {loyer:,.0f} FCFA. Merci.",
            )

    logger.info(f"Facturation: {nb_depots} dépôts, total {total_facture:,.0f} FCFA")
    return {'nb_depots': nb_depots, 'total_fcfa': total_facture}
