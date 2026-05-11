# 🌾 Grenier Commun
### *La plateforme qui donne aux agriculteurs sénégalais le pouvoir de vendre au bon prix*

<p align="center">
  <img src="https://img.shields.io/badge/Django-5.0-092E20?style=for-the-badge&logo=django&logoColor=white"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white"/>
  <img src="https://img.shields.io/badge/Redis-Cache-DC382D?style=for-the-badge&logo=redis&logoColor=white"/>
  <img src="https://img.shields.io/badge/Claude_API-Chatbot_IA-7C3AED?style=for-the-badge&logo=anthropic&logoColor=white"/>
  <img src="https://img.shields.io/badge/Meta_NLLB--200-IA_Wolof-0082C9?style=for-the-badge&logo=meta&logoColor=white"/>
  <img src="https://img.shields.io/badge/Langues-FR_·_EN_·_AR_·_WO-1A6B3A?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Déploiement-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white"/>
</p>

---
https://web-production-04b0a.up.railway.app

## Le problème : trois injustices qui se répètent chaque saison

Au Sénégal, l'agriculture emploie plus de **22 % de la population active**. Pourtant, saison après saison, des millions de petits agriculteurs subissent les mêmes trois injustices — non pas par manque de travail, mais par manque d'infrastructure, de financement et d'information.

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

> ***Stocker mieux. Financer plus vite. Vendre au bon moment.***

La plateforme repose sur un réseau de **silos physiques connectés** déployés dans les communes rurales sénégalaises, pilotés par une interface web multi-acteurs accessible en **quatre langues** — dont le Wolof, la langue nationale parlée par plus de 80 % des Sénégalais — et assistée par un **chatbot IA contextuel** qui accompagne chaque utilisateur dans sa langue, avec accès aux données réelles de la plateforme.

Ce n'est pas une application de plus. C'est une **infrastructure digitale agricole** : le système nerveux numérique qui manquait entre le champ, le silo, la banque et le marché.

---

![Page Visiteur](screenshoots/visitor.png)

## Ce qui rend ce projet unique

Plusieurs acteurs opèrent dans l'écosystème agricole sénégalais. Aucun ne combine ces dimensions dans un seul produit intégré :

| Acteur existant | Ce qu'il fait | Ce qui manque |
|---|---|---|
| Silos traditionnels | Stockage physique | Zéro numérique, zéro financement, zéro marché |
| Institutions de microfinance | Crédit warrantage manuel | Processus lent, pas de traçabilité du stock |
| Plateformes de prix (OMA, ESOKO) | Information sur les marchés | Pas de stockage, pas de financement |
| Coopératives agricoles | Organisation des producteurs | Pas de technologie, pas de financement intégré |
| **Grenier Commun** | **Stockage + Financement + Marché + Chatbot IA + 4 langues** | **C'est la combinaison qui n'existait pas** |

---

## Architecture de la solution

```
AGRICULTEUR ──→ SILO PHYSIQUE CONNECTÉ ──→ PLATEFORME WEB ──→ IMF PARTENAIRE
                      │                          │
                      │                    CHATBOT IA ←──→ Données réelles
                      │                          │
                      │                          ├──→ ACHETEUR
                      └──────────────────────────└──→ ADMIN GRENIER COMMUN
```

La plateforme s'organise autour de **cinq espaces utilisateurs** avec des rôles, droits et interfaces distincts, chacun assisté par un chatbot IA conscient du contexte.

---

## Les cinq espaces utilisateurs

### 🌾 L'Agriculteur — le cœur du projet

L'agriculteur est l'utilisateur central. Son interface est conçue pour quelqu'un qui n'est pas forcément à l'aise avec le numérique : indicateurs visuels vert/orange/rouge plutôt que chiffres bruts, navigation en 3 clics maximum, disponible en français et en Wolof.

**Gestion des stocks :**
- Consulter ses stocks en temps réel — quantité disponible, silo, date de dépôt, état de santé
- Savoir précisément quand retirer son stock selon les conditions de conservation
- Télécharger et comprendre son reçu de dépôt PDF — document légalement traçable

