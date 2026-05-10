"""
Grenier Commun — Modèles Silos & Dépôts
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


class Commune(models.Model):
    """Commune sénégalaise rattachée à un ou plusieurs silos."""
    nom = models.CharField(_('nom'), max_length=150)
    region = models.CharField(_('région'), max_length=100)
    departement = models.CharField(_('département'), max_length=100, blank=True)
    pays = models.CharField(_('pays'), max_length=50, default='Sénégal')
    code_postal = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = _('commune')
        ordering = ['region', 'nom']

    def __str__(self):
        return f'{self.nom} ({self.region})'


class Silo(models.Model):
    """Silo physique géré par Grenier Commun."""

    STATUT_ACTIF = 'ACTIF'
    STATUT_MAINTENANCE = 'MAINTENANCE'
    STATUT_INACTIF = 'INACTIF'
    STATUT_PLEIN = 'PLEIN'

    STATUT_CHOICES = [
        (STATUT_ACTIF, _('Actif')),
        (STATUT_MAINTENANCE, _('En maintenance')),
        (STATUT_INACTIF, _('Inactif')),
        (STATUT_PLEIN, _('Capacité maximale atteinte')),
    ]

    SANTE_VERT = 'VERT'
    SANTE_ORANGE = 'ORANGE'
    SANTE_ROUGE = 'ROUGE'

    SANTE_CHOICES = [
        (SANTE_VERT, _('Optimal')),
        (SANTE_ORANGE, _('Surveillance requise')),
        (SANTE_ROUGE, _('Intervention urgente')),
    ]

    # ── Identification ────────────────────────────────────────────────────────
    nom = models.CharField(_('nom du silo'), max_length=150)
    code = models.CharField(_('code unique'), max_length=20, unique=True)
    commune = models.ForeignKey(Commune, on_delete=models.PROTECT, related_name='silos')
    gestionnaire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='silos_geres',
        limit_choices_to={'role': 'GESTIONNAIRE'}
    )

    # ── Localisation ─────────────────────────────────────────────────────────
    adresse = models.TextField(_('adresse'), blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # ── Capacité ─────────────────────────────────────────────────────────────
    capacite_kg = models.PositiveIntegerField(_('capacité (kg)'), validators=[MinValueValidator(1)])
    stock_actuel_kg = models.PositiveIntegerField(_('stock actuel (kg)'), default=0)

    # ── Conditions (saisie manuelle dans le MVP) ──────────────────────────────
    temperature_celsius = models.DecimalField(
        _('température (°C)'), max_digits=5, decimal_places=2, null=True, blank=True
    )
    humidite_pourcent = models.DecimalField(
        _('humidité (%)'), max_digits=5, decimal_places=2, null=True, blank=True
    )
    derniere_mesure = models.DateTimeField(_('dernière mesure'), null=True, blank=True)

    # ── Statut & Santé ────────────────────────────────────────────────────────
    statut = models.CharField(_('statut'), max_length=20, choices=STATUT_CHOICES, default=STATUT_ACTIF)
    sante = models.CharField(_('santé'), max_length=10, choices=SANTE_CHOICES, default=SANTE_VERT)

    # ── Dates ────────────────────────────────────────────────────────────────
    date_installation = models.DateField(_('date d\'installation'), null=True, blank=True)
    cree_le = models.DateTimeField(auto_now_add=True)
    modifie_le = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('silo')
        ordering = ['commune', 'nom']

    def __str__(self):
        return f'{self.nom} — {self.commune.nom}'

    @property
    def taux_remplissage(self):
        if self.capacite_kg == 0:
            return 0
        return round((self.stock_actuel_kg / self.capacite_kg) * 100, 1)

    @property
    def capacite_disponible_kg(self):
        return self.capacite_kg - self.stock_actuel_kg

    @property
    def est_plein(self):
        return self.stock_actuel_kg >= self.capacite_kg

    @property
    def nb_depots_actifs(self):
        return self.depots.filter(statut__in=['ACTIF', 'PARTIEL', 'WARRANTE']).count()


class Denree(models.Model):
    """Référentiel des denrées agricoles stockables."""
    nom = models.CharField(_('nom'), max_length=100, unique=True)
    nom_wolof = models.CharField(_('nom en wolof'), max_length=100, blank=True)
    nom_anglais = models.CharField(_('nom en anglais'), max_length=100, blank=True)

    # Paramètres optimaux de conservation
    temperature_min = models.DecimalField(max_digits=5, decimal_places=2, default=15)
    temperature_max = models.DecimalField(max_digits=5, decimal_places=2, default=30)
    humidite_max = models.DecimalField(max_digits=5, decimal_places=2, default=13)

    unite = models.CharField(_('unité'), max_length=20, default='kg')
    actif = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('denrée')
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Depot(models.Model):
    """Dépôt d'une récolte dans un silo — document central de la plateforme."""

    STATUT_ACTIF = 'ACTIF'
    STATUT_PARTIELLEMENT_RETIRE = 'PARTIEL'
    STATUT_RETIRE = 'RETIRE'
    STATUT_VENDU = 'VENDU'
    STATUT_WARRANTE = 'WARRANTE'

    STATUT_CHOICES = [
        (STATUT_ACTIF, _('En stock')),
        (STATUT_PARTIELLEMENT_RETIRE, _('Partiellement retiré')),
        (STATUT_RETIRE, _('Retiré')),
        (STATUT_VENDU, _('Vendu')),
        (STATUT_WARRANTE, _('Sous warrantage')),
    ]

    # ── Identification ────────────────────────────────────────────────────────
    numero_recu = models.CharField(_('numéro de reçu'), max_length=30, unique=True, editable=False)
    agriculteur = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name='depots', limit_choices_to={'role': 'AGRICULTEUR'}
    )
    silo = models.ForeignKey(Silo, on_delete=models.PROTECT, related_name='depots')
    gestionnaire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='depots_enregistres',
        limit_choices_to={'role': 'GESTIONNAIRE'}
    )

    # ── Denrée & Quantité ────────────────────────────────────────────────────
    denree = models.ForeignKey(Denree, on_delete=models.PROTECT, related_name='depots')
    quantite_initiale_kg = models.DecimalField(
        _('quantité initiale (kg)'), max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.1)]
    )
    quantite_disponible_kg = models.DecimalField(
        _('quantité disponible (kg)'), max_digits=10, decimal_places=2
    )

    # ── Valeur ───────────────────────────────────────────────────────────────
    prix_reference_fcfa = models.DecimalField(
        _('prix de référence (FCFA/kg)'), max_digits=10, decimal_places=2,
        null=True, blank=True
    )

    # ── Qualité ──────────────────────────────────────────────────────────────
    observations = models.TextField(_('observations'), blank=True)
    photo = models.ImageField(_('photo'), upload_to='depots/', null=True, blank=True)

    # ── Statut ───────────────────────────────────────────────────────────────
    statut = models.CharField(_('statut'), max_length=20, choices=STATUT_CHOICES, default=STATUT_ACTIF)

    # ── Dates ────────────────────────────────────────────────────────────────
    date_depot = models.DateTimeField(_('date de dépôt'), auto_now_add=True)
    date_expiration = models.DateField(_('date d\'expiration estimée'), null=True, blank=True)
    date_retrait_effectif = models.DateTimeField(null=True, blank=True)

    # ── Documents ────────────────────────────────────────────────────────────
    recu_pdf = models.FileField(_('reçu PDF'), upload_to='recus/', null=True, blank=True)

    class Meta:
        verbose_name = _('dépôt')
        ordering = ['-date_depot']

    def __str__(self):
        return f'Dépôt {self.numero_recu} — {self.agriculteur.nom_complet}'

    def save(self, *args, **kwargs):
        if not self.numero_recu:
            self.numero_recu = self._generer_numero_recu()
        if not self.quantite_disponible_kg:
            self.quantite_disponible_kg = self.quantite_initiale_kg
        super().save(*args, **kwargs)

    def _generer_numero_recu(self):
        from django.utils import timezone
        import random
        now = timezone.now()
        return f'GC-{now.strftime("%Y%m")}-{random.randint(10000, 99999)}'

    @property
    def valeur_estimee_fcfa(self):
        if self.prix_reference_fcfa:
            return float(self.quantite_disponible_kg) * float(self.prix_reference_fcfa)
        return None

    @property
    def montant_warrantable_fcfa(self):
        """70% de la valeur du stock — montant empruntable."""
        if self.valeur_estimee_fcfa:
            return self.valeur_estimee_fcfa * settings.GC_TAUX_WARRANTAGE
        return None


