"""
Grenier Commun — Service de Traduction IA
fr/en  : deep-translator (Google Translate, sans clé API)
fr/wo  : Meta NLLB-200 via Hugging Face Inference API
"""
import time
import hashlib
import logging
import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger('apps.traduction')

# ─── Codes de langue NLLB-200 ────────────────────────────────────────────────
NLLB_CODES = {
    'fr': 'fra_Latn',
    'en': 'eng_Latn',
    'wo': 'wol_Latn',
    'ar': 'arb_Arab',
}

# Langues supportées par Google Translate via deep-translator
GOOGLE_SUPPORTED = {'fr', 'en', 'ar'}


def _cache_key(texte: str, langue_source: str, langue_cible: str) -> str:
    contenu = f"{langue_source}:{langue_cible}:{texte}"
    return f"traduction:{hashlib.md5(contenu.encode()).hexdigest()}"


def traduire_google(texte: str, langue_source: str, langue_cible: str) -> dict:
    """
    Traduction fr ↔ en via deep-translator (Google Translate, sans clé API).
    """
    debut = time.time()
    try:
        from deep_translator import GoogleTranslator
        traducteur = GoogleTranslator(source=langue_source, target=langue_cible)
        texte_traduit = traducteur.translate(texte)
        temps_ms = int((time.time() - debut) * 1000)
        return {
            'texte': texte_traduit,
            'moteur': 'GOOGLE',
            'temps_ms': temps_ms,
            'succes': True,
        }
    except Exception as e:
        logger.error(f"Google Translate erreur: {e}")
        return {'succes': False, 'erreur': str(e), 'moteur': 'GOOGLE'}


def traduire_nllb(texte: str, langue_source: str, langue_cible: str) -> dict:
    """
    Traduction via Meta NLLB-200 sur Hugging Face Inference API.
    Utilisé principalement pour le Wolof (non supporté par Google Translate).
    """
    api_key = settings.HUGGINGFACE_API_KEY
    if not api_key:
        logger.warning("Clé Hugging Face non configurée — NLLB indisponible")
        return {'succes': False, 'erreur': 'Clé Hugging Face manquante dans .env (HUGGINGFACE_API_KEY)'}

    src = NLLB_CODES.get(langue_source)
    tgt = NLLB_CODES.get(langue_cible)
    if not src or not tgt:
        return {'succes': False, 'erreur': f'Langue non supportée: {langue_source} ou {langue_cible}'}

    url = f"https://api-inference.huggingface.co/models/{settings.NLLB_MODEL_NAME}"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "inputs": texte,
        "parameters": {
            "src_lang": src,
            "tgt_lang": tgt,
            "max_length": 1024,
        }
    }

    debut = time.time()
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        temps_ms = int((time.time() - debut) * 1000)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and data:
                texte_traduit = data[0].get('translation_text', '')
                return {
                    'texte': texte_traduit,
                    'moteur': 'NLLB200',
                    'temps_ms': temps_ms,
                    'succes': True,
                }
        logger.warning(f"NLLB API erreur {response.status_code}: {response.text[:200]}")
        return {'succes': False, 'erreur': f'API erreur {response.status_code}'}

    except requests.exceptions.Timeout:
        logger.warning("NLLB API timeout")
        return {'succes': False, 'erreur': 'Timeout Hugging Face (30s)'}
    except Exception as e:
        logger.error(f"NLLB erreur: {e}")
        return {'succes': False, 'erreur': str(e)}


def traduire(
    texte: str,
    langue_cible: str,
    langue_source: str = 'fr',
    type_contenu: str = 'AUTRE',
    user=None,
    utiliser_cache: bool = True,
) -> dict:
    """
    Fonction principale de traduction.

    Routage :
      - fr ↔ en  →  deep-translator (Google, sans clé)
      - fr ↔ wo  →  NLLB-200 (Hugging Face, nécessite HUGGINGFACE_API_KEY)

    Retourne : {texte_traduit, moteur, temps_ms, depuis_cache, log_id, succes}
    """
    if not texte or not texte.strip():
        return {'texte_traduit': texte, 'succes': True, 'depuis_cache': False, 'moteur': 'NOOP'}

    if langue_source == langue_cible:
        return {'texte_traduit': texte, 'succes': True, 'depuis_cache': True, 'moteur': 'NOOP'}

    # ── Cache ─────────────────────────────────────────────────────────────────
    cle = _cache_key(texte, langue_source, langue_cible)
    if utiliser_cache:
        try:
            cached = cache.get(cle)
            if cached:
                logger.debug(f"Cache hit: {langue_source}→{langue_cible}")
                return {**cached, 'depuis_cache': True}
        except Exception:
            pass  # LocMemCache en dev, ne bloque pas

    # ── Routage moteur ────────────────────────────────────────────────────────
    paire = {langue_source, langue_cible}
    if paire <= GOOGLE_SUPPORTED:
        # fr ↔ en : Google direct
        resultat = traduire_google(texte, langue_source, langue_cible)
    else:
        # wolof impliqué : NLLB uniquement
        resultat = traduire_nllb(texte, langue_source, langue_cible)

    if not resultat.get('succes'):
        msg_erreur = resultat.get('erreur', 'Erreur inconnue')
        logger.error(f"Traduction échouée ({langue_source}→{langue_cible}): {msg_erreur}")
        return {
            'texte_traduit': texte,
            'succes': False,
            'moteur': resultat.get('moteur', 'ECHEC'),
            'depuis_cache': False,
            'erreur': msg_erreur,
            'log_id': None,
        }

    # ── Mise en cache ─────────────────────────────────────────────────────────
    payload_cache = {
        'texte_traduit': resultat['texte'],
        'moteur': resultat['moteur'],
        'temps_ms': resultat.get('temps_ms', 0),
        'succes': True,
    }
    try:
        cache.set(cle, payload_cache, settings.TRANSLATION_CACHE_TIMEOUT)
    except Exception:
        pass

    # ── Log en base ───────────────────────────────────────────────────────────
    log_id = None
    try:
        from apps.core.models import TranslationLog
        log = TranslationLog.objects.create(
            user=user,
            type_contenu=type_contenu,
            texte_source=texte,
            texte_traduit=resultat['texte'],
            langue_source=langue_source,
            langue_cible=langue_cible,
            moteur=resultat['moteur'],
            temps_traitement_ms=resultat.get('temps_ms', 0),
            depuis_cache=False,
        )
        log_id = log.pk
    except Exception as e:
        logger.warning(f"Impossible de logger la traduction: {e}")

    return {
        'texte_traduit': resultat['texte'],
        'moteur': resultat['moteur'],
        'temps_ms': resultat.get('temps_ms', 0),
        'depuis_cache': False,
        'log_id': log_id,
        'succes': True,
    }


def traduire_sms(texte_fr: str, langue_cible: str, user=None) -> str:
    if langue_cible == 'fr' or not langue_cible:
        return texte_fr
    resultat = traduire(texte_fr, langue_cible, 'fr', 'SMS', user)
    return resultat.get('texte_traduit', texte_fr)


def traduire_contenu_metier(objet, langue_cible: str, user=None) -> dict:
    if langue_cible == 'fr':
        return {}
    champs_traduisibles = getattr(objet, 'CHAMPS_TRADUISIBLES', [])
    traductions = {}
    for champ in champs_traduisibles:
        texte = getattr(objet, champ, None)
        if texte:
            res = traduire(texte, langue_cible, 'fr', user=user)
            traductions[f'{champ}_{langue_cible}'] = res.get('texte_traduit', texte)
    return traductions
