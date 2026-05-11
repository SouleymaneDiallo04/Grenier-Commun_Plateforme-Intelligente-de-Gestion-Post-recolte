"""
Grenier Commun — Outils du chatbot IA
Chaque outil interroge les données réelles Django et retourne un dict sérialisable.
"""
import json
from decimal import Decimal


# ── Définitions des outils pour l'API Claude ─────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "get_mes_stocks",
        "description": "Récupère les dépôts et stocks actifs de l'agriculteur connecté : quantités, denrées, silos, valeurs estimées et montants warrantables.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_prix_marche",
        "description": "Récupère les prix actuels du marché par denrée et/ou région au Sénégal (FCFA/kg).",
        "input_schema": {
            "type": "object",
            "properties": {
                "denree": {"type": "string", "description": "Nom de la denrée (ex: mil, maïs, arachide). Optionnel."},
                "region": {"type": "string", "description": "Région du Sénégal. Optionnel."},
            },
        },
    },
    {
        "name": "get_mes_warrantages",
        "description": "Récupère les demandes de crédit warrantage de l'agriculteur avec leurs statuts, montants et échéances.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_notifications",
        "description": "Récupère les notifications récentes de l'utilisateur connecté (lues et non lues).",
        "input_schema": {
            "type": "object",
            "properties": {
                "non_lues_seulement": {"type": "boolean", "description": "Si true, retourne uniquement les non lues. Défaut: false."},
            },
        },
    },
    {
        "name": "get_recommandations_vente",
        "description": "Récupère les recommandations IA validées pour savoir quand vendre une denrée (VENDRE, ATTENDRE, PARTIEL) avec prévisions de prix.",
        "input_schema": {
            "type": "object",
            "properties": {
                "denree": {"type": "string", "description": "Filtrer par denrée. Optionnel."},
            },
        },
    },
    {
        "name": "calculer_credit_warrantage",
        "description": "Calcule le montant de crédit disponible, les intérêts et le coût total d'un warrantage.",
        "input_schema": {
            "type": "object",
            "properties": {
                "valeur_stock_fcfa": {"type": "number", "description": "Valeur du stock en FCFA."},
                "taux_financement_pct": {"type": "number", "description": "Taux de financement en % (défaut: 70)."},
                "taux_interet_mensuel_pct": {"type": "number", "description": "Taux d'intérêt mensuel en % (défaut: 2.5)."},
                "duree_mois": {"type": "integer", "description": "Durée en mois (défaut: 3)."},
            },
            "required": ["valeur_stock_fcfa"],
        },
    },
    {
        "name": "get_infos_silo",
        "description": "Récupère les informations et statistiques du silo géré par le gestionnaire connecté : capacité, remplissage, température, humidité, santé.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_alertes_silo",
        "description": "Récupère les alertes actives du silo (température, humidité, rongeurs, capacité) avec leur niveau d'urgence.",
        "input_schema": {
            "type": "object",
            "properties": {
                "non_acquittees_seulement": {"type": "boolean", "description": "Si true, retourne uniquement les alertes non acquittées. Défaut: true."},
            },
        },
    },
    {
        "name": "get_depots_silo",
        "description": "Récupère la liste des dépôts actifs dans le silo du gestionnaire connecté.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_dossiers_imf",
        "description": "Récupère les dossiers de warrantage en attente de décision pour l'IMF connectée, avec scores crédit et montants.",
        "input_schema": {
            "type": "object",
            "properties": {
                "statut": {"type": "string", "description": "Filtrer par statut (SOUMIS, EN_INSTRUCTION, APPROUVE, REFUSE). Optionnel."},
            },
        },
    },
    {
        "name": "get_stats_admin",
        "description": "Récupère les statistiques globales de la plateforme : utilisateurs, stocks, transactions, warrantages, revenus.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_mes_transactions",
        "description": "Récupère l'historique des ventes/transactions de l'utilisateur connecté.",
        "input_schema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "description": "Nombre de transactions à retourner. Défaut: 5."},
            },
        },
    },
    {
        "name": "get_offres_marche",
        "description": "Récupère les offres d'achat disponibles sur la place de marché.",
        "input_schema": {
            "type": "object",
            "properties": {
                "denree": {"type": "string", "description": "Filtrer par denrée. Optionnel."},
            },
        },
    },
    {
        "name": "get_profil",
        "description": "Récupère le profil complet de l'utilisateur connecté : rôle, langue, score crédit (agriculteur), superficie, etc.",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "traduire_texte",
        "description": "Traduit un texte dans la langue demandée (fr, en, ar, wo) en utilisant le service de traduction de la plateforme.",
        "input_schema": {
            "type": "object",
            "properties": {
                "texte": {"type": "string", "description": "Texte à traduire."},
                "langue_cible": {"type": "string", "enum": ["fr", "en", "ar", "wo"], "description": "Langue cible."},
                "langue_source": {"type": "string", "enum": ["fr", "en", "ar", "wo"], "description": "Langue source. Défaut: fr."},
            },
            "required": ["texte", "langue_cible"],
        },
    },
]


