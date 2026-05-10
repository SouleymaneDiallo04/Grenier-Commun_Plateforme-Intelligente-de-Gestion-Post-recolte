"""
Grenier Commun — Modèle Utilisateur Custom
Rôles : AGRICULTEUR, GESTIONNAIRE, ACHETEUR, IMF, ADMIN_GC
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('L\'adresse email est obligatoire'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.ADMIN_GC)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # ── Rôles ────────────────────────────────────────────────────────────────
    AGRICULTEUR = 'AGRICULTEUR'
    GESTIONNAIRE = 'GESTIONNAIRE'
    ACHETEUR = 'ACHETEUR'
    IMF = 'IMF'
    ADMIN_GC = 'ADMIN_GC'

    ROLE_CHOICES = [
        (AGRICULTEUR, _('Agriculteur')),
        (GESTIONNAIRE, _('Gestionnaire de Silo')),
        (ACHETEUR, _('Acheteur')),
        (IMF, _('Institution de Microfinance')),
        (ADMIN_GC, _('Administrateur Grenier Commun')),
    ]

    # ── Langues ──────────────────────────────────────────────────────────────
    LANGUE_FR = 'fr'
    LANGUE_EN = 'en'
    LANGUE_WO = 'wo'

    LANGUE_CHOICES = [
        (LANGUE_FR, 'Français'),
        (LANGUE_EN, 'English'),
        (LANGUE_WO, 'Wolof'),
    ]

    # ── Champs ───────────────────────────────────────────────────────────────
    email = models.EmailField(_('adresse email'), unique=True)
    telephone = PhoneNumberField(_('numéro de téléphone'), blank=True, null=True, unique=True)
    nom = models.CharField(_('nom'), max_length=100)
    prenom = models.CharField(_('prénom'), max_length=100)
    role = models.CharField(_('rôle'), max_length=20, choices=ROLE_CHOICES, default=AGRICULTEUR)
    langue_preferee = models.CharField(_('langue préférée'), max_length=5, choices=LANGUE_CHOICES, default=LANGUE_FR)

    # ── Multi-pays (architecture extensible) ─────────────────────────────────
    pays = models.CharField(_('pays'), max_length=50, default='Sénégal')
    region = models.CharField(_('région'), max_length=100, blank=True)

    # ── Statut ───────────────────────────────────────────────────────────────
    is_active = models.BooleanField(_('actif'), default=True)
    is_staff = models.BooleanField(_('staff'), default=False)
    is_verified = models.BooleanField(_('vérifié'), default=False)

    # ── Dates ────────────────────────────────────────────────────────────────
    date_joined = models.DateTimeField(_('date d\'inscription'), default=timezone.now)
    derniere_connexion = models.DateTimeField(_('dernière connexion'), null=True, blank=True)

    # ── Avatar ───────────────────────────────────────────────────────────────
    avatar = models.ImageField(_('avatar'), upload_to='avatars/', null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom', 'role']

    class Meta:
        verbose_name = _('utilisateur')
        verbose_name_plural = _('utilisateurs')
        ordering = ['-date_joined']

    def __str__(self):
        return f'{self.prenom} {self.nom} ({self.get_role_display()})'

    @property
    def nom_complet(self):
        return f'{self.prenom} {self.nom}'

    # ── Vérificateurs de rôle ────────────────────────────────────────────────
    @property
    def est_agriculteur(self):
        return self.role == self.AGRICULTEUR

    @property
    def est_gestionnaire(self):
        return self.role == self.GESTIONNAIRE

    @property
    def est_acheteur(self):
        return self.role == self.ACHETEUR

    @property
    def est_imf(self):
        return self.role == self.IMF

    @property
    def est_admin_gc(self):
        return self.role == self.ADMIN_GC

    def get_dashboard_url(self):
        """Retourne l'URL du dashboard selon le rôle."""
        from django.urls import reverse
        routes = {
            self.AGRICULTEUR: 'agriculteurs:dashboard',
            self.GESTIONNAIRE: 'silos:dashboard',
            self.ACHETEUR: 'marche:dashboard',
            self.IMF: 'imf:dashboard',
            self.ADMIN_GC: 'administration:dashboard',
        }
        return reverse(routes.get(self.role, 'core:accueil'))


class OTPCode(models.Model):
    """Codes OTP pour vérification par téléphone."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_codes')
    code = models.CharField(max_length=6)
    telephone = PhoneNumberField()
    est_utilise = models.BooleanField(default=False)
    cree_le = models.DateTimeField(auto_now_add=True)
    expire_le = models.DateTimeField()

    class Meta:
        ordering = ['-cree_le']

    def est_valide(self):
        from django.utils import timezone
        return not self.est_utilise and self.expire_le > timezone.now()

    def __str__(self):
        return f'OTP {self.code} pour {self.user.nom_complet}'
