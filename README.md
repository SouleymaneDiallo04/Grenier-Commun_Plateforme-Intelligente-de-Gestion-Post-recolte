# 🌾 Grenier Commun
### *La plateforme qui donne aux agriculteurs sénégalais le pouvoir de vendre au bon prix*

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Redis-Cache-DC382D?style=for-the-badge&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/Meta_NLLB--200-IA_Wolof-0082C9?style=for-the-badge&logo=meta&logoColor=white"/>
  <img src="https://img.shields.io/badge/Langues-FR_·_EN_·_AR_·_WO-1A6B3A?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Déploiement-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white"/>
</p>

---

## Le problème : trois injustices qui se répètent chaque saison

Au Sénégal, l'agriculture emploie plus de **60 % de la population active**. Pourtant, saison après saison, des millions de petits agriculteurs subissent les mêmes trois injustices — non pas par manque de travail, mais par manque d'infrastructure, de financement et d'information.

### 1. La trappe du vendeur contraint

Dès la fin de la récolte — entre octobre et décembre — tous les producteurs vendent en même temps. Le marché est saturé, les prix s'effondrent. L'arachide tombe à **150 FCFA/kg** alors qu'elle vaudra **300 à 350 FCFA/kg** quatre mois plus tard. L'agriculteur ne vend pas parce que c'est le bon moment. Il vend parce qu'il n'a nulle part où stocker, et parce qu'il a besoin de cash immédiatement pour rembourser ses dettes, payer la scolarité de ses enfants, acheter des intrants pour la prochaine saison.

Il vend contraint. Il perd la moitié de la valeur de sa récolte. Chaque année.

### 2. Les pertes post-récolte : une catastrophe silencieuse

Faute d'installations de stockage adaptées, **30 à 40 % de la production agricole sénégalaise** disparaît après la récolte. Chaleur excessive, humidité, rongeurs, insectes — des tonnes de céréales et de légumineuses sont détruites chaque saison dans des greniers traditionnels inadaptés. Ces pertes représentent des centaines de milliards de FCFA évaporés, directement dans les mains les plus vulnérables de la chaîne.

### 3. L'exclusion financière structurelle

Le petit agriculteur n'a pas accès au crédit bancaire classique. Il n'a pas de garanties formelles, pas d'historique financier traçable, pas de dossier. Le warrantage agricole — système qui permet d'emprunter en utilisant son stock comme garantie — existe comme solution théorique depuis des décennies. Mais dans la pratique, il reste manuel, lent, inaccessible aux plus éloignés des centres urbains. Résultat : l'agriculteur ne peut pas financer la saison suivante, ne peut pas investir, ne peut pas grandir. Il reste au même endroit.

---

## La solution : Grenier Commun

**Grenier Commun** est la première plateforme intégrée d'Afrique de l'Ouest qui résout ces trois problèmes simultanément, dans un seul produit numérique.

> *Stocker mieux. Financer plus vite. Vendre au bon moment.*

La plateforme repose sur un réseau de **silos physiques connectés** déployés dans les communes rurales sénégalaises, pilotés par une interface web multi-acteurs accessible en **quatre langues** — dont le Wolof, la langue nationale parlée par plus de 80 % des Sénégalais.

Ce n'est pas une application de plus. C'est une **infrastructure digitale agricole** : le système nerveux numérique qui manquait entre le champ, le silo, la banque et le marché.

---

![Page Visiteur](screenshoots/visitor.png)

## Ce qui rend ce projet unique

Plusieurs acteurs opèrent dans l'écosystème agricole sénégalais. Aucun ne combine ces trois dimensions dans un seul produit intégré :

| Acteur existant | Ce qu'il fait | Ce qui manque |
|---|---|---|
| Silos traditionnels | Stockage physique | Zéro numérique, zéro financement, zéro marché |
| Institutions de microfinance | Crédit warrantage manuel | Processus lent, pas de traçabilité du stock |
| Plateformes de prix (OMA, ESOKO) | Information sur les marchés | Pas de stockage, pas de financement |
| Coopératives agricoles | Organisation des producteurs | Pas de technologie, pas de financement intégré |
| **Grenier Commun** | **Stockage + Financement + Marché + IA + 4 langues** | **C'est la combinaison qui n'existait pas** |

---

## Architecture de la solution

```
AGRICULTEUR ──→ SILO PHYSIQUE CONNECTÉ ──→ PLATEFORME WEB ──→ IMF PARTENAIRE
                      │                          │
                      │                          ├──→ ACHETEUR
                      │                          │
                      └──────────────────────────└──→ ADMIN GRENIER COMMUN
```