# ── Dispatcher ────────────────────────────────────────────────────────────────

def execute_tool(tool_name: str, tool_input: dict, user) -> str:
    handlers = {
        'get_mes_stocks': _get_mes_stocks,
        'get_prix_marche': _get_prix_marche,
        'get_mes_warrantages': _get_mes_warrantages,
        'get_notifications': _get_notifications,
        'get_recommandations_vente': _get_recommandations_vente,
        'calculer_credit_warrantage': _calculer_credit_warrantage,
        'get_infos_silo': _get_infos_silo,
        'get_alertes_silo': _get_alertes_silo,
        'get_depots_silo': _get_depots_silo,
        'get_dossiers_imf': _get_dossiers_imf,
        'get_stats_admin': _get_stats_admin,
        'get_mes_transactions': _get_mes_transactions,
        'get_offres_marche': _get_offres_marche,
        'get_profil': _get_profil,
        'traduire_texte': _traduire_texte,
    }
    handler = handlers.get(tool_name)
    if not handler:
        return json.dumps({'erreur': f'Outil inconnu: {tool_name}'})
    try:
        return json.dumps(handler(user, **tool_input), ensure_ascii=False, default=str)
    except Exception as e:
        return json.dumps({'erreur': str(e)}, ensure_ascii=False)


# ── Implémentations ───────────────────────────────────────────────────────────

def _get_mes_stocks(user, **kwargs):
    from apps.silos.models import Depot
    depots = Depot.objects.filter(
        agriculteur=user,
        statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
    ).select_related('silo', 'denree', 'silo__commune')

    if not depots.exists():
        return {'stocks': [], 'message': 'Aucun stock actif.'}

    result = []
    for d in depots:
        result.append({
            'recu': d.numero_recu,
            'denree': d.denree.nom,
            'silo': d.silo.nom,
            'commune': d.silo.commune.nom,
            'quantite_initiale_kg': float(d.quantite_initiale_kg),
            'quantite_disponible_kg': float(d.quantite_disponible_kg),
            'statut': d.get_statut_display(),
            'date_depot': d.date_depot.strftime('%d/%m/%Y'),
            'valeur_estimee_fcfa': d.valeur_estimee_fcfa,
            'montant_warrantable_fcfa': d.montant_warrantable_fcfa,
        })
    return {'stocks': result, 'total': len(result)}


def _get_prix_marche(user, denree=None, region=None, **kwargs):
    from apps.core.models import PrixMarche
    qs = PrixMarche.objects.select_related('denree').order_by('-date_maj')
    if denree:
        qs = qs.filter(denree__nom__icontains=denree)
    if region:
        qs = qs.filter(region__icontains=region)
    qs = qs[:15]

    if not qs.exists():
        return {'prix': [], 'message': 'Aucun prix disponible pour ces critères.'}

    return {
        'prix': [
            {
                'denree': p.denree.nom,
                'region': p.region,
                'prix_kg_fcfa': float(p.prix_kg_fcfa),
                'prix_min_fcfa': float(p.prix_min_fcfa) if p.prix_min_fcfa else None,
                'prix_max_fcfa': float(p.prix_max_fcfa) if p.prix_max_fcfa else None,
                'source': p.source,
                'date_maj': p.date_maj.strftime('%d/%m/%Y'),
            }
            for p in qs
        ]
    }


