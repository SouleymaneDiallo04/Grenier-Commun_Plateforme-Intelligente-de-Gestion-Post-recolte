"""
Grenier Commun — Modèles Warrantage, Marché, Traduction, Notifications
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator


# ══════════════════════════════════════════════════════════════════════════════
# WARRANTAGE / CRÉDIT
# ══════════════════════════════════════════════════════════════════════════════

class IMFPartenaire(models.Model):
    """Institution de Microfinance partenaire."""
    nom = models.CharField(_('nom'), max_length=200)
    sigle = models.CharField(_('sigle'), max_length=20, blank=True)
    contact_nom = models.CharField(_('contact principal'), max_length=150)
    contact_email = models.EmailField()
    contact_telephone = models.CharField(max_length=20)
    adresse = models.TextField(blank=True)
    taux_interet_mensuel = models.DecimalField(
        _('taux d\'intérêt mensuel (%)'), max_digits=5, decimal_places=2, default=2.0
    )
    delai_traitement_jours = models.PositiveIntegerField(_('délai de traitement (jours)'), default=5)
    actif = models.BooleanField(default=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('IMF partenaire')
        ordering = ['nom']

    def __str__(self):
        return f'{self.sigle or self.nom}'


class ProfilAgriculteur(models.Model):
    """Profil étendu de l'agriculteur avec données agricoles."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profil_agriculteur'
    )
    commune = models.ForeignKey(
        'silos.Commune', on_delete=models.SET_NULL, null=True, blank=True
    )
    village = models.CharField(_('village'), max_length=150, blank=True)
    superficie_ha = models.DecimalField(
        _('superficie (ha)'), max_digits=8, decimal_places=2, null=True, blank=True
    )
    cultures_principales = models.ManyToManyField('silos.Denree', blank=True)
    numero_agriculteur = models.CharField(_('numéro agriculteur'), max_length=30, unique=True, blank=True)

    # Score de crédit calculé par l'IA
    score_credit = models.PositiveSmallIntegerField(_('score de crédit'), default=50)
    score_calcule_le = models.DateTimeField(null=True, blank=True)

    bio = models.TextField(_('présentation'), blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('profil agriculteur')

    def __str__(self):
        return f'Profil de {self.user.nom_complet}'

    @property
    def categorie_risque(self):
        if self.score_credit >= 70:
            return 'FAIBLE'
        elif self.score_credit >= 40:
            return 'MOYEN'
        return 'ELEVE'


class WarrantageCredit(models.Model):
    """Demande de crédit warrantage adossée à un dépôt."""

    STATUT_SOUMIS = 'SOUMIS'
    STATUT_EN_INSTRUCTION = 'EN_INSTRUCTION'
    STATUT_APPROUVE = 'APPROUVE'
    STATUT_REFUSE = 'REFUSE'
    STATUT_VIRE = 'VIRE'
    STATUT_REMBOURSE = 'REMBOURSE'
    STATUT_EN_DEFAUT = 'EN_DEFAUT'

    STATUT_CHOICES = [
        (STATUT_SOUMIS, _('Soumis')),
        (STATUT_EN_INSTRUCTION, _('En instruction')),
        (STATUT_APPROUVE, _('Approuvé')),
        (STATUT_REFUSE, _('Refusé')),
        (STATUT_VIRE, _('Fonds virés')),
        (STATUT_REMBOURSE, _('Remboursé')),
        (STATUT_EN_DEFAUT, _('En défaut')),
    ]

    depot = models.OneToOneField(
        'silos.Depot', on_delete=models.PROTECT, related_name='warrantage'
    )
    imf = models.ForeignKey(
        IMFPartenaire, on_delete=models.PROTECT, related_name='credits',
        null=True, blank=True
    )
    agriculteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='warrantages'
    )

    # Montants
    montant_demande_fcfa = models.DecimalField(
        _('montant demandé (FCFA)'), max_digits=12, decimal_places=2
    )
    montant_accorde_fcfa = models.DecimalField(
        _('montant accordé (FCFA)'), max_digits=12, decimal_places=2,
        null=True, blank=True
    )
    taux_interet_mensuel = models.DecimalField(
        _('taux d\'intérêt mensuel (%)'), max_digits=5, decimal_places=2,
        null=True, blank=True
    )
    duree_mois = models.PositiveSmallIntegerField(_('durée (mois)'), default=3)

    # Score IA au moment de la demande
    score_credit_snapshot = models.PositiveSmallIntegerField(null=True, blank=True)

    # Statut
    statut = models.CharField(_('statut'), max_length=20, choices=STATUT_CHOICES, default=STATUT_SOUMIS)
    motif_refus = models.TextField(_('motif de refus'), blank=True)

    # Paiement
    mode_paiement = models.CharField(_('mode de paiement'), max_length=50, default='Wave')
    numero_paiement = models.CharField(_('numéro Wave/Orange Money'), max_length=30, blank=True)

    # Dates
    date_demande = models.DateTimeField(auto_now_add=True)
    date_decision = models.DateTimeField(null=True, blank=True)
    date_virement = models.DateTimeField(null=True, blank=True)
    date_echeance = models.DateField(null=True, blank=True)
    date_remboursement = models.DateTimeField(null=True, blank=True)

    # Documents
    dossier_pdf = models.FileField(upload_to='warrantages/', null=True, blank=True)

    class Meta:
        verbose_name = _('warrantage / crédit')
        ordering = ['-date_demande']

    def __str__(self):
        return f'Warrantage {self.montant_demande_fcfa} FCFA — {self.agriculteur.nom_complet}'