**Prix et décisions de vente :**
- Suivre les prix du marché hebdomadaires par denrée et par région
- Comparer les offres acheteurs disponibles dans le réseau
- Recevoir une recommandation IA : *"Vendre maintenant"* ou *"Attendez encore 4 semaines"* avec justification chiffrée

**Warrantage et crédit :**
- Calculer en temps réel combien il peut emprunter sur son stock (70 % de la valeur)
- Simuler les intérêts selon la durée et le taux de l'IMF choisie
- Faire une demande de crédit directement depuis la plateforme, sans déplacement
- Suivre son dossier : soumis → en instruction → approuvé → fonds virés
- Consulter la liste des IMF partenaires avec leurs conditions

**Historique et notifications :**
- Voir ses ventes passées et en cours avec le détail des prix obtenus
- Suivre l'état de toutes ses demandes de warrantage sur plusieurs saisons
- Recevoir des SMS traduits dans sa langue préférée
- Être alerté proactivement : *"Le prix du mil a augmenté de 15 % cette semaine"* ou *"Votre warrantage expire dans 10 jours"*

---

### 🏛️ Le Gestionnaire de Silo — le maillon humain de terrain

Agent communal ou membre de coopérative, il est la présence physique dans le silo. Son interface fonctionne sur tablette ou PC au bureau communal.

**Ce qu'il peut faire :**
- Enregistrer un dépôt guidé étape par étape avec génération automatique du reçu et envoi SMS de confirmation
- Enregistrer des retraits partiels ou totaux avec bon de sortie
- Voir le taux de remplissage du silo en temps réel et la capacité restante disponible
- Consulter, gérer et acquitter les alertes actives — humidité, température, capacité maximale
- Saisir les conditions du silo et déclencher la vérification automatique des seuils
- Générer le résumé du rapport mensuel d'activité pour la commune

---

### 🛒 L'Acheteur — accès à l'offre agricole sénégalaise

Transformateur local, exportateur, commerçant en gros ou ONG d'approvisionnement. Compte validé manuellement avant activation.

**Ce qu'il peut faire :**
- Consulter le catalogue agrégé des stocks disponibles sans données nominatives sur les agriculteurs
- Connaître les prix actuels par denrée et par région pour calibrer ses offres
- Comparer les prix disponibles dans le réseau avant de soumettre
- Soumettre une offre d'achat et savoir en temps réel si elle a trouvé preneur
- Accéder à l'historique de ses transactions et télécharger ses factures PDF

---

### 🏦 L'IMF Partenaire — financement accéléré et objectivé

Analyste crédit ou décideur d'une institution de microfinance partenaire (PAMECAS, CMS, ACEP...).

**Ce qu'il peut faire :**
- Recevoir les dossiers instruits avec stock certifié en garantie et score de crédit IA
- Résumer en un coup d'œil les dossiers en attente de décision
- Consulter le score de crédit (0-100) et l'historique complet de chaque agriculteur
- Comprendre les critères d'approbation utilisés par le scoring IA
- Approuver ou refuser — l'agriculteur est notifié par SMS dans sa langue
- Suivre les remboursements et son portefeuille warrantage complet

---

### ⚙️ L'Admin Grenier Commun — le cockpit de tout le réseau

**Ce qu'il peut faire :**
- Vue globale temps réel : utilisateurs actifs, stocks totaux, transactions du mois, alertes
- Carte interactive du réseau de silos avec statut de santé par silo
- Matching des offres d'achat avec les stocks disponibles
- Lister et valider les recommandations IA en attente avant publication
- Résumé financier du mois : commissions, warrantages actifs, loyers de stockage
- Supervision du module traduction : qualité par langue, corrections soumises

---

## 🤖 Le Chatbot IA — l'assistant contextuel intégré

