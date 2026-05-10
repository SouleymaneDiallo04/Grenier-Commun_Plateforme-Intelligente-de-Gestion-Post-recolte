"""
Grenier Commun — Vues Espace Acheteur / Marché
"""
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Min, Max
from apps.core.decorators import role_required
from apps.core.models import OffreAchat, PrixMarche, Transaction
from apps.silos.models import Depot, Denree

logger = logging.getLogger('apps.marche')


@login_required
@role_required('ACHETEUR', 'ADMIN_GC')
def dashboard(request):
    """Tableau de bord de l'acheteur."""
    mes_offres = OffreAchat.objects.filter(
        acheteur=request.user
    ).select_related('denree').order_by('-date_offre')[:5]

    offres_actives = OffreAchat.objects.filter(
        acheteur=request.user,
        statut__in=['SOUMISE', 'NEGOCIATION']
    ).count()

    mes_transactions = Transaction.objects.filter(
        offre__acheteur=request.user
    ).select_related('offre__denree').order_by('-date_transaction')[:5]

    # Prix du marché actuels
    prix_recents = PrixMarche.objects.select_related('denree').order_by('-date_maj')[:6]

    return render(request, 'marche/dashboard.html', {
        'mes_offres': mes_offres,
        'offres_actives': offres_actives,
        'mes_transactions': mes_transactions,
        'prix_recents': prix_recents,
    })


@login_required
@role_required('ACHETEUR', 'ADMIN_GC')
def catalogue(request):
    """Catalogue des stocks disponibles dans le réseau."""
    denree_filtre = request.GET.get('denree')
    region_filtre = request.GET.get('region')
    qte_min = request.GET.get('qte_min', '')

    # Agrégation par silo et denrée — pas de données nominatives
    from apps.silos.models import Silo
    stocks = Depot.objects.filter(
        statut='ACTIF'
    ).values(
        'denree__nom', 'denree__id', 'silo__nom', 'silo__commune__nom', 'silo__commune__region'
    ).annotate(
        quantite_totale=Sum('quantite_disponible_kg'),
        prix_min=Min('prix_reference_fcfa'),
        prix_max=Max('prix_reference_fcfa'),
        nb_deposants=Count('agriculteur', distinct=True),
    ).filter(quantite_totale__gt=0)

    if denree_filtre:
        stocks = stocks.filter(denree__id=denree_filtre)
    if region_filtre:
        stocks = stocks.filter(silo__commune__region__icontains=region_filtre)
    if qte_min:
        try:
            stocks = stocks.filter(quantite_totale__gte=float(qte_min))
        except ValueError:
            pass

    denrees = Denree.objects.filter(actif=True)
    prix_ref = PrixMarche.objects.select_related('denree').order_by('-date_maj')[:10]

    return render(request, 'marche/catalogue.html', {
        'stocks': stocks,
        'denrees': denrees,
        'prix_ref': prix_ref,
        'denree_filtre': denree_filtre,
        'region_filtre': region_filtre,
        'qte_min': qte_min,
    })


@login_required
@role_required('ACHETEUR', 'ADMIN_GC')
def nouvelle_offre(request):
    """Soumettre une offre d'achat."""
    denrees = Denree.objects.filter(actif=True)

    if request.method == 'POST':
        denree_id = request.POST.get('denree')
        quantite = request.POST.get('quantite_kg', '0').replace(',', '.')
        prix = request.POST.get('prix_propose_fcfa', '0').replace(',', '.')
        region = request.POST.get('region_preferee', '')
        delai = request.POST.get('delai_souhaite_jours', 30)
        notes = request.POST.get('notes', '')

        try:
            denree = Denree.objects.get(pk=denree_id)
            offre = OffreAchat.objects.create(
                acheteur=request.user,
                denree=denree,
                quantite_kg=float(quantite),
                prix_propose_fcfa=float(prix),
                region_preferee=region,
                delai_souhaite_jours=int(delai),
                notes=notes,
                statut='SOUMISE',
            )
            # Notification admin
            from apps.notifications.tasks import envoyer_notification
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admins = User.objects.filter(role='ADMIN_GC', is_active=True)
            for admin in admins:
                envoyer_notification.delay(
                    user_id=admin.pk,
                    canal='APP',
                    titre='Nouvelle offre d\'achat',
                    contenu=f"Nouvelle offre de {request.user.nom_complet}: {float(quantite):.0f}kg de {denree.nom} à {float(prix):.0f} FCFA/kg.",
                )

            messages.success(request, f'✅ Offre soumise avec succès ! Référence: OFF-{offre.pk:05d}. Notre équipe vous contactera sous 48h.')
            return redirect('marche:detail_offre', pk=offre.pk)

        except Denree.DoesNotExist:
            messages.error(request, 'Denrée invalide.')
        except (ValueError, TypeError):
            messages.error(request, 'Valeurs invalides.')

    # Prix de référence pour pré-remplir
    prix_suggestions = {p.denree_id: p.prix_kg_fcfa for p in PrixMarche.objects.order_by('-date_maj')}

    return render(request, 'marche/nouvelle_offre.html', {
        'denrees': denrees,
        'prix_suggestions': prix_suggestions,
    })


@login_required
@role_required('ACHETEUR', 'ADMIN_GC')
def detail_offre(request, pk):
    """Détail d'une offre d'achat."""
    if request.user.role == 'ADMIN_GC':
        offre = get_object_or_404(OffreAchat, pk=pk)
    else:
        offre = get_object_or_404(OffreAchat, pk=pk, acheteur=request.user)

    return render(request, 'marche/detail_offre.html', {'offre': offre})


@login_required
@role_required('ACHETEUR', 'ADMIN_GC')
def mes_transactions(request):
    """Historique des transactions finalisées."""
    if request.user.role == 'ADMIN_GC':
        transactions = Transaction.objects.all()
    else:
        transactions = Transaction.objects.filter(offre__acheteur=request.user)

    transactions = transactions.select_related(
        'offre__acheteur', 'offre__denree'
    ).order_by('-date_transaction')

    return render(request, 'marche/mes_transactions.html', {'transactions': transactions})
