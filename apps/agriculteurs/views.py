"""
Grenier Commun — Vues Espace Agriculteur
"""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from django.utils import timezone
from apps.silos.models import Depot, Retrait
from apps.core.models import WarrantageCredit, PrixMarche, RecommandationVente
from apps.core.decorators import role_required

logger = logging.getLogger('apps.agriculteurs')


@login_required
@role_required('AGRICULTEUR')
def dashboard(request):
    """Tableau de bord principal de l'agriculteur."""
    user = request.user

    # Stocks actifs
    depots_actifs = Depot.objects.filter(
        agriculteur=user,
        statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
    ).select_related('silo', 'silo__commune', 'denree')

    # Statistiques
    stock_total_kg = depots_actifs.aggregate(
        total=Sum('quantite_disponible_kg')
    )['total'] or 0

    valeur_totale = sum(
        d.valeur_estimee_fcfa or 0 for d in depots_actifs
    )

    # Crédits warrantage en cours
    credits_actifs = WarrantageCredit.objects.filter(
        agriculteur=user,
        statut__in=['APPROUVE', 'VIRE']
    ).count()

    # Recommandations de la semaine
    recommandations = RecommandationVente.objects.filter(
        validee_par_admin=True,
        valide_jusqu_au__gte=timezone.now().date()
    ).select_related('denree')[:5]

    # Dernières notifications non lues
    from apps.core.models import Notification
    notifications = Notification.objects.filter(
        destinataire=user,
        canal='APP',
        statut__in=['ENVOYE', 'EN_ATTENTE']
    ).order_by('-cree_le')[:5]

    # Alertes sur ses silos
    alertes = []
    for depot in depots_actifs:
        alertes_silo = depot.silo.alertes.filter(
            est_acquittee=False,
            niveau__in=['ORANGE', 'ROUGE']
        )
        alertes.extend(alertes_silo)

    contexte = {
        'depots_actifs': depots_actifs,
        'stock_total_kg': stock_total_kg,
        'valeur_totale': valeur_totale,
        'credits_actifs': credits_actifs,
        'recommandations': recommandations,
        'notifications': notifications,
        'alertes': alertes[:3],
        'nb_depots': depots_actifs.count(),
    }
    return render(request, 'agriculteurs/dashboard.html', contexte)


@login_required
@role_required('AGRICULTEUR')
def mes_stocks(request):
    """Liste complète des dépôts de l'agriculteur."""
    statut_filtre = request.GET.get('statut', '')
    depots = Depot.objects.filter(agriculteur=request.user).select_related(
        'silo', 'silo__commune', 'denree'
    )
    if statut_filtre:
        depots = depots.filter(statut=statut_filtre)

    return render(request, 'agriculteurs/mes_stocks.html', {
        'depots': depots,
        'statuts': Depot.STATUT_CHOICES,
        'statut_filtre': statut_filtre,
    })


@login_required
@role_required('AGRICULTEUR')
def detail_depot(request, pk):
    """Détail d'un dépôt avec reçu, historique retraits, traduction."""
    depot = get_object_or_404(Depot, pk=pk, agriculteur=request.user)
    retraits = depot.retraits.all().order_by('-date_retrait')
    warrantage = getattr(depot, 'warrantage', None)
    langues = {
        'fr': {'nom': 'Français', 'flag': '🇫🇷'},
        'en': {'nom': 'English', 'flag': '🇬🇧'},
        'wo': {'nom': 'Wolof', 'flag': '🇸🇳'},
    }
    return render(request, 'agriculteurs/detail_depot.html', {
        'depot': depot,
        'retraits': retraits,
        'warrantage': warrantage,
        'langues': langues,
    })


@login_required
@role_required('AGRICULTEUR')
def prix_marche(request):
    """Prix du marché et recommandations de vente."""
    denree_filtre = request.GET.get('denree')
    prix = PrixMarche.objects.all().select_related('denree').order_by('-date_maj')
    if denree_filtre:
        prix = prix.filter(denree__id=denree_filtre)

    from apps.silos.models import Denree
    denrees = Denree.objects.filter(actif=True)
    recommandations = RecommandationVente.objects.filter(
        validee_par_admin=True
    ).select_related('denree').order_by('-cree_le')[:10]

    return render(request, 'agriculteurs/prix_marche.html', {
        'prix': prix,
        'denrees': denrees,
        'recommandations': recommandations,
        'denree_filtre': denree_filtre,
    })


@login_required
@role_required('AGRICULTEUR')
def mes_warrantages(request):
    """Liste des demandes de warrantage."""
    warrantages = WarrantageCredit.objects.filter(
        agriculteur=request.user
    ).select_related('depot', 'depot__denree', 'imf').order_by('-date_demande')

    return render(request, 'agriculteurs/mes_warrantages.html', {
        'warrantages': warrantages,
    })