C'est la fonctionnalité qui distingue Grenier Commun de toute autre plateforme agricole africaine. Un assistant conversationnel propulsé par **Claude (Anthropic)** est disponible en permanence pour chaque utilisateur connecté — bouton flottant en bas à droite de chaque page.

Il ne répond pas depuis une base de connaissances statique. Il **accède aux données réelles de la plateforme en temps réel** via des function calls, puis formule une réponse en langage naturel dans la langue de l'utilisateur.

### Architecture technique

```python
# 15 outils métier que le chatbot appelle selon la question posée

get_stocks(user)           # stocks réels de l'agriculteur connecté
get_prix_marche(denree)    # prix actuels du marché par denrée
get_warrantage_status()    # état précis des dossiers de crédit
get_alertes_silo()         # alertes actives du silo en temps réel
get_dossiers_imf()         # dossiers en attente de décision IMF
get_stats_admin()          # vue globale de la plateforme pour l'admin
calculer_credit(depot)     # simulation de crédit warrantage
calculer_interets(...)     # calcul des intérêts selon durée et taux
translate(texte, lang)     # traduction inline sans quitter le chat
get_recommandations()      # recommandations IA de vente publiées
get_offres_acheteur()      # offres soumises et leur statut actuel
get_imf_partenaires()      # liste des IMF avec leurs conditions
get_notifications()        # résumé des notifications non lues
get_rapport_mensuel()      # synthèse du rapport silo du mois
get_finances_admin()       # données financières pour l'admin
```

### Ce que le chatbot fait selon le rôle

**Agriculteur** — questions de terrain, en Wolof si besoin :
- *"Combien je peux emprunter sur mon stock d'arachide ?"* → calcul en direct sur données réelles
- *"Est-ce le bon moment pour vendre mon mil ?"* → recommandation IA + prix actuels
- *"Où en est ma demande de crédit ?"* → statut précis du dossier
- *"Traduis mon reçu en Wolof"* → traduction inline sans quitter la conversation
- *"Mon OTP n'arrive pas"* → diagnostic et résolution guidée étape par étape

**Gestionnaire** — pilotage opérationnel du silo :
- *"Montre-moi les alertes actives"* → liste en temps réel avec niveaux de gravité
- *"Comment enregistrer un retrait ?"* → guide étape par étape
- *"Génère le résumé du rapport du mois"* → synthèse automatique

**IMF** — instruction rapide des dossiers :
- *"Combien de dossiers sont en attente ?"* → résumé immédiat
- *"Quel est le score de crédit d'Amadou Diallo ?"* → score + historique complet
- *"Quels sont les critères d'approbation ?"* → explication des règles de scoring

**Acheteur** — recherche et suivi d'offres :
- *"Y a-t-il du sorgho disponible à Kaolack ?"* → catalogue filtré en direct
- *"Mon offre a-t-elle trouvé preneur ?"* → statut précis en temps réel

**Admin** — supervision globale :
- *"Donne-moi une vue globale de la plateforme"* → KPIs temps réel
- *"Quelles recommandations IA sont en attente ?"* → liste avec détails
- *"Résume les finances du mois"* → rapport financier synthétique

### Caractéristiques

- **Historique de conversation en session** — le contexte est maintenu tout au long de l'échange
- **Suggestions rapides par rôle** — 3-4 questions pré-remplies à l'ouverture selon le profil
- **Réponse dans la langue préférée** — détecte et répond en Wolof, arabe, anglais ou français
- **Interface HTMX** — messages en temps réel sans rechargement de page
- **Widget non-intrusif** — bouton flottant discret, panel rétractable

---

## Module IA — Traduction multilingue native

### Niveau 1 — Interface traduite (i18n Django)

**4 langues natives**, 400+ chaînes traduites, support RTL complet pour l'arabe :

- 🇫🇷 **Français** — langue source, interface complète
- 🇬🇧 **Anglais** — 408 entrées, interface complète
- 🇸🇦 **Arabe** — 407 entrées, layout RTL, sidebar à droite, contenu en miroir
- 🇸🇳 **Wolof** — 105 entrées clés, traduction IA Meta NLLB-200 pour le reste