class Retrait(models.Model):
    """Retrait partiel ou total d'un dépôt."""

    TYPE_RETRAIT = 'RETRAIT'
    TYPE_VENTE = 'VENTE'

    TYPE_CHOICES = [
        (TYPE_RETRAIT, _('Retrait par l\'agriculteur')),
        (TYPE_VENTE, _('Vente via la plateforme')),
    ]

    depot = models.ForeignKey(Depot, on_delete=models.PROTECT, related_name='retraits')
    gestionnaire = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='retraits_enregistres'
    )
    quantite_kg = models.DecimalField(
        _('quantité retirée (kg)'), max_digits=10, decimal_places=2,
        validators=[MinValueValidator(0.1)]
    )
    type_retrait = models.CharField(_('type'), max_length=10, choices=TYPE_CHOICES, default=TYPE_RETRAIT)
    prix_vente_fcfa = models.DecimalField(
        _('prix de vente (FCFA/kg)'), max_digits=10, decimal_places=2,
        null=True, blank=True
    )
    observations = models.TextField(blank=True)
    bon_sortie_pdf = models.FileField(upload_to='bons_sortie/', null=True, blank=True)
    date_retrait = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('retrait')
        ordering = ['-date_retrait']

    def __str__(self):
        return f'Retrait {self.quantite_kg}kg — {self.depot.numero_recu}'


