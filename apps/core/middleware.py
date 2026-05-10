"""
Grenier Commun — AutoTranslateMiddleware

Intercepte chaque réponse HTML et traduit tout le texte visible vers la
langue active Django (en, ar, wo).  Fonctionne comme un filet de sécurité :
les chaînes déjà traduites par {% trans %} ne sont pas re-traduites (source='auto').

Moteurs :
  fr ↔ en / ar  →  Google Translate  (deep-translator, sans clé API)
  fr ↔ wo       →  NLLB-200          (Hugging Face — ignoré si pas de clé)

Cache :
  - Par chaîne   : clé = hash(texte+lang)  — TTL 24 h
  - Par page     : clé = hash(url+lang)    — TTL 30 min

Dépendances : beautifulsoup4  (pip install beautifulsoup4)
"""

import re
import hashlib
import logging

from django.utils.translation import get_language
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('apps.core.middleware')

# Balises dont le contenu textuel ne doit JAMAIS être traduit
_SKIP_TAGS = frozenset({
    'script', 'style', 'noscript', 'code', 'pre',
    'head', 'title', 'meta', 'link',
})

# Chaînes purement numériques / symboliques → on ne traduit pas
_SKIP_RE = re.compile(
    r'^[\d\s.,;:!?()\[\]{}<>_+=\-*/\\@#$^&~|°€₣£¥₹%→←↔×÷±∞√]+$'
)


# ── Clés de cache ─────────────────────────────────────────────────────────────

def _str_key(text: str, lang: str) -> str:
    h = hashlib.md5(text.encode()).hexdigest()[:12]
    return f'str_tr:{lang}:{h}'


def _page_key(path: str, lang: str) -> str:
    h = hashlib.md5(path.encode()).hexdigest()[:12]
    return f'page_tr:{lang}:{h}'


# ── Filtrage ──────────────────────────────────────────────────────────────────

def _worth_translating(text: str) -> bool:
    t = text.strip()
    if len(t) < 2:
        return False
    if _SKIP_RE.match(t):
        return False
    return True


# ── Appels API ────────────────────────────────────────────────────────────────

def _google_batch(texts: list, target_lang: str) -> dict:
    """
    Traduit une liste de chaînes via Google Translate (deep-translator).
    Envoie tout en une seule requête séparée par des sauts de ligne.
    Si le découpage échoue, repasse en mode individuel.
    """
    result = {}
    if not texts:
        return result

    try:
        from deep_translator import GoogleTranslator
        translator = GoogleTranslator(source='auto', target=target_lang)
        joined = '\n'.join(texts)
        raw = translator.translate(joined) or joined
        parts = raw.split('\n')

        if len(parts) == len(texts):
            for orig, trans in zip(texts, parts):
                result[orig] = trans.strip() or orig
            return result
        # Mauvais découpage → individuel
    except Exception as exc:
        logger.debug('Batch Google Translate échoué : %s', exc)

    # Mode individuel (fallback)
    try:
        from deep_translator import GoogleTranslator
        for text in texts:
            try:
                trans = GoogleTranslator(source='auto', target=target_lang).translate(text)
                result[text] = trans or text
            except Exception:
                result[text] = text
    except ImportError:
        for text in texts:
            result[text] = text

    return result


def _resolve_translations(texts: list, target_lang: str) -> dict:
    """
    Pour chaque texte : cherche en cache, appelle l'API pour le reste.
    Découpe en sous-lots de ~3 500 caractères max pour rester sous la limite.
    """
    result = {}
    need_api = []

    for text in texts:
        cached = cache.get(_str_key(text, target_lang))
        if cached is not None:
            result[text] = cached
        else:
            need_api.append(text)

    if not need_api:
        return result

    # Découpe en sous-lots
    batches, batch, blen = [], [], 0
    for text in need_api:
        if blen + len(text) > 3500 and batch:
            batches.append(batch)
            batch, blen = [], 0
        batch.append(text)
        blen += len(text) + 1
    if batch:
        batches.append(batch)

    for sub in batches:
        translated = _google_batch(sub, target_lang)
        for orig, trans in translated.items():
            result[orig] = trans
            try:
                cache.set(_str_key(orig, target_lang), trans, 86400)  # 24 h
            except Exception:
                pass

    return result