La plateforme s'organise autour de **cinq espaces utilisateurs** avec des rôles, droits et interfaces distincts.

---

## Les cinq espaces utilisateurs

### 🌾 L'Agriculteur — le cœur du projet

L'agriculteur est l'utilisateur central. Son interface est conçue pour quelqu'un qui n'est pas forcément à l'aise avec le numérique : indicateurs visuels vert/orange/rouge plutôt que chiffres bruts, navigation en 3 clics maximum, disponible en français et en Wolof.

**Ce qu'il peut faire :**
- Consulter son stock en temps réel avec son état de santé (vert / orange / rouge)
- Télécharger son reçu de dépôt PDF — document légalement traçable
- Suivre les prix du marché hebdomadaires pour ses denrées
- Recevoir une recommandation de vente générée par l'IA : *"Attendez encore 4 semaines"* ou *"C'est le bon moment pour vendre"*
- Faire une demande de crédit warrantage directement depuis la plateforme, sans déplacement
- Suivre le statut de son crédit en temps réel : soumis → instruit → approuvé → viré
- Recevoir des notifications SMS traduits dans sa langue préférée
- Indiquer son intention de vendre et recevoir les offres des acheteurs

---

### 🏛️ Le Gestionnaire de Silo — le maillon humain de terrain

Agent communal ou membre de coopérative, il est la présence physique dans le silo. Son interface fonctionne sur tablette ou PC au bureau communal.

**Ce qu'il peut faire :**
- Enregistrer un dépôt : recherche de l'agriculteur, pesée, saisie de la denrée, génération automatique du reçu physique et envoi du SMS de confirmation
- Enregistrer des retraits partiels ou totaux avec bon de sortie
- Saisir les conditions du silo (température, humidité) et déclencher la vérification automatique des alertes
- Consulter et acquitter les alertes avec commentaire de l'action corrective prise
- Générer le rapport mensuel d'activité pour la commune

---

### 🛒 L'Acheteur — accès à l'offre agricole sénégalaise

Transformateur local, exportateur, commerçant en gros ou ONG d'approvisionnement. Son compte est validé manuellement par l'équipe Grenier Commun avant activation.

**Ce qu'il peut faire :**
- Consulter le catalogue agrégé des stocks disponibles dans le réseau — denrée, région, quantité, qualité estimée — sans données nominatives sur les agriculteurs
- Filtrer par denrée, région, quantité minimale, disponibilité
- Soumettre une offre d'achat transmise à l'équipe Grenier Commun pour matching
- Suivre le statut de ses offres et accéder à l'historique de ses transactions
- Télécharger ses factures en PDF

---

### 🏦 L'IMF Partenaire — financement accéléré et objectivé

Analyste crédit ou décideur d'une institution de microfinance partenaire (PAMECAS, CMS, ACEP...). Accès restreint exclusivement aux dossiers qui le concernent.

**Ce qu'il peut faire :**
- Recevoir les dossiers de warrantage instruits et vérifiés par Grenier Commun
- Consulter le dossier complet : identité de l'agriculteur, stock certifié en garantie, score de crédit IA, historique de remboursements
- Approuver avec le montant et le taux, ou refuser avec motif — l'agriculteur est notifié par SMS automatiquement dans sa langue
- Suivre les remboursements et son portefeuille warrantage complet

---

### ⚙️ L'Admin Grenier Commun — le cockpit de tout le réseau

L'équipe opérationnelle de Grenier Commun pilote l'intégralité du réseau depuis un tableau de bord central.

**Ce qu'il peut faire :**
- Carte interactive du réseau de silos en temps réel avec statut de santé par silo
- KPIs globaux : tonnes stockées, valeur totale des stocks, agriculteurs inscrits, alertes actives, offres en attente
- Gestion de tous les silos, utilisateurs, dossiers warrantage et offres acheteurs
- Matching des offres d'achat avec les stocks disponibles
- Validation et publication des recommandations de vente générées par l'IA avant diffusion aux agriculteurs
- Supervision du module traduction : statistiques de qualité par langue, corrections soumises par les utilisateurs
- Rapports exportables pour les partenaires institutionnels : communes, ministères, bailleurs de fonds

---

## Stack technique

### Architecture en 4 couches

