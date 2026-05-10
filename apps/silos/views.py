"""
Grenier Commun — Vues Espace Gestionnaire de Silo
"""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Count
from apps.core.decorators import role_required
from .models import Silo, Depot, Retrait, AlerteSilo, Denree

logger = logging.getLogger('apps.silos')


@login_required
@role_required('GESTIONNAIRE', 'ADMIN_GC')
def dashboard(request):
    """Tableau de bord du gestionnaire de silo."""
    try:
        silo = Silo.objects.get(gestionnaire=request.user, statut='ACTIF')
    except Silo.DoesNotExist:
        messages.warning(request, 'Aucun silo actif ne vous est assigné.')
        return render(request, 'silos/dashboard.html', {'silo': None})
    except Silo.MultipleObjectsReturned:
        silo = Silo.objects.filter(gestionnaire=request.user, statut='ACTIF').first()

    depots_actifs = Depot.objects.filter(
        silo=silo, statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
    ).select_related('agriculteur', 'denree').order_by('-date_depot')

    alertes = AlerteSilo.objects.filter(
        silo=silo, est_acquittee=False
    ).order_by('-cree_le')

    derniers_depots = depots_actifs[:8]

    stats = {
        'nb_depots': depots_actifs.count(),
        'stock_total_kg': depots_actifs.aggregate(t=Sum('quantite_disponible_kg'))['t'] or 0,
        'nb_alertes': alertes.count(),
        'nb_agriculteurs': depots_actifs.values('agriculteur').distinct().count(),
    }

    return render(request, 'silos/dashboard.html', {
        'silo': silo,
        'depots_actifs': derniers_depots,
        'alertes': alertes,
        'stats': stats,
    })


@login_required
@role_required('GESTIONNAIRE', 'ADMIN_GC')
def nouveau_depot(request):
    """Enregistrer un nouveau dépôt dans le silo."""
    try:
        silo = Silo.objects.get(gestionnaire=request.user, statut='ACTIF')
    except Silo.DoesNotExist:
        messages.error(request, 'Aucun silo actif assigné.')
        return redirect('silos:dashboard')
    except Silo.MultipleObjectsReturned:
        silo = Silo.objects.filter(gestionnaire=request.user, statut='ACTIF').first()

    from django.contrib.auth import get_user_model
    User = get_user_model()
    agriculteurs = User.objects.filter(role='AGRICULTEUR', is_active=True).order_by('nom')
    denrees = Denree.objects.filter(actif=True)

    if request.method == 'POST':
        agriculteur_id = request.POST.get('agriculteur')
        denree_id = request.POST.get('denree')
        quantite = request.POST.get('quantite_kg', '0').replace(',', '.')
        prix_ref = request.POST.get('prix_reference_fcfa', '').replace(',', '.')
        observations = request.POST.get('observations', '')

        try:
            quantite_kg = float(quantite)
            if quantite_kg <= 0:
                raise ValueError()
        except ValueError:
            messages.error(request, 'Quantité invalide.')
            return render(request, 'silos/nouveau_depot.html', {
                'silo': silo, 'agriculteurs': agriculteurs, 'denrees': denrees,
            })

        if silo.capacite_disponible_kg < quantite_kg:
            messages.error(request, f'Capacité insuffisante. Disponible: {silo.capacite_disponible_kg} kg.')
            return render(request, 'silos/nouveau_depot.html', {
                'silo': silo, 'agriculteurs': agriculteurs, 'denrees': denrees,
            })

        try:
            agriculteur = User.objects.get(pk=agriculteur_id, role='AGRICULTEUR')
            denree = Denree.objects.get(pk=denree_id)
        except (User.DoesNotExist, Denree.DoesNotExist):
            messages.error(request, 'Agriculteur ou denrée invalide.')
            return render(request, 'silos/nouveau_depot.html', {
                'silo': silo, 'agriculteurs': agriculteurs, 'denrees': denrees,
            })

        depot = Depot.objects.create(
            agriculteur=agriculteur,
            silo=silo,
            gestionnaire=request.user,
            denree=denree,
            quantite_initiale_kg=quantite_kg,
            quantite_disponible_kg=quantite_kg,
            prix_reference_fcfa=prix_ref if prix_ref else None,
            observations=observations,
        )

        # Mise à jour stock silo
        silo.stock_actuel_kg += int(quantite_kg)
        silo.save(update_fields=['stock_actuel_kg'])

        # SMS de confirmation à l'agriculteur
        from apps.notifications.tasks import envoyer_notification
        envoyer_notification.delay(
            user_id=agriculteur.pk,
            canal='SMS',
            contenu=(
                f"Grenier Commun: Dépôt confirmé. "
                f"Reçu N°{depot.numero_recu} — "
                f"{quantite_kg:.0f}kg de {denree.nom} dans le silo {silo.nom}. "
                f"Conservez ce numéro."
            ),
        )

        messages.success(
            request,
            f'✅ Dépôt enregistré ! Reçu N°{depot.numero_recu} — SMS envoyé à {agriculteur.nom_complet}.'
        )
        return redirect('silos:detail_depot', pk=depot.pk)

    return render(request, 'silos/nouveau_depot.html', {
        'silo': silo,
        'agriculteurs': agriculteurs,
        'denrees': denrees,
    })


