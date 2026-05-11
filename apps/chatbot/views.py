"""
Grenier Commun — Vue Chatbot IA
Moteur : Claude (Anthropic) si ANTHROPIC_API_KEY configuré, sinon Mistral via HuggingFace.
"""
import logging
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST

from .tools import TOOL_DEFINITIONS, execute_tool

logger = logging.getLogger('apps.chatbot')


# ── Prompt système ────────────────────────────────────────────────────────────

def _build_system_prompt(user) -> str:
    role_map = {
        'AGRICULTEUR': 'un agriculteur sénégalais qui stocke ses récoltes et cherche à financer et vendre sa production',
        'GESTIONNAIRE': 'un gestionnaire de silo communautaire qui supervise les dépôts et les conditions de stockage',
        'ACHETEUR': 'un acheteur professionnel de céréales qui soumet des offres sur la place de marché',
        'IMF': 'un responsable de microfinance qui instruit et valide les dossiers de crédit warrantage',
        'ADMIN_GC': "l'administrateur de la plateforme Grenier Commun",
    }
    lang_map = {'fr': 'français', 'en': 'anglais', 'wo': 'wolof', 'ar': 'arabe'}

    role_desc = role_map.get(user.role, 'un utilisateur')
    langue = lang_map.get(getattr(user, 'langue_preferee', 'fr'), 'français')

    return f"""Tu es l'assistant IA de Grenier Commun, une plateforme de gestion post-récolte et de financement warrantage au Sénégal.

Tu parles avec {user.nom_complet}, qui est {role_desc}.
RÈGLE ABSOLUE : Réponds TOUJOURS en {langue}. Ne change jamais de langue sauf si l'utilisateur te le demande explicitement.

Grenier Commun permet aux agriculteurs sénégalais de :
- Stocker leurs céréales dans des silos sécurisés et obtenir un reçu numérique
- Obtenir un crédit warrantage (jusqu'à 70% de la valeur du stock) virés en 48h sur Wave ou Orange Money
- Vendre leurs céréales au meilleur moment grâce aux prix du marché et recommandations IA
- Communiquer dans leur langue (français, anglais, wolof, arabe)

INSTRUCTIONS :
- Sois concis, chaleureux et pratique — pas de réponses trop longues
- Formate les montants en FCFA avec des séparateurs (ex: 150 000 FCFA)
- Si tu ne peux pas répondre, oriente vers l'administrateur Grenier Commun
- Ne divulgue jamais les données d'autres utilisateurs
- Tu peux expliquer le fonctionnement du warrantage, des silos et de la plateforme"""


# ── Chargement du contexte pour Mistral ──────────────────────────────────────

def _load_user_context(user) -> str:
    """Pré-charge les données pertinentes selon le rôle pour les injecter dans le prompt Mistral."""
    parts = []

    def _run(tool_name, tool_input=None):
        try:
            return execute_tool(tool_name, tool_input or {}, user)
        except Exception as e:
            logger.warning(f"Contexte tool '{tool_name}' échoué: {e}")
            return None

    role = getattr(user, 'role', '')

    if role == 'AGRICULTEUR':
        for name, inp in [
            ('get_mes_stocks', {}),
            ('get_prix_marche', {}),
            ('get_mes_warrantages', {}),
            ('get_recommandations_vente', {}),
        ]:
            data = _run(name, inp)
            if data:
                parts.append(f"[{name}]\n{data}")

    elif role == 'GESTIONNAIRE':
        for name in ('get_infos_silo', 'get_alertes_silo', 'get_depots_silo'):
            data = _run(name)
            if data:
                parts.append(f"[{name}]\n{data}")

    elif role == 'IMF':
        data = _run('get_dossiers_imf')
        if data:
            parts.append(f"[get_dossiers_imf]\n{data}")
        prix = _run('get_prix_marche')
        if prix:
            parts.append(f"[get_prix_marche]\n{prix}")

    elif role == 'ACHETEUR':
        for name in ('get_offres_marche', 'get_prix_marche'):
            data = _run(name)
            if data:
                parts.append(f"[{name}]\n{data}")

    elif role == 'ADMIN_GC':
        data = _run('get_stats_admin')
        if data:
            parts.append(f"[get_stats_admin]\n{data}")

    else:
        prix = _run('get_prix_marche')
        if prix:
            parts.append(f"[get_prix_marche]\n{prix}")

    if not parts:
        return ""
    return "=== DONNÉES TEMPS RÉEL DE LA PLATEFORME ===\n" + "\n\n".join(parts)