```
┌─────────────────────────────────────────────────────┐
│  INTERFACE       Django Templates · HTMX · Tailwind  │
│                  Alpine.js · Chart.js · Leaflet.js   │
├─────────────────────────────────────────────────────┤
│  LOGIQUE MÉTIER  Django Views · Services · Celery    │
│                  Tasks asynchrones · Permissions     │
├─────────────────────────────────────────────────────┤
│  DONNÉES         PostgreSQL · Django ORM · Redis     │
│                  Cache sessions · Files de tâches    │
├─────────────────────────────────────────────────────┤
│  INTELLIGENCE    Meta NLLB-200 · Google Translate    │
│                  scikit-learn · Price Predictor      │
│                  Credit Scorer · Early Warning       │
└─────────────────────────────────────────────────────┘
```

### Technologies principales

| Composant | Technologie | Rôle |
|---|---|---|
| Framework web | Django 5.0 | Backend, ORM, templates, routing |
| Base de données | PostgreSQL 16 | Persistance principale |
| Cache & broker | Redis | Sessions, cache traductions, Celery |
| Tâches async | Celery | SMS, rapports, scoring IA, alertes |
| Interface | HTMX + Tailwind CSS + Alpine.js | Frontend moderne sans SPA |
| Cartes | Leaflet.js + OpenStreetMap | Carte réseau de silos |
| PDF | WeasyPrint | Reçus, attestations, rapports |
| SMS | Twilio | Notifications agriculteurs multilingues |
| Traduction IA | Meta NLLB-200 (Hugging Face) | Wolof et langues africaines |
| Traduction fallback | deep-translator (Google) | FR / EN / AR sans clé API |
| Déploiement | Render | Web service + PostgreSQL + Redis |
| Stockage fichiers | Cloudinary | PDFs et images |
| Sécurité | django-axes + RBAC + HTTPS | Anti brute-force, rôles stricts |

---

## Module IA — Traduction multilingue native

L'internationalisation de Grenier Commun va bien au-delà d'une simple traduction d'interface. C'est un système à trois niveaux.

### Niveau 1 — Interface traduite (i18n Django)

**4 langues natives**, 400+ chaînes traduites par langue, avec support complet du RTL pour l'arabe :

- 🇫🇷 **Français** — langue source, interface complète
- 🇬🇧 **Anglais** — 408 entrées, interface complète
- 🇸🇦 **Arabe** — 407 entrées, layout RTL, sidebar positionnée à droite
- 🇸🇳 **Wolof** — 105 entrées clés, traduction IA pour le reste

Chaque langue a son préfixe URL (`/fr/`, `/en/`, `/ar/`, `/wo/`). Le changement de langue redirige intelligemment vers la même page dans la nouvelle langue. L'état est mémorisé.

### Niveau 2 — Module de traduction IA (contenu métier)

Accessible depuis le menu de tout utilisateur, il permet de traduire à la demande :

- Reçus de dépôt, alertes système, recommandations de vente, messages SMS, rapports
- **Deux moteurs selon la paire de langues** : Google Translate (FR/EN/AR, rapide, sans clé) et Meta NLLB-200 (tout ce qui implique le Wolof — le seul modèle open-source de référence pour les langues africaines, entraîné sur 200 langues)
- **Historique par utilisateur** : chaque traduction conservée, consultable, filtrable
- **Système de correction communautaire** : après chaque traduction, suggestion de correction possible — les retours s'accumulent pour améliorer la qualité future
- **Cache Redis 24h** : une traduction effectuée ne repasse plus par l'IA — réponse instantanée
- **Indicateur de source** : ⚡ cache ou 🤖 IA, avec temps de traitement en ms

### Niveau 3 — AutoTranslateMiddleware (filet de sécurité)

Un middleware intercepte les réponses HTML avant envoi au navigateur et traduit automatiquement tout texte non couvert par les fichiers `.po`. Les pages complètes sont mises en cache 30 minutes via Redis. L'utilisateur ne voit jamais de texte en français par accident dans une session anglaise ou wolof.

---

## Module IA — Intelligence métier

### Price Predictor
Modèle de prédiction de prix (Random Forest / XGBoost) entraîné sur les historiques de marchés sénégalais (DAPSA, OMA), les volumes stockés dans le réseau, la météo et le calendrier agricole. Il génère chaque semaine une recommandation de vente par denrée — validée par l'admin avant publication.

### Credit Scorer
Score de risque de 0 à 100 calculé pour chaque agriculteur à partir de son ancienneté dans le système, son volume moyen stocké, son historique de remboursements et sa régularité. Ce score accompagne chaque dossier transmis à l'IMF pour accélérer et objectiver la décision de crédit.

### Early Warning System
Surveillance des conditions de conservation (température, humidité) dans chaque silo. Alertes graduées (surveillance / intervention requise / urgence) avec message en langage naturel. Détection des signaux faibles avant qu'une dégradation soit visible.

---

## Modèle économique intégré