# ══════════════════════════════════════════════════════════════════════════════
# MARCHÉ & PRIX
# ══════════════════════════════════════════════════════════════════════════════

class PrixMarche(models.Model):
    """Prix de marché de référence par denrée et région."""
    denree = models.ForeignKey('silos.Denree', on_delete=models.CASCADE, related_name='prix')
    region = models.CharField(_('région'), max_length=100, default='National')
    pays = models.CharField(_('pays'), max_length=50, default='Sénégal')
    prix_kg_fcfa = models.DecimalField(_('prix (FCFA/kg)'), max_digits=10, decimal_places=2)
    prix_min_fcfa = models.DecimalField(_('prix min (FCFA/kg)'), max_digits=10, decimal_places=2, null=True, blank=True)
    prix_max_fcfa = models.DecimalField(_('prix max (FCFA/kg)'), max_digits=10, decimal_places=2, null=True, blank=True)
    source = models.CharField(_('source'), max_length=100, default='DAPSA/OMA')
    date_maj = models.DateField(_('date de mise à jour'), auto_now_add=True)
    semaine = models.PositiveSmallIntegerField(null=True, blank=True)
    annee = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = _('prix de marché')
        ordering = ['-date_maj', 'denree']

    def __str__(self):
        return f'{self.denree.nom} — {self.prix_kg_fcfa} FCFA/kg ({self.date_maj})'


class RecommandationVente(models.Model):
    """Recommandation de vente générée par l'IA pour une denrée."""
    ATTENDRE = 'ATTENDRE'
    VENDRE = 'VENDRE'
    VENDRE_PARTIELLEMENT = 'PARTIEL'

    ACTION_CHOICES = [
        (ATTENDRE, _('Attendre')),
        (VENDRE, _('Vendre maintenant')),
        (VENDRE_PARTIELLEMENT, _('Vendre partiellement')),
    ]

    denree = models.ForeignKey('silos.Denree', on_delete=models.CASCADE)
    action_recommandee = models.CharField(_('action'), max_length=10, choices=ACTION_CHOICES)
    message_fr = models.TextField(_('message (FR)'))
    message_wo = models.TextField(_('message (Wolof)'), blank=True)
    message_en = models.TextField(_('message (EN)'), blank=True)
    prix_actuel_fcfa = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    prix_prevu_4sem_fcfa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    prix_prevu_8sem_fcfa = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    validee_par_admin = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)
    valide_jusqu_au = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = _('recommandation de vente')
        ordering = ['-cree_le']

    def __str__(self):
        return f'Reco {self.denree.nom} — {self.get_action_recommandee_display()}'


