"""
Grenier Commun — Vues Administration GC
"""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from apps.core.decorators import role_required

logger = logging.getLogger('apps.administration')


@login_required
@role_required('ADMIN_GC')
def dashboard(request):
    """Cockpit central — vue globale du réseau Grenier Commun."""
    from apps.silos.models import Silo, Depot, AlerteSilo
    from apps.core.models import WarrantageCredit, OffreAchat, Transaction
    from django.contrib.auth import get_user_model
    User = get_user_model()

    # ── KPIs globaux ────────────────────────────────────────────────────────
    kpis = {
        'silos_actifs': Silo.objects.filter(statut='ACTIF').count(),
        'tonnes_stockees': Depot.objects.filter(
            statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
        ).aggregate(total=Sum('quantite_disponible_kg'))['total'] or 0,
        'agriculteurs': User.objects.filter(role='AGRICULTEUR', is_active=True).count(),
        'alertes_actives': AlerteSilo.objects.filter(est_acquittee=False).count(),
        'credits_en_cours': WarrantageCredit.objects.filter(
            statut__in=['SOUMIS', 'EN_INSTRUCTION', 'APPROUVE', 'VIRE']
        ).count(),
        'offres_en_attente': OffreAchat.objects.filter(statut='SOUMISE').count(),
    }

    kpis['tonnes_stockees_t'] = round(float(kpis['tonnes_stockees']) / 1000, 1)

    # ── Valeur totale des stocks ─────────────────────────────────────────────
    depots = Depot.objects.filter(
        statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
    ).select_related('denree')
    valeur_totale = sum(d.valeur_estimee_fcfa or 0 for d in depots)

    # ── Alertes critiques (ROUGE) ────────────────────────────────────────────
    alertes_critiques = AlerteSilo.objects.filter(
        est_acquittee=False, niveau='ROUGE'
    ).select_related('silo', 'silo__commune').order_by('-cree_le')[:5]

    # ── Silos pour la carte ──────────────────────────────────────────────────
    silos = Silo.objects.filter(
        latitude__isnull=False
    ).select_related('commune', 'gestionnaire').annotate(
        nb_depots=Count('depots', filter=Q(depots__statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']))
    )

    silos_json = [
        {
            'id': s.pk,
            'nom': s.nom,
            'commune': s.commune.nom,
            'lat': float(s.latitude),
            'lng': float(s.longitude),
            'sante': s.sante,
            'taux': s.taux_remplissage,
            'nb_depots': s.nb_depots,
        }
        for s in silos
    ]

    # ── Dernières demandes warrantage ────────────────────────────────────────
    derniers_warrantages = WarrantageCredit.objects.filter(
        statut='SOUMIS'
    ).select_related('agriculteur', 'depot__denree').order_by('-date_demande')[:5]

    # ── Revenus du mois ──────────────────────────────────────────────────────
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    transactions_mois = Transaction.objects.filter(date_transaction__gte=debut_mois)
    revenus_commissions = transactions_mois.aggregate(
        total=Sum('commission_gc_fcfa')
    )['total'] or 0

    import json
    return render(request, 'administration/dashboard.html', {
        'kpis': kpis,
        'valeur_totale': valeur_totale,
        'alertes_critiques': alertes_critiques,
        'silos_json': json.dumps(silos_json),
        'derniers_warrantages': derniers_warrantages,
        'revenus_commissions': revenus_commissions,
    })


@login_required
@role_required('ADMIN_GC')
def gestion_silos(request):
    """Gestion du réseau de silos."""
    from apps.silos.models import Silo, Commune
    silos = Silo.objects.select_related(
        'commune', 'gestionnaire'
    ).annotate(
        nb_depots_actifs=Count('depots', filter=Q(depots__statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']))
    ).order_by('commune__region', 'nom')

    return render(request, 'administration/gestion_silos.html', {'silos': silos})


@login_required
@role_required('ADMIN_GC')
def gestion_utilisateurs(request):
    """Gestion de tous les utilisateurs."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    role_filtre = request.GET.get('role', '')
    users = User.objects.all().order_by('-date_joined')
    if role_filtre:
        users = users.filter(role=role_filtre)

    # Validation d'un acheteur
    if request.method == 'POST' and request.POST.get('action') == 'valider_acheteur':
        user_id = request.POST.get('user_id')
        try:
            u = User.objects.get(pk=user_id, role='ACHETEUR')
            u.is_verified = True
            u.save(update_fields=['is_verified'])
            messages.success(request, f'✅ Compte acheteur {u.nom_complet} validé.')
        except User.DoesNotExist:
            messages.error(request, 'Utilisateur introuvable.')
        return redirect('administration:gestion_utilisateurs')

    return render(request, 'administration/gestion_utilisateurs.html', {
        'users': users,
        'roles': User.ROLE_CHOICES,
        'role_filtre': role_filtre,
    })


@login_required
@role_required('ADMIN_GC')
def gestion_warrantage(request):
    """Supervision de tous les warrantages."""
    from apps.core.models import WarrantageCredit, IMFPartenaire
    statut_filtre = request.GET.get('statut', 'SOUMIS')
    warrantages = WarrantageCredit.objects.select_related(
        'agriculteur', 'depot__denree', 'depot__silo', 'imf'
    ).order_by('-date_demande')

    if statut_filtre:
        warrantages = warrantages.filter(statut=statut_filtre)

    imfs = IMFPartenaire.objects.filter(actif=True)

    # Transmission à une IMF
    if request.method == 'POST' and request.POST.get('action') == 'transmettre_imf':
        wid = request.POST.get('warrantage_id', '').strip()
        imf_id = request.POST.get('imf_id', '').strip()
        if not imf_id:
            messages.error(request, 'Veuillez sélectionner une IMF partenaire.')
            return redirect('administration:gestion_warrantage')
        try:
            w = WarrantageCredit.objects.get(pk=wid, statut='SOUMIS')
            imf = IMFPartenaire.objects.get(pk=imf_id)
            w.imf = imf
            w.statut = 'EN_INSTRUCTION'
            w.save(update_fields=['imf', 'statut'])

            from apps.notifications.tasks import envoyer_notification
            envoyer_notification.delay(
                user_id=w.agriculteur.pk,
                canal='SMS',
                contenu=f"Votre demande de warrantage WA-{w.pk:05d} a été transmise à {imf.nom}. Délai de traitement: {imf.delai_traitement_jours} jours.",
            )
            messages.success(request, f'Dossier WA-{w.pk:05d} transmis à {imf.nom}.')
        except (WarrantageCredit.DoesNotExist, IMFPartenaire.DoesNotExist):
            messages.error(request, 'Erreur lors de la transmission.')
        return redirect('administration:gestion_warrantage')

    return render(request, 'administration/gestion_warrantage.html', {
        'warrantages': warrantages,
        'imfs': imfs,
        'statuts': WarrantageCredit.STATUT_CHOICES,
        'statut_filtre': statut_filtre,
    })


@login_required
@role_required('ADMIN_GC')
def gestion_marche(request):
    """Gestion des offres d'achat et matching."""
    from apps.core.models import OffreAchat
    from apps.silos.models import Depot

    offres = OffreAchat.objects.select_related(
        'acheteur', 'denree'
    ).order_by('-date_offre')

    # Matching : proposer des dépôts disponibles pour une offre
    offre_id = request.GET.get('matcher')
    depots_correspondants = []
    offre_selectionnee = None

    if offre_id:
        try:
            offre_selectionnee = OffreAchat.objects.get(pk=offre_id)
            depots_correspondants = Depot.objects.filter(
                denree=offre_selectionnee.denree,
                statut='ACTIF',
                quantite_disponible_kg__gte=offre_selectionnee.quantite_kg * 0.3,
            ).select_related('agriculteur', 'silo', 'silo__commune')
        except OffreAchat.DoesNotExist:
            pass

    return render(request, 'administration/gestion_marche.html', {
        'offres': offres,
        'offre_selectionnee': offre_selectionnee,
        'depots_correspondants': depots_correspondants,
    })


@login_required
@role_required('ADMIN_GC')
def finances(request):
    """Vue financière globale."""
    from apps.core.models import Transaction, WarrantageCredit
    from apps.silos.models import Depot
    from django.db.models import Sum

    transactions = Transaction.objects.select_related(
        'offre__acheteur', 'offre__denree'
    ).order_by('-date_transaction')[:50]

    stats = {
        'total_commissions_vente': Transaction.objects.aggregate(
            t=Sum('commission_gc_fcfa'))['t'] or 0,
        'total_warrantages_actifs': WarrantageCredit.objects.filter(
            statut__in=['APPROUVE', 'VIRE']
        ).aggregate(t=Sum('montant_accorde_fcfa'))['t'] or 0,
    }

    return render(request, 'administration/finances.html', {
        'transactions': transactions,
        'stats': stats,
    })


@login_required
@role_required('ADMIN_GC')
def donnees(request):
    """Données agrégées et rapports."""
    from apps.silos.models import Denree, Depot
    from apps.core.models import PrixMarche, RecommandationVente
    from django.db.models import Sum

    # Volumes par denrée
    volumes = Depot.objects.filter(
        statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
    ).values('denree__nom').annotate(
        total_kg=Sum('quantite_disponible_kg')
    ).order_by('-total_kg')

    # Recommandations à valider
    reco_en_attente = RecommandationVente.objects.filter(
        validee_par_admin=False
    ).select_related('denree').order_by('-cree_le')

    if request.method == 'POST' and request.POST.get('action') == 'valider_reco':
        reco_id = request.POST.get('reco_id')
        try:
            reco = RecommandationVente.objects.get(pk=reco_id)
            reco.validee_par_admin = True
            reco.save(update_fields=['validee_par_admin'])
            messages.success(request, f'Recommandation validée pour {reco.denree.nom}.')
        except RecommandationVente.DoesNotExist:
            messages.error(request, 'Recommandation introuvable.')
        return redirect('administration:donnees')

    return render(request, 'administration/donnees.html', {
        'volumes': volumes,
        'reco_en_attente': reco_en_attente,
    })


@login_required
@role_required('ADMIN_GC')
def traductions(request):
    """Supervision du module traduction — corrections soumises."""
    from apps.core.models import TranslationLog
    logs = TranslationLog.objects.filter(
        suggestion_correction__gt=''
    ).select_related('user').order_by('-cree_le')

    # Marquer une correction comme traitée
    if request.method == 'POST':
        log_id = request.POST.get('log_id')
        try:
            log = TranslationLog.objects.get(pk=log_id)
            log.correction_traitee = True
            log.save(update_fields=['correction_traitee'])
            messages.success(request, 'Correction marquée comme traitée.')
        except TranslationLog.DoesNotExist:
            pass
        return redirect('administration:traductions')

    # Stats qualité
    from django.db.models import Avg
    stats_qualite = TranslationLog.objects.filter(
        note_qualite__isnull=False
    ).values('langue_cible').annotate(avg_note=Avg('note_qualite'))

    return render(request, 'administration/traductions.html', {
        'logs': logs,
        'stats_qualite': stats_qualite,
    })