def _get_mes_warrantages(user, **kwargs):
    from apps.core.models import WarrantageCredit
    warrantages = WarrantageCredit.objects.filter(
        agriculteur=user
    ).select_related('depot__denree', 'imf').order_by('-date_demande')

    if not warrantages.exists():
        return {'warrantages': [], 'message': 'Aucune demande de warrantage.'}

    return {
        'warrantages': [
            {
                'id': w.pk,
                'denree': w.depot.denree.nom,
                'statut': w.get_statut_display(),
                'montant_demande_fcfa': float(w.montant_demande_fcfa),
                'montant_accorde_fcfa': float(w.montant_accorde_fcfa) if w.montant_accorde_fcfa else None,
                'taux_interet_mensuel': float(w.taux_interet_mensuel) if w.taux_interet_mensuel else None,
                'duree_mois': w.duree_mois,
                'imf': w.imf.sigle or w.imf.nom if w.imf else None,
                'date_demande': w.date_demande.strftime('%d/%m/%Y'),
                'date_echeance': w.date_echeance.strftime('%d/%m/%Y') if w.date_echeance else None,
                'motif_refus': w.motif_refus if w.motif_refus else None,
            }
            for w in warrantages
        ]
    }


def _get_notifications(user, non_lues_seulement=False, **kwargs):
    from apps.core.models import Notification
    qs = Notification.objects.filter(
        destinataire=user, canal='APP'
    ).order_by('-cree_le')[:10]

    if non_lues_seulement:
        qs = qs.filter(statut__in=['EN_ATTENTE', 'ENVOYE'])

    if not qs.exists():
        return {'notifications': [], 'message': 'Aucune notification.'}

    return {
        'notifications': [
            {
                'titre': n.titre,
                'contenu': n.contenu,
                'statut': n.get_statut_display(),
                'date': n.cree_le.strftime('%d/%m/%Y %H:%M'),
            }
            for n in qs
        ]
    }


def _get_recommandations_vente(user, denree=None, **kwargs):
    from apps.core.models import RecommandationVente
    qs = RecommandationVente.objects.filter(
        validee_par_admin=True
    ).select_related('denree').order_by('-cree_le')

    if denree:
        qs = qs.filter(denree__nom__icontains=denree)
    qs = qs[:8]

    if not qs.exists():
        return {'recommandations': [], 'message': 'Aucune recommandation disponible.'}

    lang = getattr(user, 'langue_preferee', 'fr')
    return {
        'recommandations': [
            {
                'denree': r.denree.nom,
                'action': r.get_action_recommandee_display(),
                'message': r.message_en if lang == 'en' and r.message_en else
                           r.message_wo if lang == 'wo' and r.message_wo else r.message_fr,
                'prix_actuel_fcfa': float(r.prix_actuel_fcfa) if r.prix_actuel_fcfa else None,
                'prix_prevu_4sem_fcfa': float(r.prix_prevu_4sem_fcfa) if r.prix_prevu_4sem_fcfa else None,
                'prix_prevu_8sem_fcfa': float(r.prix_prevu_8sem_fcfa) if r.prix_prevu_8sem_fcfa else None,
                'valide_jusqu_au': r.valide_jusqu_au.strftime('%d/%m/%Y') if r.valide_jusqu_au else None,
            }
            for r in qs
        ]
    }


def _calculer_credit_warrantage(user, valeur_stock_fcfa, taux_financement_pct=70,
                                 taux_interet_mensuel_pct=2.5, duree_mois=3, **kwargs):
    montant_credit = valeur_stock_fcfa * (taux_financement_pct / 100)
    interets_total = montant_credit * (taux_interet_mensuel_pct / 100) * duree_mois
    cout_total = montant_credit + interets_total
    remboursement_mensuel = cout_total / duree_mois if duree_mois > 0 else cout_total

    return {
        'valeur_stock_fcfa': round(valeur_stock_fcfa),
        'taux_financement_pct': taux_financement_pct,
        'montant_credit_fcfa': round(montant_credit),
        'taux_interet_mensuel_pct': taux_interet_mensuel_pct,
        'duree_mois': duree_mois,
        'interets_total_fcfa': round(interets_total),
        'cout_total_fcfa': round(cout_total),
        'remboursement_mensuel_fcfa': round(remboursement_mensuel),
    }


def _get_infos_silo(user, **kwargs):
    from apps.silos.models import Silo
    try:
        silo = Silo.objects.select_related('commune').get(gestionnaire=user)
    except Silo.DoesNotExist:
        return {'erreur': 'Aucun silo assigné à cet utilisateur.'}

    return {
        'nom': silo.nom,
        'code': silo.code,
        'commune': silo.commune.nom,
        'region': silo.commune.region,
        'capacite_kg': silo.capacite_kg,
        'stock_actuel_kg': silo.stock_actuel_kg,
        'capacite_disponible_kg': silo.capacite_disponible_kg,
        'taux_remplissage_pct': silo.taux_remplissage,
        'temperature_celsius': float(silo.temperature_celsius) if silo.temperature_celsius else None,
        'humidite_pourcent': float(silo.humidite_pourcent) if silo.humidite_pourcent else None,
        'sante': silo.get_sante_display(),
        'statut': silo.get_statut_display(),
        'nb_depots_actifs': silo.nb_depots_actifs,
    }