class OffreAchat(models.Model):
    """Offre d'achat soumise par un acheteur."""

    STATUT_SOUMISE = 'SOUMISE'
    STATUT_EN_NEGOCIATION = 'NEGOCIATION'
    STATUT_ACCEPTEE = 'ACCEPTEE'
    STATUT_REFUSEE = 'REFUSEE'
    STATUT_ANNULEE = 'ANNULEE'
    STATUT_FINALISEE = 'FINALISEE'

    STATUT_CHOICES = [
        (STATUT_SOUMISE, _('Soumise')),
        (STATUT_EN_NEGOCIATION, _('En négociation')),
        (STATUT_ACCEPTEE, _('Acceptée')),
        (STATUT_REFUSEE, _('Refusée')),
        (STATUT_ANNULEE, _('Annulée')),
        (STATUT_FINALISEE, _('Finalisée')),
    ]

    acheteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='offres_achat'
    )
    denree = models.ForeignKey('silos.Denree', on_delete=models.PROTECT)
    quantite_kg = models.DecimalField(_('quantité souhaitée (kg)'), max_digits=10, decimal_places=2)
    prix_propose_fcfa = models.DecimalField(_('prix proposé (FCFA/kg)'), max_digits=10, decimal_places=2)
    region_preferee = models.CharField(_('région préférée'), max_length=100, blank=True)
    delai_souhaite_jours = models.PositiveSmallIntegerField(_('délai souhaité (jours)'), default=30)
    statut = models.CharField(_('statut'), max_length=15, choices=STATUT_CHOICES, default=STATUT_SOUMISE)
    notes = models.TextField(_('notes'), blank=True)

    # Matching avec agriculteurs (géré par admin)
    depots_cibles = models.ManyToManyField('silos.Depot', blank=True, related_name='offres')

    date_offre = models.DateTimeField(auto_now_add=True)
    date_decision = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('offre d\'achat')
        ordering = ['-date_offre']

    def __str__(self):
        return f'Offre {self.acheteur.nom_complet} — {self.quantite_kg}kg {self.denree.nom}'


class Transaction(models.Model):
    """Transaction de vente finalisée."""
    offre = models.OneToOneField(OffreAchat, on_delete=models.PROTECT, related_name='transaction')
    retrait = models.OneToOneField('silos.Retrait', on_delete=models.PROTECT, related_name='transaction')
    montant_total_fcfa = models.DecimalField(max_digits=12, decimal_places=2)
    commission_gc_fcfa = models.DecimalField(_('commission GC'), max_digits=10, decimal_places=2)
    date_transaction = models.DateTimeField(auto_now_add=True)
    facture_pdf = models.FileField(upload_to='factures/', null=True, blank=True)

    class Meta:
        verbose_name = _('transaction')
        ordering = ['-date_transaction']

    def __str__(self):
        return f'Transaction {self.montant_total_fcfa} FCFA — {self.date_transaction.date()}'


# ══════════════════════════════════════════════════════════════════════════════
# TRADUCTION IA
# ══════════════════════════════════════════════════════════════════════════════