@login_required
@role_required('GESTIONNAIRE', 'ADMIN_GC')
def detail_depot(request, pk):
    """Détail d'un dépôt — vue gestionnaire."""
    depot = get_object_or_404(Depot, pk=pk)
    retraits = depot.retraits.all().order_by('-date_retrait')
    warrantage = getattr(depot, 'warrantage', None)
    return render(request, 'silos/detail_depot.html', {
        'depot': depot,
        'retraits': retraits,
        'warrantage': warrantage,
    })


@login_required
@role_required('GESTIONNAIRE', 'ADMIN_GC')
def enregistrer_retrait(request, depot_pk):
    """Enregistrer un retrait ou une sortie de stock."""
    depot = get_object_or_404(Depot, pk=depot_pk)
    silo = depot.silo

    if depot.statut == 'WARRANTE':
        messages.error(request, 'Ce dépôt est sous warrantage actif — retrait impossible sans remboursement du crédit.')
        return redirect('silos:detail_depot', pk=depot_pk)

    if request.method == 'POST':
        quantite = float(request.POST.get('quantite_kg', '0').replace(',', '.'))
        type_retrait = request.POST.get('type_retrait', 'RETRAIT')
        prix_vente = request.POST.get('prix_vente_fcfa', '').replace(',', '.')
        observations = request.POST.get('observations', '')

        if quantite <= 0 or quantite > float(depot.quantite_disponible_kg):
            messages.error(request, f'Quantité invalide. Maximum disponible: {depot.quantite_disponible_kg} kg.')
            return redirect('silos:enregistrer_retrait', depot_pk=depot_pk)

        retrait = Retrait.objects.create(
            depot=depot,
            gestionnaire=request.user,
            quantite_kg=quantite,
            type_retrait=type_retrait,
            prix_vente_fcfa=prix_vente if prix_vente else None,
            observations=observations,
        )

        # Mise à jour quantité disponible
        depot.quantite_disponible_kg -= quantite
        if depot.quantite_disponible_kg <= 0:
            depot.statut = 'VENDU' if type_retrait == 'VENTE' else 'RETIRE'
        else:
            depot.statut = 'PARTIEL'
        depot.save(update_fields=['quantite_disponible_kg', 'statut'])

        # Mise à jour stock silo
        silo.stock_actuel_kg = max(0, silo.stock_actuel_kg - int(quantite))
        silo.save(update_fields=['stock_actuel_kg'])

        # Notification SMS
        from apps.notifications.tasks import envoyer_notification
        msg = f"Grenier Commun: Retrait de {quantite:.0f}kg de {depot.denree.nom} enregistré. Stock restant: {depot.quantite_disponible_kg:.0f}kg."
        if type_retrait == 'VENTE' and prix_vente:
            montant = float(quantite) * float(prix_vente)
            msg = f"Grenier Commun: Vente de {quantite:.0f}kg de {depot.denree.nom} à {float(prix_vente):.0f} FCFA/kg. Total: {montant:,.0f} FCFA."

        envoyer_notification.delay(user_id=depot.agriculteur.pk, canal='SMS', contenu=msg)

        messages.success(request, f'✅ Retrait de {quantite:.0f} kg enregistré.')
        return redirect('silos:detail_depot', pk=depot_pk)

    return render(request, 'silos/enregistrer_retrait.html', {'depot': depot})