def _get_alertes_silo(user, non_acquittees_seulement=True, **kwargs):
    from apps.silos.models import Silo, AlerteSilo
    try:
        silo = Silo.objects.get(gestionnaire=user)
    except Silo.DoesNotExist:
        return {'erreur': 'Aucun silo assigné.'}

    qs = AlerteSilo.objects.filter(silo=silo).order_by('-cree_le')
    if non_acquittees_seulement:
        qs = qs.filter(est_acquittee=False)
    qs = qs[:10]

    if not qs.exists():
        msg = 'Aucune alerte active.' if non_acquittees_seulement else 'Aucune alerte.'
        return {'alertes': [], 'message': msg}

    return {
        'alertes': [
            {
                'type': a.get_type_alerte_display(),
                'niveau': a.get_niveau_display(),
                'message': a.message,
                'valeur_mesuree': a.valeur_mesuree,
                'valeur_seuil': a.valeur_seuil,
                'date': a.cree_le.strftime('%d/%m/%Y %H:%M'),
                'acquittee': a.est_acquittee,
            }
            for a in qs
        ]
    }


def _get_depots_silo(user, **kwargs):
    from apps.silos.models import Silo, Depot
    try:
        silo = Silo.objects.get(gestionnaire=user)
    except Silo.DoesNotExist:
        return {'erreur': 'Aucun silo assigné.'}

    depots = Depot.objects.filter(
        silo=silo, statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
    ).select_related('agriculteur', 'denree').order_by('-date_depot')[:20]

    if not depots.exists():
        return {'depots': [], 'message': 'Aucun dépôt actif dans ce silo.'}

    return {
        'depots': [
            {
                'recu': d.numero_recu,
                'agriculteur': d.agriculteur.nom_complet,
                'denree': d.denree.nom,
                'quantite_disponible_kg': float(d.quantite_disponible_kg),
                'statut': d.get_statut_display(),
                'date_depot': d.date_depot.strftime('%d/%m/%Y'),
            }
            for d in depots
        ],
        'total': depots.count(),
    }


def _get_dossiers_imf(user, statut=None, **kwargs):
    from apps.core.models import WarrantageCredit, IMFPartenaire
    try:
        imf = IMFPartenaire.objects.get(contact_email=user.email)
    except IMFPartenaire.DoesNotExist:
        return {'erreur': 'Aucune IMF associée à ce compte.'}

    qs = WarrantageCredit.objects.filter(imf=imf).select_related(
        'agriculteur', 'depot__denree'
    ).order_by('-date_demande')

    if statut:
        qs = qs.filter(statut=statut.upper())
    else:
        qs = qs.filter(statut__in=['SOUMIS', 'EN_INSTRUCTION'])

    qs = qs[:15]

    if not qs.exists():
        return {'dossiers': [], 'message': 'Aucun dossier en attente.'}

    return {
        'dossiers': [
            {
                'id': w.pk,
                'agriculteur': w.agriculteur.nom_complet,
                'denree': w.depot.denree.nom,
                'montant_demande_fcfa': float(w.montant_demande_fcfa),
                'score_credit': w.score_credit_snapshot,
                'statut': w.get_statut_display(),
                'date_demande': w.date_demande.strftime('%d/%m/%Y'),
            }
            for w in qs
        ]
    }


