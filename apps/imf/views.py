"""
Grenier Commun — Vues Espace IMF Partenaire
"""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from apps.core.decorators import role_required
from apps.core.models import WarrantageCredit, IMFPartenaire

logger = logging.getLogger('apps.imf')


def _get_imf(user):
    """Récupère l'IMF partenaire liée à l'utilisateur connecté."""
    try:
        return IMFPartenaire.objects.get(contact_email=user.email, actif=True)
    except IMFPartenaire.DoesNotExist:
        return None


@login_required
@role_required('IMF', 'ADMIN_GC')
def dashboard(request):
    """Tableau de bord IMF."""
    imf = _get_imf(request.user)
    if not imf and request.user.role != 'ADMIN_GC':
        messages.error(request, 'Votre compte n\'est pas lié à une IMF partenaire.')
        return render(request, 'imf/dashboard.html', {'imf': None})

    dossiers_qs = WarrantageCredit.objects.filter(imf=imf) if imf else WarrantageCredit.objects.all()
    dossiers_qs = dossiers_qs.select_related('agriculteur', 'depot__denree', 'depot__silo')

    stats = {
        'en_attente': dossiers_qs.filter(statut='EN_INSTRUCTION').count(),
        'approuves': dossiers_qs.filter(statut__in=['APPROUVE', 'VIRE']).count(),
        'rembourses': dossiers_qs.filter(statut='REMBOURSE').count(),
        'en_defaut': dossiers_qs.filter(statut='EN_DEFAUT').count(),
    }

    dossiers_urgents = dossiers_qs.filter(statut='EN_INSTRUCTION').order_by('date_demande')[:10]

    return render(request, 'imf/dashboard.html', {
        'imf': imf,
        'stats': stats,
        'dossiers_urgents': dossiers_urgents,
    })


@login_required
@role_required('IMF', 'ADMIN_GC')
def dossiers(request):
    """Liste de tous les dossiers de crédit."""
    imf = _get_imf(request.user)
    statut_filtre = request.GET.get('statut', '')

    dossiers_qs = WarrantageCredit.objects.filter(imf=imf) if imf else WarrantageCredit.objects.all()
    dossiers_qs = dossiers_qs.select_related('agriculteur', 'depot__denree', 'depot__silo__commune')

    if statut_filtre:
        dossiers_qs = dossiers_qs.filter(statut=statut_filtre)

    dossiers_qs = dossiers_qs.order_by('-date_demande')

    return render(request, 'imf/dossiers.html', {
        'dossiers': dossiers_qs,
        'statuts': WarrantageCredit.STATUT_CHOICES,
        'statut_filtre': statut_filtre,
    })


@login_required
@role_required('IMF', 'ADMIN_GC')
def detail_dossier(request, pk):
    """Détail complet d'un dossier de warrantage."""
    imf = _get_imf(request.user)
    if imf:
        dossier = get_object_or_404(WarrantageCredit, pk=pk, imf=imf)
    else:
        dossier = get_object_or_404(WarrantageCredit, pk=pk)

    agriculteur = dossier.agriculteur
    profil = getattr(agriculteur, 'profil_agriculteur', None)
    historique = WarrantageCredit.objects.filter(
        agriculteur=agriculteur
    ).exclude(pk=pk).order_by('-date_demande')[:5]

    return render(request, 'imf/detail_dossier.html', {
        'dossier': dossier,
        'profil': profil,
        'historique': historique,
    })


@login_required
@role_required('IMF', 'ADMIN_GC')
def decider_dossier(request, pk):
    """Approuver ou refuser un dossier de warrantage."""
    imf = _get_imf(request.user)
    if imf:
        dossier = get_object_or_404(WarrantageCredit, pk=pk, imf=imf, statut='EN_INSTRUCTION')
    else:
        dossier = get_object_or_404(WarrantageCredit, pk=pk, statut='EN_INSTRUCTION')

    if request.method == 'POST':
        action = request.POST.get('action')
        from apps.notifications.tasks import envoyer_notification

        if action == 'approuver':
            montant = request.POST.get('montant_accorde', '').replace(',', '.')
            taux = request.POST.get('taux_interet', '').replace(',', '.')
            duree = request.POST.get('duree_mois', 3)

            try:
                dossier.montant_accorde_fcfa = float(montant)
                dossier.taux_interet_mensuel = float(taux)
                dossier.duree_mois = int(duree)
                dossier.statut = 'APPROUVE'
                dossier.date_decision = timezone.now()
                dossier.save()

                # Recalculer score crédit
                from apps.intelligence.tasks import calculer_score_credit
                profil = getattr(dossier.agriculteur, 'profil_agriculteur', None)
                if profil:
                    calculer_score_credit.delay(profil.pk)

                envoyer_notification.delay(
                    user_id=dossier.agriculteur.pk,
                    canal='SMS',
                    contenu=(
                        f"Grenier Commun: Votre demande de crédit warrantage "
                        f"WA-{dossier.pk:05d} a été APPROUVÉE. "
                        f"Montant: {float(montant):,.0f} FCFA. "
                        f"Les fonds seront virés sous 48h sur {dossier.numero_paiement or 'votre compte'}."
                    ),
                )
                messages.success(request, f'✅ Dossier WA-{dossier.pk:05d} approuvé pour {float(montant):,.0f} FCFA.')

            except (ValueError, TypeError):
                messages.error(request, 'Montant ou taux invalide.')
                return redirect('imf:detail_dossier', pk=pk)

        elif action == 'refuser':
            motif = request.POST.get('motif_refus', '').strip()
            dossier.statut = 'REFUSE'
            dossier.motif_refus = motif
            dossier.date_decision = timezone.now()
            dossier.save()

            # Libérer le dépôt
            dossier.depot.statut = 'ACTIF'
            dossier.depot.save(update_fields=['statut'])

            envoyer_notification.delay(
                user_id=dossier.agriculteur.pk,
                canal='SMS',
                contenu=(
                    f"Grenier Commun: Votre demande de crédit warrantage "
                    f"WA-{dossier.pk:05d} a été refusée. "
                    f"Motif: {motif[:100] if motif else 'Non communiqué'}. "
                    f"Votre stock reste disponible."
                ),
            )
            messages.warning(request, f'Dossier WA-{dossier.pk:05d} refusé.')

        return redirect('imf:dossiers')

    return render(request, 'imf/decider_dossier.html', {'dossier': dossier})