Chaque langue a son préfixe URL (`/fr/`, `/en/`, `/ar/`, `/wo/`). La sidebar est rétractable avec persistance dans le navigateur.

### Niveau 2 — Module de traduction IA (contenu métier)

Accessible depuis le menu ou directement dans le chat :
- Reçus, alertes, recommandations de vente, SMS, rapports
- **Google Translate** (FR/EN/AR, sans clé) et **Meta NLLB-200** (tout ce qui implique le Wolof)
- Historique par utilisateur, système de correction communautaire, cache Redis 24h

### Niveau 3 — AutoTranslateMiddleware

Intercepte les réponses HTML et traduit automatiquement tout texte non couvert par les fichiers `.po`. Pages mises en cache 30 minutes. L'utilisateur ne voit jamais de texte en français par accident.

---

## Module IA — Intelligence métier

**Price Predictor** — Random Forest / XGBoost entraîné sur les historiques DAPSA/OMA. Recommandations de vente hebdomadaires validées par l'admin avant publication.

**Credit Scorer** — Score 0-100 par agriculteur basé sur ancienneté, volumes, historique de remboursements. Accompagne chaque dossier IMF pour objectiver la décision.

**Early Warning System** — Surveillance température/humidité dans chaque silo. Alertes graduées en langage naturel. Détection des signaux faibles avant dégradation visible.

---

## Stack technique

### Architecture en 4 couches

```
┌──────────────────────────────────────────────────────────┐
│  INTERFACE       Django Templates · HTMX · Tailwind CSS  │
│                  Alpine.js · Chart.js · Leaflet.js       │
│                  Chatbot widget flottant (HTMX)          │
├──────────────────────────────────────────────────────────┤
│  LOGIQUE MÉTIER  Django Views · Services · Celery tasks  │
│                  15 outils chatbot · Permissions RBAC    │
├──────────────────────────────────────────────────────────┤
│  DONNÉES         PostgreSQL · Django ORM · Redis         │
│                  Cache sessions · Files de tâches        │
├──────────────────────────────────────────────────────────┤
│  INTELLIGENCE    Claude API (chatbot contextuel)         │
│                  Meta NLLB-200 · Google Translate        │
│                  scikit-learn · Price Predictor          │
│                  Credit Scorer · Early Warning           │
└──────────────────────────────────────────────────────────┘
```

| Composant | Technologie | Rôle |
|---|---|---|
| Framework | Django 5.0 | Backend, ORM, templates, routing |
| Base de données | PostgreSQL 16 | Persistance principale |
| Cache & broker | Redis | Sessions, cache traductions, Celery |
| Tâches async | Celery | SMS, rapports, scoring IA, alertes |
| Interface | HTMX + Tailwind CSS + Alpine.js | Frontend moderne sans SPA |
| Chatbot IA | Claude API + function calls | Assistant contextuel multi-rôles |
| Cartes | Leaflet.js + OpenStreetMap | Carte réseau de silos |
| PDF | WeasyPrint | Reçus, attestations, rapports |
| SMS | Twilio | Notifications multilingues |
| Traduction IA | Meta NLLB-200 (Hugging Face) | Wolof et langues africaines |
| Traduction fallback | deep-translator (Google) | FR / EN / AR sans clé API |
| i18n | Django gettext + .po/.mo | Interface 4 langues native |
| Déploiement | Render | Web service + PostgreSQL + Redis |
| Stockage | Cloudinary | PDFs et images |
| Sécurité | django-axes + RBAC + HTTPS | Anti brute-force, rôles stricts |

---

## Modèle économique

| Source | Mécanisme | Taux |
|---|---|---|
| Location de stockage | Calculée automatiquement à chaque dépôt | 1,5 % / mois |
| Commission warrantage | Prélevée à l'approbation du crédit | 1,5 % du montant |
| Commission sur ventes | Prélevée à la finalisation | 2 % de la transaction |
| Données agrégées | Abonnement institutionnel annuel | Ministères, ONG, fonds |