def _get_stats_admin(user, **kwargs):
    if not user.est_admin_gc:
        return {'erreur': 'Accès réservé aux administrateurs.'}

    from apps.accounts.models import User as UserModel
    from apps.silos.models import Depot, Silo
    from apps.core.models import WarrantageCredit, Transaction
    from django.db.models import Sum

    total_users = UserModel.objects.filter(is_active=True).count()
    total_agriculteurs = UserModel.objects.filter(role='AGRICULTEUR', is_active=True).count()
    total_depots_actifs = Depot.objects.filter(statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']).count()
    stock_total = Depot.objects.filter(
        statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']
    ).aggregate(total=Sum('quantite_disponible_kg'))['total'] or 0
    warrantages_actifs = WarrantageCredit.objects.filter(
        statut__in=['APPROUVE', 'VIRE']
    ).aggregate(total=Sum('montant_accorde_fcfa'))['total'] or 0
    nb_silos = Silo.objects.filter(statut='ACTIF').count()
    commissions = Transaction.objects.aggregate(
        total=Sum('commission_gc_fcfa')
    )['total'] or 0

    return {
        'utilisateurs_actifs': total_users,
        'agriculteurs': total_agriculteurs,
        'depots_actifs': total_depots_actifs,
        'stock_total_kg': float(stock_total),
        'warrantages_actifs_fcfa': float(warrantages_actifs),
        'silos_actifs': nb_silos,
        'commissions_totales_fcfa': float(commissions),
    }


def _get_mes_transactions(user, limit=5, **kwargs):
    from apps.core.models import Transaction, OffreAchat
    if user.est_acheteur:
        qs = Transaction.objects.filter(
            offre__acheteur=user
        ).select_related('offre__denree').order_by('-date_transaction')[:limit]
        if not qs.exists():
            return {'transactions': [], 'message': 'Aucune transaction.'}
        return {
            'transactions': [
                {
                    'denree': t.offre.denree.nom,
                    'montant_total_fcfa': float(t.montant_total_fcfa),
                    'date': t.date_transaction.strftime('%d/%m/%Y'),
                }
                for t in qs
            ]
        }

    # Agriculteur — transactions via retraits/ventes
    from apps.silos.models import Retrait
    retraits = Retrait.objects.filter(
        depot__agriculteur=user,
        type_retrait='VENTE'
    ).select_related('depot__denree').order_by('-date_retrait')[:limit]

    if not retraits.exists():
        return {'transactions': [], 'message': 'Aucune vente enregistrée.'}

    return {
        'transactions': [
            {
                'denree': r.depot.denree.nom,
                'quantite_kg': float(r.quantite_kg),
                'prix_vente_fcfa_kg': float(r.prix_vente_fcfa) if r.prix_vente_fcfa else None,
                'total_fcfa': float(r.quantite_kg * r.prix_vente_fcfa) if r.prix_vente_fcfa else None,
                'date': r.date_retrait.strftime('%d/%m/%Y'),
            }
            for r in retraits
        ]
    }


def _get_offres_marche(user, denree=None, **kwargs):
    from apps.core.models import OffreAchat
    qs = OffreAchat.objects.filter(
        statut__in=['SOUMISE', 'EN_NEGOCIATION']
    ).select_related('denree', 'acheteur').order_by('-date_offre')

    if denree:
        qs = qs.filter(denree__nom__icontains=denree)
    qs = qs[:10]

    if not qs.exists():
        return {'offres': [], 'message': 'Aucune offre disponible.'}

    return {
        'offres': [
            {
                'id': o.pk,
                'denree': o.denree.nom,
                'quantite_kg': float(o.quantite_kg),
                'prix_propose_fcfa_kg': float(o.prix_propose_fcfa),
                'region': o.region_preferee or 'Toutes régions',
                'delai_jours': o.delai_souhaite_jours,
                'statut': o.get_statut_display(),
                'date_offre': o.date_offre.strftime('%d/%m/%Y'),
            }
            for o in qs
        ]
    }


def _get_profil(user, **kwargs):
    profil = {
        'nom_complet': user.nom_complet,
        'email': user.email,
        'role': user.get_role_display(),
        'langue_preferee': user.get_langue_preferee_display(),
        'pays': user.pays,
        'region': user.region,
        'verifie': user.is_verified,
        'membre_depuis': user.date_joined.strftime('%B %Y'),
    }

    if user.est_agriculteur:
        try:
            pa = user.profil_agriculteur
            profil.update({
                'village': pa.village,
                'superficie_ha': float(pa.superficie_ha) if pa.superficie_ha else None,
                'score_credit': pa.score_credit,
                'categorie_risque': pa.categorie_risque,
                'numero_agriculteur': pa.numero_agriculteur,
            })
        except Exception:
            pass

    return profil


def _traduire_texte(user, texte, langue_cible, langue_source='fr', **kwargs):
    try:
        from apps.traduction.services import traduire
        resultat = traduire(
            texte=texte,
            langue_cible=langue_cible,
            langue_source=langue_source,
            type_contenu='AUTRE',
            user=user,
        )
        if resultat.get('succes'):
            return {
                'texte_original': texte,
                'texte_traduit': resultat['texte_traduit'],
                'moteur': resultat.get('moteur'),
                'depuis_cache': resultat.get('depuis_cache', False),
            }
        return {'erreur': resultat.get('erreur', 'Traduction échouée.')}
    except Exception as e:
        return {'erreur': str(e)}