@login_required
@role_required('GESTIONNAIRE', 'ADMIN_GC')
def alertes(request):
    """Liste de toutes les alertes du silo."""
    silo = Silo.objects.filter(gestionnaire=request.user).first()

    alertes_qs = AlerteSilo.objects.filter(
        silo=silo, est_acquittee=False
    ).order_by('-cree_le') if silo else AlerteSilo.objects.none()

    return render(request, 'silos/alertes.html', {
        'alertes': alertes_qs, 'silo': silo,
    })


@login_required
@role_required('GESTIONNAIRE', 'ADMIN_GC')
def acquitter_alerte(request, pk):
    """Acquitter une alerte avec commentaire."""
    alerte = get_object_or_404(AlerteSilo, pk=pk)
    if request.method == 'POST':
        commentaire = request.POST.get('commentaire', '').strip()
        alerte.est_acquittee = True
        alerte.acquittee_par = request.user
        alerte.commentaire_acquittement = commentaire
        alerte.acquittee_le = timezone.now()
        alerte.save()
        messages.success(request, 'Alerte acquittée.')
    return redirect('silos:alertes')


@login_required
@role_required('GESTIONNAIRE', 'ADMIN_GC')
def mettre_a_jour_conditions(request):
    """Saisie manuelle des conditions du silo (température, humidité)."""
    silo = Silo.objects.filter(gestionnaire=request.user).first()
    if not silo:
        messages.error(request, 'Aucun silo assigné.')
        return redirect('silos:dashboard')

    if request.method == 'POST':
        temperature = request.POST.get('temperature_celsius', '').replace(',', '.')
        humidite = request.POST.get('humidite_pourcent', '').replace(',', '.')
        try:
            if temperature:
                silo.temperature_celsius = float(temperature)
            if humidite:
                silo.humidite_pourcent = float(humidite)
            silo.derniere_mesure = timezone.now()
            silo.save()

            # Lancer la vérification des conditions
            from apps.intelligence.tasks import verifier_conditions_silos
            verifier_conditions_silos.delay()

            messages.success(request, '✅ Conditions mises à jour. Vérification des alertes en cours...')
        except ValueError:
            messages.error(request, 'Valeurs invalides.')

    return redirect('silos:dashboard')


@login_required
@role_required('GESTIONNAIRE', 'ADMIN_GC')
def rapport_mensuel(request):
    """Rapport mensuel d'activité du silo."""
    silo = Silo.objects.filter(gestionnaire=request.user).first()
    if not silo:
        messages.error(request, 'Aucun silo assigné.')
        return redirect('silos:dashboard')

    from django.utils import timezone as tz
    now = tz.now()
    debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    depots_mois = Depot.objects.filter(silo=silo, date_depot__gte=debut_mois)
    retraits_mois = Retrait.objects.filter(depot__silo=silo, date_retrait__gte=debut_mois)

    stats_mois = {
        'nb_depots': depots_mois.count(),
        'kg_entres': depots_mois.aggregate(t=Sum('quantite_initiale_kg'))['t'] or 0,
        'nb_retraits': retraits_mois.count(),
        'kg_sortis': retraits_mois.aggregate(t=Sum('quantite_kg'))['t'] or 0,
        'nb_alertes': AlerteSilo.objects.filter(silo=silo, cree_le__gte=debut_mois).count(),
    }

    return render(request, 'silos/rapport_mensuel.html', {
        'silo': silo,
        'stats_mois': stats_mois,
        'mois': now.strftime('%B %Y'),
        'depots_mois': depots_mois.select_related('agriculteur', 'denree'),
    })