class TranslationLog(models.Model):
    """Historique complet des traductions effectuées."""

    TYPE_RECU = 'RECU'
    TYPE_ALERTE = 'ALERTE'
    TYPE_RECOMMANDATION = 'RECOMMANDATION'
    TYPE_SMS = 'SMS'
    TYPE_NOTIFICATION = 'NOTIFICATION'
    TYPE_RAPPORT = 'RAPPORT'
    TYPE_AUTRE = 'AUTRE'

    TYPE_CHOICES = [
        (TYPE_RECU, _('Reçu de dépôt')),
        (TYPE_ALERTE, _('Alerte système')),
        (TYPE_RECOMMANDATION, _('Recommandation de vente')),
        (TYPE_SMS, _('SMS agriculteur')),
        (TYPE_NOTIFICATION, _('Notification')),
        (TYPE_RAPPORT, _('Rapport')),
        (TYPE_AUTRE, _('Autre')),
    ]

    MOTEUR_NLLB = 'NLLB200'
    MOTEUR_GOOGLE = 'GOOGLE'
    MOTEUR_MANUEL = 'MANUEL'

    MOTEUR_CHOICES = [
        (MOTEUR_NLLB, 'Meta NLLB-200'),
        (MOTEUR_GOOGLE, 'Google Translate'),
        (MOTEUR_MANUEL, 'Traduction manuelle'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='traductions'
    )
    type_contenu = models.CharField(_('type de contenu'), max_length=20, choices=TYPE_CHOICES, default=TYPE_AUTRE)
    texte_source = models.TextField(_('texte source'))
    texte_traduit = models.TextField(_('texte traduit'))
    langue_source = models.CharField(_('langue source'), max_length=5, default='fr')
    langue_cible = models.CharField(_('langue cible'), max_length=5)
    moteur = models.CharField(_('moteur de traduction'), max_length=10, choices=MOTEUR_CHOICES, default=MOTEUR_NLLB)

    # Évaluation de la qualité
    note_qualite = models.PositiveSmallIntegerField(
        _('note qualité (1-5)'), null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    suggestion_correction = models.TextField(_('suggestion de correction'), blank=True)
    correction_traitee = models.BooleanField(_('correction traitée'), default=False)

    # Métadonnées
    temps_traitement_ms = models.PositiveIntegerField(_('temps (ms)'), null=True, blank=True)
    depuis_cache = models.BooleanField(_('depuis cache'), default=False)

    cree_le = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('log de traduction')
        ordering = ['-cree_le']
        indexes = [
            models.Index(fields=['user', 'cree_le']),
            models.Index(fields=['langue_cible', 'cree_le']),
        ]

    def __str__(self):
        return f'Traduction {self.langue_source}→{self.langue_cible} — {self.cree_le.date()}'


# ══════════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ══════════════════════════════════════════════════════════════════════════════

class Notification(models.Model):
    """Notifications sortantes multi-canal."""

    CANAL_SMS = 'SMS'
    CANAL_APP = 'APP'
    CANAL_EMAIL = 'EMAIL'

    CANAL_CHOICES = [
        (CANAL_SMS, 'SMS'),
        (CANAL_APP, 'In-App'),
        (CANAL_EMAIL, 'Email'),
    ]

    STATUT_EN_ATTENTE = 'EN_ATTENTE'
    STATUT_ENVOYE = 'ENVOYE'
    STATUT_ECHEC = 'ECHEC'
    STATUT_LU = 'LU'

    STATUT_CHOICES = [
        (STATUT_EN_ATTENTE, _('En attente')),
        (STATUT_ENVOYE, _('Envoyé')),
        (STATUT_ECHEC, _('Échec')),
        (STATUT_LU, _('Lu')),
    ]

    destinataire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications'
    )
    canal = models.CharField(_('canal'), max_length=10, choices=CANAL_CHOICES)
    titre = models.CharField(_('titre'), max_length=200, blank=True)
    contenu = models.TextField(_('contenu'))
    contenu_traduit = models.TextField(_('contenu traduit'), blank=True)
    langue_envoi = models.CharField(_('langue d\'envoi'), max_length=5, default='fr')
    statut = models.CharField(_('statut'), max_length=15, choices=STATUT_CHOICES, default=STATUT_EN_ATTENTE)
    erreur = models.TextField(_('message d\'erreur'), blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    envoye_le = models.DateTimeField(null=True, blank=True)
    lu_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('notification')
        ordering = ['-cree_le']
        indexes = [models.Index(fields=['destinataire', 'statut'])]

    def __str__(self):
        return f'Notif {self.canal} → {self.destinataire.nom_complet} — {self.statut}'