# ── Traduction HTML ───────────────────────────────────────────────────────────

def _translate_html(html: str, target_lang: str) -> str:
    try:
        from bs4 import BeautifulSoup, NavigableString, Comment
    except ImportError:
        logger.warning('beautifulsoup4 manquant — AutoTranslateMiddleware inactif')
        return html

    soup = BeautifulSoup(html, 'html.parser')

    # Collecte des nœuds texte traductibles
    translatable = []
    for node in soup.find_all(string=True):
        # UNIQUEMENT les vrais nœuds texte — exclut Comment, CData, Script,
        # Stylesheet, Doctype, etc. qui sont tous des sous-classes de NavigableString
        if type(node) is not NavigableString:
            continue
        # Ignorer si un ancêtre est une balise à exclure OU porte data-notranslate
        skip = any(
            getattr(anc, 'name', None) in _SKIP_TAGS
            or ('data-notranslate' in getattr(anc, 'attrs', {}))
            for anc in node.parents
        )
        if skip:
            continue
        if _worth_translating(str(node).strip()):
            translatable.append(node)

    if not translatable:
        return str(soup)

    # Dédoublonnage
    unique = list({str(n).strip() for n in translatable})
    translations = _resolve_translations(unique, target_lang)

    # Application des traductions
    for node in translatable:
        raw = str(node)
        stripped = raw.strip()
        trans = translations.get(stripped)
        if trans and trans != stripped:
            lead  = raw[:len(raw) - len(raw.lstrip())]
            trail = raw[len(raw.rstrip()):]
            node.replace_with(NavigableString(lead + trans + trail))

    return str(soup)


# ── Middleware ────────────────────────────────────────────────────────────────

class AutoTranslateMiddleware:
    """
    Post-traite les réponses HTML pour traduire automatiquement tout le texte
    visible dans la langue active Django.

    Placement dans MIDDLEWARE : après LocaleMiddleware (dernière position).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        lang = get_language()

        # Passe-droit : français (langue de base) ou langue non définie
        if not lang or lang.startswith('fr'):
            return response

        # Wolof sans clé Hugging Face → pas de traduction possible
        if lang == 'wo' and not getattr(settings, 'HUGGINGFACE_API_KEY', ''):
            return response

        # Uniquement les réponses HTML 200 complètes
        if response.status_code != 200:
            return response
        if 'text/html' not in response.get('Content-Type', ''):
            return response
        if not hasattr(response, 'content'):
            return response
        # Ignorer les requêtes HTMX (réponses partielles — pas de <html>)
        if request.headers.get('HX-Request'):
            return response
        # Ignorer si ce n'est pas une page HTML complète
        raw_start = response.content[:200].decode('utf-8', errors='ignore').lower()
        if '<!doctype' not in raw_start and '<html' not in raw_start:
            return response

        # Cache page entière
        pkey = _page_key(request.get_full_path(), lang)
        cached_page = cache.get(pkey)
        if cached_page:
            response.content = cached_page
            if 'Content-Length' in response:
                response['Content-Length'] = len(cached_page)
            return response

        # Traduction
        try:
            html = response.content.decode('utf-8')
            translated = _translate_html(html, lang)
            encoded = translated.encode('utf-8')
            try:
                cache.set(pkey, encoded, 1800)   # 30 min
            except Exception:
                pass
            response.content = encoded
            if 'Content-Length' in response:
                response['Content-Length'] = len(encoded)
        except Exception as exc:
            logger.error('AutoTranslateMiddleware erreur : %s', exc, exc_info=True)

        return response