class AlerteSilo(models.Model):
    """Alertes de conservation générées par le système."""

    NIVEAU_VERT = 'VERT'
    NIVEAU_ORANGE = 'ORANGE'
    NIVEAU_ROUGE = 'ROUGE'

    NIVEAU_CHOICES = [
        (NIVEAU_VERT, _('Normal')),
        (NIVEAU_ORANGE, _('Surveillance')),
        (NIVEAU_ROUGE, _('Urgence')),
    ]

    TYPE_TEMPERATURE = 'TEMPERATURE'
    TYPE_HUMIDITE = 'HUMIDITE'
    TYPE_RONGEUR = 'RONGEUR'
    TYPE_REMPLISSAGE = 'REMPLISSAGE'
    TYPE_AUTRE = 'AUTRE'

    TYPE_CHOICES = [
        (TYPE_TEMPERATURE, _('Température anormale')),
        (TYPE_HUMIDITE, _('Humidité excessive')),
        (TYPE_RONGEUR, _('Présence de rongeurs')),
        (TYPE_REMPLISSAGE, _('Capacité maximale atteinte')),
        (TYPE_AUTRE, _('Autre anomalie')),
    ]

    silo = models.ForeignKey(Silo, on_delete=models.CASCADE, related_name='alertes')
    type_alerte = models.CharField(_('type'), max_length=20, choices=TYPE_CHOICES)
    niveau = models.CharField(_('niveau'), max_length=10, choices=NIVEAU_CHOICES)
    message = models.TextField(_('message'))
    valeur_mesuree = models.CharField(_('valeur mesurée'), max_length=50, blank=True)
    valeur_seuil = models.CharField(_('valeur seuil'), max_length=50, blank=True)

    est_acquittee = models.BooleanField(_('acquittée'), default=False)
    acquittee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='alertes_acquittees'
    )
    commentaire_acquittement = models.TextField(blank=True)

    cree_le = models.DateTimeField(auto_now_add=True)
    acquittee_le = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = _('alerte silo')
        ordering = ['-cree_le']

    def __str__(self):
        return f'Alerte {self.niveau} — {self.silo.nom} — {self.get_type_alerte_display()}'