@login_required
@role_required('AGRICULTEUR')
def demander_warrantage(request, depot_pk):
    """Formulaire de demande de crédit warrantage."""
    depot = get_object_or_404(Depot, pk=depot_pk, agriculteur=request.user)

    # Vérifications
    if depot.statut == 'WARRANTE':
        messages.error(request, 'Ce dépôt est déjà sous warrantage.')
        return redirect('agriculteurs:detail_depot', pk=depot_pk)
    if hasattr(depot, 'warrantage'):
        messages.error(request, 'Une demande existe déjà pour ce dépôt.')
        return redirect('agriculteurs:detail_depot', pk=depot_pk)
    if not depot.valeur_estimee_fcfa:
        messages.error(request, 'Impossible de calculer la valeur du stock — prix de référence manquant.')
        return redirect('agriculteurs:detail_depot', pk=depot_pk)

    from apps.core.models import IMFPartenaire
    imfs = IMFPartenaire.objects.filter(actif=True)
    montant_max = depot.montant_warrantable_fcfa

    if request.method == 'POST':
        montant = float(request.POST.get('montant', 0))
        imf_id = request.POST.get('imf')
        mode_paiement = request.POST.get('mode_paiement', 'Wave')
        numero_paiement = request.POST.get('numero_paiement', '')
        duree = int(request.POST.get('duree_mois', 3))

        if montant <= 0 or montant > montant_max:
            messages.error(request, f'Montant invalide. Maximum autorisé : {montant_max:,.0f} FCFA')
        else:
            try:
                imf = IMFPartenaire.objects.get(pk=imf_id)

                # Score IA snapshot
                score = getattr(getattr(request.user, 'profil_agriculteur', None), 'score_credit', 50)

                warrantage = WarrantageCredit.objects.create(
                    depot=depot,
                    imf=imf,
                    agriculteur=request.user,
                    montant_demande_fcfa=montant,
                    duree_mois=duree,
                    mode_paiement=mode_paiement,
                    numero_paiement=numero_paiement,
                    score_credit_snapshot=score,
                    statut='SOUMIS',
                )
                depot.statut = 'WARRANTE'
                depot.save(update_fields=['statut'])

                # Notification SMS
                from apps.notifications.tasks import envoyer_notification
                envoyer_notification.delay(
                    user_id=request.user.pk,
                    canal='SMS',
                    contenu=f"Votre demande de crédit warrantage de {montant:,.0f} FCFA a été soumise avec succès. Référence: WA-{warrantage.pk:05d}",
                )

                messages.success(request, '✅ Demande de warrantage soumise avec succès ! Vous serez notifié dès la décision.')
                return redirect('agriculteurs:mes_warrantages')

            except IMFPartenaire.DoesNotExist:
                messages.error(request, 'IMF invalide.')

    return render(request, 'agriculteurs/demander_warrantage.html', {
        'depot': depot,
        'imfs': imfs,
        'montant_max': montant_max,
        'valeur_stock': depot.valeur_estimee_fcfa,
    })


@login_required
@role_required('AGRICULTEUR')
def mes_ventes(request):
    """Historique des ventes."""
    from apps.silos.models import Retrait
    ventes = Retrait.objects.filter(
        depot__agriculteur=request.user,
        type_retrait='VENTE'
    ).select_related('depot', 'depot__denree', 'depot__silo').order_by('-date_retrait')

    return render(request, 'agriculteurs/mes_ventes.html', {'ventes': ventes})


@login_required
@role_required('AGRICULTEUR')
def mon_profil(request):
    """Profil de l'agriculteur."""
    from apps.core.models import ProfilAgriculteur
    profil, created = ProfilAgriculteur.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        request.user.nom = request.POST.get('nom', request.user.nom)
        request.user.prenom = request.POST.get('prenom', request.user.prenom)
        request.user.langue_preferee = request.POST.get('langue_preferee', request.user.langue_preferee)
        request.user.save(update_fields=['nom', 'prenom', 'langue_preferee'])

        profil.village = request.POST.get('village', profil.village)
        profil.superficie_ha = request.POST.get('superficie_ha') or None
        profil.bio = request.POST.get('bio', profil.bio)
        profil.save()
        messages.success(request, '✅ Profil mis à jour.')
        return redirect('agriculteurs:mon_profil')

    return render(request, 'agriculteurs/mon_profil.html', {
        'profil': profil,
        'langues': {'fr': 'Français', 'en': 'English', 'wo': 'Wolof'},
    })