# ── Appel Mistral (HuggingFace) ───────────────────────────────────────────────

def _call_mistral(history: list, user) -> str:
    api_key = getattr(settings, 'MISTRAL_API_KEY', '')
    if not api_key:
        return _msg_no_ia(user)

    import requests as req

    system = _build_system_prompt(user)
    context = _load_user_context(user)
    if context:
        system += f"\n\n{context}"

    messages = [{"role": "system", "content": system}]
    for msg in history[-12:]:
        content = msg.get("content", "")
        if isinstance(content, str) and content.strip():
            messages.append({"role": msg["role"], "content": content})

    try:
        response = req.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistral-small-latest",
                "messages": messages,
                "max_tokens": 800,
                "temperature": 0.6,
            },
            timeout=30,
        )
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Erreur API Mistral: {e}")
        return "Une erreur s'est produite avec le service IA. Veuillez réessayer."


# ── Appel Claude (Anthropic) ──────────────────────────────────────────────────

def _call_claude(history: list, user) -> str:
    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        return _call_mistral(history, user)

    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
    except ImportError:
        return "Le module 'anthropic' n'est pas installé. Exécutez : pip install anthropic"

    messages = list(history)
    system = _build_system_prompt(user)

    for _ in range(6):
        try:
            response = client.messages.create(
                model='claude-haiku-4-5-20251001',
                max_tokens=1024,
                system=system,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )
        except Exception as e:
            logger.error(f"Erreur API Claude: {e}")
            return "Une erreur s'est produite. Veuillez réessayer."

        if response.stop_reason == 'end_turn':
            for block in response.content:
                if hasattr(block, 'text'):
                    return block.text
            return "Je n'ai pas pu générer de réponse."

        if response.stop_reason == 'tool_use':
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type == 'tool_use':
                    result = execute_tool(block.name, block.input, user)
                    logger.debug(f"Tool '{block.name}' → {result[:200]}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": tool_results})
        else:
            break

    return "Je n'ai pas pu traiter votre demande. Veuillez reformuler."


def _msg_no_ia(user) -> str:
    lang = getattr(user, 'langue_preferee', 'fr')
    msgs = {
        'fr': "L'assistant IA n'est pas encore configuré. Contactez l'administrateur.",
        'en': "The AI assistant is not yet configured. Please contact the administrator.",
        'wo': "Assistant IA bi amul configuration bi. Contacter administrateur bi.",
        'ar': "المساعد الذكي غير مهيأ بعد. يرجى التواصل مع المسؤول.",
    }
    return msgs.get(lang, msgs['fr'])


# ── Vues ──────────────────────────────────────────────────────────────────────

@login_required
@require_POST
def chat_message(request):
    message = request.POST.get('message', '').strip()
    if not message:
        return HttpResponse('')

    history = request.session.get('chatbot_history', [])
    history.append({"role": "user", "content": message})

    response_text = _call_claude(history, request.user)

    history.append({"role": "assistant", "content": response_text})
    request.session['chatbot_history'] = history[-20:]
    request.session.modified = True

    return render(request, 'chatbot/partials/messages.html', {
        'user_message': message,
        'assistant_message': response_text,
    })


@login_required
@require_POST
def clear_history(request):
    request.session['chatbot_history'] = []
    request.session.modified = True
    return HttpResponse(status=204)
