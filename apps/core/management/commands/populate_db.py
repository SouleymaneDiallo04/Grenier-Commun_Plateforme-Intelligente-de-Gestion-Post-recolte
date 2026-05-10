"""
Grenier Commun — Commande de population de la base de données (développement).
Usage : py manage.py populate_db
"""
from decimal import Decimal
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Popule la base de données avec des données de démonstration'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('=== Population de la base de données ==='))
        self._create_communes()
        self._create_denrees()
        self._create_users()
        self._create_imf()
        self._create_silos()
        self._create_profils()
        self._create_depots()
        self._create_prix_marche()
        self._create_recommandations()
        self._create_alertes()
        self._create_warrantages()
        self._create_offres()
        self._create_notifications()
        self.stdout.write(self.style.SUCCESS('\n✓ Base de données populée avec succès !'))
        self.stdout.write('')
        self.stdout.write('  Comptes disponibles (mot de passe : Password123!)')
        self.stdout.write('  ─────────────────────────────────────────────────')
        self.stdout.write('  admin@gc.sn            → Admin GC')
        self.stdout.write('  gestionnaire1@gc.sn    → Gestionnaire Silo Kaolack')
        self.stdout.write('  gestionnaire2@gc.sn    → Gestionnaire Silo Thies')
        self.stdout.write('  gestionnaire3@gc.sn    → Gestionnaire Silo Saint-Louis')
        self.stdout.write('  gestionnaire4@gc.sn    → Gestionnaire Silo Fatick')
        self.stdout.write('  gestionnaire5@gc.sn    → Gestionnaire Silo Kaffrine')
        self.stdout.write('  agriculteur1@gc.sn     → Agriculteur')
        self.stdout.write('  agriculteur2@gc.sn     → Agriculteur')
        self.stdout.write('  agriculteur3@gc.sn     → Agriculteur')
        self.stdout.write('  acheteur@gc.sn         → Acheteur')
        self.stdout.write('  imf@gc.sn              → Institution de Microfinance')

    # ─── Communes ─────────────────────────────────────────────────────────────
    def _create_communes(self):
        from apps.silos.models import Commune
        data = [
            ('Kaolack',        'Kaolack',        'Kaolack'),
            ('Thiès',          'Thiès',           'Thiès'),
            ('Dakar',          'Dakar',           'Dakar'),
            ('Saint-Louis',    'Saint-Louis',     'Saint-Louis'),
            ('Ziguinchor',     'Ziguinchor',      'Ziguinchor'),
            ('Louga',          'Louga',           'Louga'),
            ('Fatick',         'Fatick',          'Fatick'),
            ('Tambacounda',    'Tambacounda',     'Tambacounda'),
            ('Kaffrine',       'Kaffrine',        'Kaffrine'),
            ('Kolda',          'Kolda',           'Kolda'),
        ]
        created = 0
        for nom, region, dept in data:
            _, ok = Commune.objects.get_or_create(
                nom=nom, defaults={'region': region, 'departement': dept}
            )
            if ok:
                created += 1
        self.stdout.write(f'  communes        : {Commune.objects.count()} ({created} nouvelles)')

    # ─── Denrées ──────────────────────────────────────────────────────────────
    def _create_denrees(self):
        from apps.silos.models import Denree
        data = [
            ('Mil',        'Gero',          'Millet',    15, 30, 13),
            ('Sorgho',     'Gawri',         'Sorghum',   15, 30, 13),
            ('Maïs',       'Mbas',          'Corn',      10, 28, 14),
            ('Arachide',   'Gerte',         'Groundnut', 15, 25,  9),
            ('Riz paddy',  'Tiep bu dëkk',  'Paddy rice',10, 28, 14),
            ('Niébé',      'Nebe',          'Cowpea',    15, 30, 12),
            ('Fonio',      'Foni',          'Fonio',     15, 28, 12),
        ]
        created = 0
        for nom, wolof, anglais, t_min, t_max, h_max in data:
            _, ok = Denree.objects.get_or_create(
                nom=nom,
                defaults={
                    'nom_wolof': wolof, 'nom_anglais': anglais,
                    'temperature_min': t_min, 'temperature_max': t_max,
                    'humidite_max': h_max,
                }
            )
            if ok:
                created += 1
        self.stdout.write(f'  denrees         : {Denree.objects.count()} ({created} nouvelles)')

    # ─── Utilisateurs ─────────────────────────────────────────────────────────
    def _create_users(self):
        data = [
            ('admin@gc.sn',         'Admin',     'GC',       'ADMIN_GC',     True,  True),
            ('gestionnaire1@gc.sn', 'Moussa',    'Diallo',   'GESTIONNAIRE', False, False),
            ('gestionnaire2@gc.sn', 'Ousmane',   'Fall',     'GESTIONNAIRE', False, False),
            ('gestionnaire3@gc.sn', 'Aissatou',  'Mbaye',    'GESTIONNAIRE', False, False),
            ('gestionnaire4@gc.sn', 'Cheikh',    'Gueye',    'GESTIONNAIRE', False, False),
            ('gestionnaire5@gc.sn', 'Rokhaya',   'Sarr',     'GESTIONNAIRE', False, False),
            ('agriculteur1@gc.sn',  'Amadou',    'Ndiaye',   'AGRICULTEUR',  False, False),
            ('agriculteur2@gc.sn',  'Fatou',     'Sow',      'AGRICULTEUR',  False, False),
            ('agriculteur3@gc.sn',  'Ibrahima',  'Diop',     'AGRICULTEUR',  False, False),
            ('acheteur@gc.sn',      'Jean',      'Dupont',   'ACHETEUR',     False, False),
            ('imf@gc.sn',           'Ali',       'Ba',       'IMF',          False, False),
        ]
        created = 0
        for email, prenom, nom, role, is_staff, is_super in data:
            if not User.objects.filter(email=email).exists():
                User.objects.create_user(
                    email=email, password='Password123!',
                    prenom=prenom, nom=nom, role=role,
                    is_staff=is_staff, is_superuser=is_super,
                    is_verified=True,
                )
                created += 1
        self.stdout.write(f'  utilisateurs    : {User.objects.count()} ({created} nouveaux)')

    # ─── IMF Partenaires ──────────────────────────────────────────────────────
    def _create_imf(self):
        from apps.core.models import IMFPartenaire
        data = [
            ('Caisse Nationale de Crédit Agricole du Sénégal', 'CNCAS',   'Ali Diallo',  'ali.diallo@cncas.sn',   '+221338210000', 2.0, 7),
            ('Partenariat Mobilisation Épargne Crédit Sénégal', 'PAMECAS', 'Ndeye Thiaw', 'n.thiaw@pamecas.sn',    '+221338220000', 2.5, 5),
            ('Crédit Mutuel du Sénégal',                        'CMS',     'Omar Faye',   'o.faye@cms.sn',         '+221338230000', 1.8, 10),
        ]
        created = 0
        for nom, sigle, contact, email, tel, taux, delai in data:
            _, ok = IMFPartenaire.objects.get_or_create(
                sigle=sigle,
                defaults={
                    'nom': nom, 'contact_nom': contact, 'contact_email': email,
                    'contact_telephone': tel, 'taux_interet_mensuel': taux,
                    'delai_traitement_jours': delai,
                }
            )
            if ok:
                created += 1
        self.stdout.write(f'  IMF             : {IMFPartenaire.objects.count()} ({created} nouvelles)')

    # ─── Silos ────────────────────────────────────────────────────────────────
    def _create_silos(self):
        from apps.silos.models import Commune, Silo
        # Un gestionnaire distinct par silo
        data = [
            ('Silo Kaolack Centre', 'SIL-KLK-001', 'Kaolack',     50000, 22000, 28.5, 12.0, 'VERT',   'ACTIF',       'gestionnaire1@gc.sn'),
            ('Silo Thiès Nord',     'SIL-THS-001', 'Thiès',        30000, 18000, 27.0, 11.5, 'VERT',   'ACTIF',       'gestionnaire2@gc.sn'),
            ('Silo Saint-Louis',    'SIL-STL-001', 'Saint-Louis',  40000,  5000, 31.0, 15.0, 'ORANGE', 'ACTIF',       'gestionnaire3@gc.sn'),
            ('Silo Fatick',         'SIL-FTC-001', 'Fatick',       25000, 20000, 26.5, 12.5, 'VERT',   'ACTIF',       'gestionnaire4@gc.sn'),
            ('Silo Kaffrine',       'SIL-KFF-001', 'Kaffrine',     35000,     0, 29.0, 13.0, 'ORANGE', 'MAINTENANCE', 'gestionnaire5@gc.sn'),
        ]
        created = 0
        for nom, code, ville, capacite, stock, temp, hum, sante, statut, gest_email in data:
            commune = Commune.objects.filter(nom=ville).first()
            gestionnaire = User.objects.filter(email=gest_email).first()
            if not commune or not gestionnaire:
                continue
            _, ok = Silo.objects.get_or_create(
                code=code,
                defaults={
                    'nom': nom, 'commune': commune, 'gestionnaire': gestionnaire,
                    'capacite_kg': capacite, 'stock_actuel_kg': stock,
                    'temperature_celsius': temp, 'humidite_pourcent': hum,
                    'sante': sante, 'statut': statut,
                    'date_installation': date(2022, 1, 15),
                    'derniere_mesure': timezone.now(),
                }
            )
            if ok:
                created += 1
        self.stdout.write(f'  silos           : {Silo.objects.count()} ({created} nouveaux)')

    # ─── Profils Agriculteurs ─────────────────────────────────────────────────
    def _create_profils(self):
        from apps.core.models import ProfilAgriculteur
        from apps.silos.models import Commune, Denree
        agriculteurs = User.objects.filter(role='AGRICULTEUR')
        profils_data = [
            ('Kaolack', 'Kahone',  5.5, 78),
            ('Thiès',   'Pout',    3.2, 55),
            ('Fatick',  'Gossas',  8.0, 42),
        ]
        denrees = list(Denree.objects.all()[:3])
        created = 0
        for i, user in enumerate(agriculteurs):
            if ProfilAgriculteur.objects.filter(user=user).exists():
                continue
            ville, village, superficie, score = profils_data[i % len(profils_data)]
            commune = Commune.objects.filter(nom=ville).first()
            profil = ProfilAgriculteur.objects.create(
                user=user, commune=commune, village=village,
                superficie_ha=superficie, score_credit=score,
                numero_agriculteur=f'AGR-2024-{i+1:04d}',
                score_calcule_le=timezone.now(),
            )
            if denrees:
                profil.cultures_principales.set(denrees[:2])
            created += 1
        self.stdout.write(f'  profils agr.    : {ProfilAgriculteur.objects.count()} ({created} nouveaux)')

    # ─── Dépôts ───────────────────────────────────────────────────────────────
    def _create_depots(self):
        from apps.silos.models import Silo, Denree, Depot
        agriculteurs = list(User.objects.filter(role='AGRICULTEUR'))
        silos = list(Silo.objects.filter(statut='ACTIF'))
        denrees = list(Denree.objects.all())
        if not (agriculteurs and silos and denrees):
            return
        today = date.today()
        # (agr_idx, silo_idx, denree_idx, qte_kg, prix_fcfa, statut)
        configs = [
            (0, 0, 0, 2000,  195, 'ACTIF'),
            (0, 1, 1, 1500,  220, 'ACTIF'),
            (1, 0, 2, 3000,  175, 'ACTIF'),
            (1, 1, 3,  800,  310, 'WARRANTE'),
            (2, 0, 4, 5000,  240, 'ACTIF'),
            (2, 2, 0, 1200,  185, 'PARTIEL'),
            (0, 0, 2, 4000,  270, 'ACTIF'),
            (1, 1, 4, 2500,  255, 'ACTIF'),
        ]
        created = 0
        for agr_i, silo_i, den_i, qte, prix, statut in configs:
            agr   = agriculteurs[agr_i % len(agriculteurs)]
            silo  = silos[silo_i % len(silos)]
            denree = denrees[den_i % len(denrees)]
            if Depot.objects.filter(agriculteur=agr, silo=silo, denree=denree,
                                    quantite_initiale_kg=qte).exists():
                continue
            qte_dispo = qte if statut == 'ACTIF' else int(qte * 0.6)
            Depot.objects.create(
                agriculteur=agr, silo=silo, denree=denree,
                gestionnaire=silo.gestionnaire,
                quantite_initiale_kg=Decimal(str(qte)),
                quantite_disponible_kg=Decimal(str(qte_dispo)),
                prix_reference_fcfa=Decimal(str(prix)),
                statut=statut,
                date_expiration=today + timedelta(days=120),
            )
            created += 1
        from apps.silos.models import Depot as D
        self.stdout.write(f'  dépôts          : {D.objects.count()} ({created} nouveaux)')

    # ─── Prix de marché ───────────────────────────────────────────────────────
    def _create_prix_marche(self):
        from apps.core.models import PrixMarche
        from apps.silos.models import Denree
        today = date.today()
        semaine = today.isocalendar()[1]
        annee   = today.year
        # {denree: [(region, prix, min, max)]}
        data = {
            'Mil':       [('Kaolack', 180, 160, 200), ('Thiès',  185, 165, 205), ('National', 182, 160, 205)],
            'Sorgho':    [('Kaolack', 165, 150, 180), ('Thiès',  170, 155, 185), ('National', 167, 150, 185)],
            'Maïs':      [('Kaolack', 200, 180, 220), ('Thiès',  210, 190, 230), ('National', 205, 180, 230)],
            'Arachide':  [('Kaolack', 350, 320, 380), ('Fatick', 360, 330, 390), ('National', 355, 320, 390)],
            'Riz paddy': [('Saint-Louis', 250, 230, 270), ('Kaolack', 260, 240, 280), ('National', 255, 230, 280)],
            'Niébé':     [('Kaolack', 420, 390, 450), ('National', 415, 390, 450)],
            'Fonio':     [('Kaolack', 380, 350, 420), ('National', 375, 350, 420)],
        }
        created = 0
        for denree_nom, prix_list in data.items():
            denree = Denree.objects.filter(nom=denree_nom).first()
            if not denree:
                continue
            for region, prix, p_min, p_max in prix_list:
                _, ok = PrixMarche.objects.get_or_create(
                    denree=denree, region=region, annee=annee, semaine=semaine,
                    defaults={
                        'prix_kg_fcfa': Decimal(str(prix)),
                        'prix_min_fcfa': Decimal(str(p_min)),
                        'prix_max_fcfa': Decimal(str(p_max)),
                    }
                )
                if ok:
                    created += 1
        self.stdout.write(f'  prix marché     : {PrixMarche.objects.count()} ({created} nouveaux)')

    # ─── Recommandations ──────────────────────────────────────────────────────
    def _create_recommandations(self):
        from apps.core.models import RecommandationVente
        from apps.silos.models import Denree
        today = date.today()
        data = [
            ('Mil',      'VENDRE',  'Les prix du mil sont au plus haut depuis 6 mois. Moment idéal pour vendre.',        182, 178, 175),
            ('Maïs',     'ATTENDRE','Le marché du maïs est orienté à la hausse. Attendez 4 à 8 semaines.',               205, 215, 225),
            ('Arachide', 'PARTIEL', 'Vendez 50 % de votre stock maintenant et conservez le reste jusqu\'en octobre.',    355, 360, 375),
        ]
        created = 0
        for denree_nom, action, message, p_actuel, p_4sem, p_8sem in data:
            denree = Denree.objects.filter(nom=denree_nom).first()
            if not denree or RecommandationVente.objects.filter(denree=denree).exists():
                continue
            RecommandationVente.objects.create(
                denree=denree, action_recommandee=action,
                message_fr=message,
                message_en=f'[EN] {message}',
                prix_actuel_fcfa=Decimal(str(p_actuel)),
                prix_prevu_4sem_fcfa=Decimal(str(p_4sem)),
                prix_prevu_8sem_fcfa=Decimal(str(p_8sem)),
                validee_par_admin=True,
                valide_jusqu_au=today + timedelta(days=7),
            )
            created += 1
        self.stdout.write(f'  recommandations : {RecommandationVente.objects.count()} ({created} nouvelles)')

    # ─── Alertes silos ────────────────────────────────────────────────────────
    def _create_alertes(self):
        from apps.silos.models import Silo, AlerteSilo
        data = [
            ('SIL-STL-001', 'TEMPERATURE', 'ORANGE',
             'Température de 31°C — seuil optimal dépassé pour le riz paddy. Vérifier la ventilation.',
             '31.0°C', '28.0°C'),
            ('SIL-KFF-001', 'HUMIDITE', 'ROUGE',
             'Humidité critique à 18,5 %. Risque de moisissures. Intervention urgente requise.',
             '18.5 %', '14.0 %'),
            ('SIL-KLK-001', 'REMPLISSAGE', 'ORANGE',
             'Silo à 88 % de sa capacité. Planifier les retraits ou suspendre les nouveaux dépôts.',
             '88 %', '85 %'),
        ]
        created = 0
        for code, type_a, niveau, msg, val, seuil in data:
            silo = Silo.objects.filter(code=code).first()
            if not silo or AlerteSilo.objects.filter(silo=silo, type_alerte=type_a).exists():
                continue
            AlerteSilo.objects.create(
                silo=silo, type_alerte=type_a, niveau=niveau,
                message=msg, valeur_mesuree=val, valeur_seuil=seuil,
            )
            created += 1
        self.stdout.write(f'  alertes silos   : {AlerteSilo.objects.count()} ({created} nouvelles)')

    # ─── Warrantages ──────────────────────────────────────────────────────────
    def _create_warrantages(self):
        from apps.core.models import WarrantageCredit, IMFPartenaire
        from apps.silos.models import Depot
        cncas = IMFPartenaire.objects.filter(sigle='CNCAS').first()
        today = date.today()
        # Dépôts actifs → demandes dans différents états
        depots_actifs = list(Depot.objects.filter(statut='ACTIF')[:3])
        depot_warrante = Depot.objects.filter(statut='WARRANTE').first()
        statuts = [
            ('SOUMIS',         None,  None),
            ('EN_INSTRUCTION', cncas, None),
            ('APPROUVE',       cncas, True),
        ]
        created = 0
        for i, depot in enumerate(depots_actifs):
            if WarrantageCredit.objects.filter(depot=depot).exists():
                continue
            statut, imf, accorde = statuts[i]
            valeur  = float(depot.quantite_disponible_kg) * float(depot.prix_reference_fcfa)
            montant = round(valeur * 0.70 / 1000) * 1000
            WarrantageCredit.objects.create(
                depot=depot,
                agriculteur=depot.agriculteur,
                imf=imf,
                montant_demande_fcfa=Decimal(str(montant)),
                montant_accorde_fcfa=Decimal(str(montant)) if accorde else None,
                taux_interet_mensuel=Decimal('2.0') if accorde else None,
                duree_mois=3,
                score_credit_snapshot=78 - i * 12,
                statut=statut,
                mode_paiement='Wave',
                date_echeance=today + timedelta(days=90) if accorde else None,
            )
            created += 1
        # Dépôt warranté → crédit remboursé
        if depot_warrante and not WarrantageCredit.objects.filter(depot=depot_warrante).exists():
            valeur  = float(depot_warrante.quantite_disponible_kg) * float(depot_warrante.prix_reference_fcfa)
            montant = round(valeur * 0.70 / 1000) * 1000
            WarrantageCredit.objects.create(
                depot=depot_warrante,
                agriculteur=depot_warrante.agriculteur,
                imf=cncas,
                montant_demande_fcfa=Decimal(str(montant)),
                montant_accorde_fcfa=Decimal(str(montant)),
                taux_interet_mensuel=Decimal('2.0'),
                duree_mois=3,
                score_credit_snapshot=65,
                statut='REMBOURSE',
                mode_paiement='Orange Money',
            )
            created += 1
        self.stdout.write(f'  warrantages     : {WarrantageCredit.objects.count()} ({created} nouveaux)')

    # ─── Offres d'achat ───────────────────────────────────────────────────────
    def _create_offres(self):
        from apps.core.models import OffreAchat
        from apps.silos.models import Denree
        acheteur = User.objects.filter(email='acheteur@gc.sn').first()
        if not acheteur:
            return
        denrees = list(Denree.objects.all())
        configs = [
            (0, 2000, 190, 'Kaolack', 30, 'SOUMISE',    'Bonne qualité requise, livraison à Kaolack'),
            (1, 1500, 170, 'Thiès',   20, 'SOUMISE',    ''),
            (2, 5000, 210, '',        45, 'ACCEPTEE',   'Livraison en plusieurs fois possible'),
            (3,  800, 360, 'Kaolack', 15, 'FINALISEE',  ''),
            (0, 3000, 185, 'Fatick',  60, 'SOUMISE',    'Qualité standard acceptée'),
        ]
        created = 0
        for den_i, qte, prix, region, delai, statut, notes in configs:
            denree = denrees[den_i % len(denrees)]
            if OffreAchat.objects.filter(acheteur=acheteur, denree=denree, quantite_kg=qte).exists():
                continue
            OffreAchat.objects.create(
                acheteur=acheteur, denree=denree,
                quantite_kg=Decimal(str(qte)),
                prix_propose_fcfa=Decimal(str(prix)),
                region_preferee=region,
                delai_souhaite_jours=delai,
                statut=statut, notes=notes,
            )
            created += 1
        self.stdout.write(f'  offres achat    : {OffreAchat.objects.count()} ({created} nouvelles)')

    # ─── Notifications ────────────────────────────────────────────────────────
    def _create_notifications(self):
        from apps.core.models import Notification
        agriculteurs = list(User.objects.filter(role='AGRICULTEUR'))
        if not agriculteurs:
            return
        data = [
            ('Dépôt enregistré',
             'Votre dépôt de 2 000 kg de Mil a bien été enregistré. Reçu disponible dans vos stocks.',
             'APP', 'LU'),
            ('',
             'Rappel : votre dépôt expire dans 30 jours. Planifiez votre retrait dès maintenant.',
             'APP', 'EN_ATTENTE'),
            ('Crédit approuvé',
             'Votre demande de warrantage de 245 000 FCFA a été approuvée par la CNCAS.',
             'APP', 'LU'),
            ('Recommandation de vente',
             'Le prix du Maïs est favorable cette semaine (210 FCFA/kg). Consultez vos recommandations.',
             'APP', 'EN_ATTENTE'),
            ('Alerte conservation',
             'Température élevée détectée dans le Silo Saint-Louis. Vérification en cours.',
             'APP', 'ENVOYE'),
        ]
        created = 0
        for i, (titre, contenu, canal, statut) in enumerate(data):
            agr = agriculteurs[i % len(agriculteurs)]
            if Notification.objects.filter(destinataire=agr, contenu=contenu).exists():
                continue
            Notification.objects.create(
                destinataire=agr, canal=canal,
                titre=titre, contenu=contenu, statut=statut,
            )
            created += 1
        self.stdout.write(f'  notifications   : {Notification.objects.count()} ({created} nouvelles)')
