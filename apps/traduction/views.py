"""
Grenier Commun — Vues Module Traduction IA
"""
import json
import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.conf import settings
from .services import traduire
from apps.core.models import TranslationLog

logger = logging.getLogger('apps.traduction')


@login_required
def traduire(request):
    """Page principale du module traduction."""
    langues = settings.SUPPORTED_LANGUAGES
    resultat = None
    log_id = None

    if request.method == 'POST':
        texte = request.POST.get('texte', '').strip()
        langue_source = request.POST.get('langue_source', 'fr')
        langue_cible = request.POST.get('langue_cible', 'wo')
        type_contenu = request.POST.get('type_contenu', 'AUTRE')

        if texte:
            from .services import traduire as svc_traduire
            res = svc_traduire(
                texte=texte,
                langue_cible=langue_cible,
                langue_source=langue_source,
                type_contenu=type_contenu,
                user=request.user,
            )
            resultat = res
            log_id = res.get('log_id')

    contexte = {
        'langues': langues,
        'resultat': resultat,
        'log_id': log_id,
        'types_contenu': TranslationLog.TYPE_CHOICES,
    }
    return render(request, 'traduction/traduire.html', contexte)


@login_required
def historique(request):
    """Historique des traductions de l'utilisateur connecté."""
    logs = TranslationLog.objects.filter(user=request.user).order_by('-cree_le')

    # Filtres
    langue_cible = request.GET.get('langue')
    if langue_cible:
        logs = logs.filter(langue_cible=langue_cible)

    type_contenu = request.GET.get('type')
    if type_contenu:
        logs = logs.filter(type_contenu=type_contenu)

    paginator = Paginator(logs, 20)
    page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'traduction/historique.html', {
        'page': page,
        'langues': settings.SUPPORTED_LANGUAGES,
        'types': TranslationLog.TYPE_CHOICES,
        'filtre_langue': langue_cible,
        'filtre_type': type_contenu,
    })


@login_required
@require_POST
def evaluer(request, pk):
    """Soumettre une évaluation / suggestion de correction."""
    log = get_object_or_404(TranslationLog, pk=pk, user=request.user)
    suggestion = request.POST.get('suggestion', '').strip()

    if suggestion:
        log.suggestion_correction = suggestion
        log.save(update_fields=['suggestion_correction'])
        messages.success(request, 'Votre suggestion a été enregistrée. Merci !')
    else:
        messages.warning(request, 'La suggestion ne peut pas être vide.')

    return redirect('traduction:historique')


@login_required
@require_POST
def api_traduire(request):
    """
    Endpoint HTMX/JSON pour traduction à la demande depuis n'importe quelle page.
    Utilisé par le bouton 'Traduire' sur les reçus, alertes, recommandations.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    texte = data.get('texte', '').strip()
    langue_cible = data.get('langue_cible', request.user.langue_preferee)
    langue_source = data.get('langue_source', 'fr')
    type_contenu = data.get('type_contenu', 'AUTRE')

    if not texte:
        return JsonResponse({'erreur': 'Texte vide'}, status=400)

    from .services import traduire as svc_traduire
    res = svc_traduire(
        texte=texte,
        langue_cible=langue_cible,
        langue_source=langue_source,
        type_contenu=type_contenu,
        user=request.user,
    )

    if request.htmx:
        return render(request, 'traduction/partials/resultat_inline.html', {
            'texte_traduit': res.get('texte_traduit'),
            'langue_cible': langue_cible,
            'langue_label': settings.SUPPORTED_LANGUAGES.get(langue_cible, {}).get('nom', langue_cible),
            'moteur': res.get('moteur'),
            'log_id': res.get('log_id'),
            'succes': res.get('succes'),
        })

    return JsonResponse({
        'texte_traduit': res.get('texte_traduit'),
        'moteur': res.get('moteur'),
        'temps_ms': res.get('temps_ms'),
        'log_id': res.get('log_id'),
        'succes': res.get('succes'),
    })