---

## Sécurité

- **Authentification multi-facteur** : OTP SMS agriculteurs, email + OTP comptes sensibles
- **RBAC strict** : 5 rôles distincts, accès cloisonné aux données
- **Anti brute-force** : django-axes, verrouillage après 5 tentatives
- **HTTPS forcé** en production avec HSTS
- **Protection CSRF** sur tous les formulaires
- **Séparation des données** : aucune donnée nominative agriculteur visible par les acheteurs

---

## Installation locale

```bash
git clone https://github.com/votre-username/grenier-commun.git
cd grenier-commun
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # Mac / Linux
pip install -r requirements.txt
cp .env.complet .env           # Remplir les valeurs
createdb grenier_commun
python setup_project.py
python manage.py makemigrations accounts silos core
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Variables `.env` minimales :**
```
SECRET_KEY=votre-cle-secrete
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres:mdp@localhost:5432/grenier_commun
REDIS_URL=redis://127.0.0.1:6379/0
HUGGINGFACE_API_KEY=hf_xxxxx       # Traduction Wolof (NLLB-200)
ANTHROPIC_API_KEY=sk-ant-xxxxx     # Chatbot IA (Claude)
```

---

## Roadmap

| Phase | Période | Contenu |
|---|---|---|
| ✅ MVP V1.0 | Mois 1–4 | 5 espaces, warrantage, traduction 4 langues, chatbot IA, IA métier |
| 🔄 Pilote terrain | Mois 5–6 | 2–3 communes pilotes au Sénégal, formation, retours |
| 📋 V1.5 | Mois 7–9 | Wave/Orange Money, agriculture contractuelle |
| 🤖 V2.0 | Mois 10–12 | ML entraîné sur données réelles, scoring automatisé |
| 🌍 V3.0 | Année 2 | Mali, Côte d'Ivoire, Burkina Faso |

---

## Impact visé

- **Doubler le prix de vente effectif** en permettant aux agriculteurs d'attendre le bon moment
- **Réduire les pertes post-récolte de 30–40 %** grâce à des silos surveillés en temps réel
- **Démocratiser l'accès au crédit warrantage** — processus 100 % numérique, décision en 48h
- **Première plateforme AgriTech professionnelle en Wolof** — langue de 80 % des Sénégalais
- **Premier chatbot agricole africain** accédant aux données réelles en temps réel
- **Architecture multi-pays** prête sans reconstruction

---

## Structure du projet

```
grenier_commun/
├── config/                  # Settings, URLs, Celery, WSGI
├── apps/
│   ├── core/                # Modèles partagés, décorateurs
│   ├── accounts/            # Utilisateurs custom, OTP, 5 rôles
│   ├── silos/               # Silos, Dépôts, Retraits, Alertes
│   ├── agriculteurs/        # Espace agriculteur
│   ├── warrantage/          # Crédits warrantage
│   ├── marche/              # Offres, transactions, prix
│   ├── imf/                 # Espace IMF partenaires
│   ├── notifications/       # SMS, in-app, email multilingues
│   ├── traduction/          # NLLB-200, historique, corrections
│   ├── intelligence/        # Price Predictor, Credit Scorer, Early Warning
│   ├── chatbot/             # Claude API · 15 outils · widget HTMX
│   └── administration/      # Cockpit admin
├── templates/               # 42+ templates HTML
├── static/                  # CSS design system, JS
├── locale/                  # fr / en / ar / wo — .po et .mo
└── compile_mo.py            # Compilateur .mo autonome
```

---

## Licence

Projet académique et entrepreneurial. Tous droits réservés — contact pour partenariats et déploiements.

---

<p align="center">
  <strong>Grenier Commun</strong> · Sénégal · Afrique de l'Ouest · 2025<br>
  <em>Stocker mieux. Financer plus vite. Vendre au bon moment.</em>
</p>