La plateforme génère des revenus sur chaque maillon de la chaîne :

| Source | Mécanisme | Taux |
|---|---|---|
| Location de stockage | Calculée automatiquement à chaque dépôt | 1,5 % de la valeur du stock / mois |
| Commission warrantage | Prélevée à l'approbation du crédit | 1,5 % du montant accordé |
| Commission sur ventes | Prélevée à la finalisation de la transaction | 2 % du montant de la vente |
| Données agrégées | Abonnement institutionnel annuel | Ministères, ONG, fonds agricoles |

---

## Sécurité

- **Authentification multi-facteur** : OTP SMS pour les agriculteurs, email + OTP pour les comptes sensibles
- **RBAC strict** : 5 rôles distincts, chaque utilisateur accède uniquement aux données qui le concernent
- **Anti brute-force** : django-axes, verrouillage après 5 tentatives échouées
- **HTTPS forcé** en production avec HSTS
- **Protection CSRF** sur tous les formulaires
- **Logs d'audit immuables** pour toutes les actions sensibles
- **Séparation des données** : aucune donnée nominative d'agriculteur visible par les acheteurs

---

## Installation locale

```bash
# Cloner le projet
git clone https://github.com/votre-username/grenier-commun.git
cd grenier-commun

# Environnement virtuel
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux

# Dépendances
pip install -r requirements.txt

# Configuration
cp .env.complet .env         # Remplir les valeurs obligatoires

# Base de données (PostgreSQL requis)
createdb grenier_commun

# Initialisation
python setup_project.py
python manage.py makemigrations accounts silos core
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Variables `.env` obligatoires pour démarrer :**
```
SECRET_KEY=votre-cle-secrete
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres:mdp@localhost:5432/grenier_commun
REDIS_URL=redis://127.0.0.1:6379/0
HUGGINGFACE_API_KEY=hf_xxxxx   # Pour la traduction Wolof
```

---

## Roadmap

| Phase | Période | Contenu |
|---|---|---|
| ✅ MVP V1.0 | Mois 1–4 | 5 espaces, warrantage, traduction IA 4 langues, IA métier |
| 🔄 Pilote terrain | Mois 5–6 | 2–3 communes pilotes au Sénégal, formation, retours |
| 📋 V1.5 | Mois 7–9 | Intégration Wave/Orange Money, agriculture contractuelle |
| 🤖 V2.0 | Mois 10–12 | Modèles ML entraînés sur données réelles, scoring automatisé |
| 🌍 V3.0 | Année 2 | Mali, Côte d'Ivoire, Burkina Faso — architecture multi-pays prête |

---

## Impact visé

- **Doubler le prix de vente effectif** pour les agriculteurs en leur permettant d'attendre le bon moment
- **Réduire les pertes post-récolte de 30 à 40 %** grâce à des silos surveillés en temps réel
- **Démocratiser l'accès au crédit warrantage** avec un processus 100 % numérique, décision en 48h
- **Première plateforme AgriTech professionnelle en Wolof** — la langue de 80 % des Sénégalais
- **Architecture multi-pays** prête : Mali, Côte d'Ivoire, Burkina Faso sans reconstruction

---

## Structure du projet

```
grenier_commun/
├── config/                  # Settings, URLs, Celery, WSGI
├── apps/
│   ├── core/                # Modèles partagés, décorateurs, context processors
│   ├── accounts/            # Utilisateurs custom, OTP, 5 rôles
│   ├── silos/               # Silos, Dépôts, Retraits, Alertes, Denrées
│   ├── agriculteurs/        # Espace agriculteur
│   ├── warrantage/          # Crédits warrantage
│   ├── marche/              # Offres d'achat, transactions, prix
│   ├── imf/                 # Espace IMF partenaires
│   ├── notifications/       # SMS, in-app, email multilingues
│   ├── traduction/          # Module IA NLLB-200, historique, corrections
│   ├── intelligence/        # Price Predictor, Credit Scorer, Early Warning
│   └── administration/      # Cockpit admin Grenier Commun
├── templates/               # 42 templates HTML
├── static/                  # CSS design system, JS
├── locale/                  # fr / en / ar / wo — fichiers .po et .mo
└── compile_mo.py            # Compilateur .mo sans dépendances externes
```

---

## Licence

Ce projet est développé dans le cadre d'un projet académique et entrepreneurial. Tous droits réservés — contact pour partenariats et déploiements.

---

<p align="center">
  <strong>Grenier Commun</strong> · Sénégal · Afrique de l'Ouest · 2025<br>
  <em>Stocker mieux. Financer plus vite. Vendre au bon moment.</em>
</p>
