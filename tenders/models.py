# tenders/models.py
from django.db import models
from django.utils import timezone
import hashlib

class AppelOffre(models.Model):
    # Types d'avis
    TYPE_AVIS_CHOICES = [
        ('appel_offres', 'Appel d\'offres'),
        ('consultation', 'Consultation'),
        ('marché', 'Marché'),
        ('alerte', 'Alerte'),
        ('autre', 'Autre'),
    ]
    
    # Nature de l'avis
    NATURE_CHOICES = [
        ('services', 'Services'),
        ('travaux', 'Travaux'),
        ('fournitures', 'Fournitures'),
        ('mixtes', 'Mixtes'),
    ]
    
    # Statuts
    STATUT_CHOICES = [
        ('en_cours', 'Avis en cours'),
        ('cloture', 'Avis clôturé'),
        ('accepte', 'Avis accepté'),
        ('annule', 'Avis annulé'),
    ]
    
    # Départements français (exemples)
    DEPARTEMENT_CHOICES = [
        ('75', 'Paris'),
        ('13', 'Bouches-du-Rhône'),
        ('69', 'Rhône'),
        ('59', 'Nord'),
        ('33', 'Gironde'),
        ('31', 'Haute-Garonne'),
        ('06', 'Alpes-Maritimes'),
        ('44', 'Loire-Atlantique'),
        ('35', 'Ille-et-Vilaine'),
        ('67', 'Bas-Rhin'),
        # Ajoutez d'autres départements au besoin
    ]
    
    # Champs principaux
    titre = models.CharField(max_length=300, verbose_name="Nom de l'appel")
    numero = models.CharField(max_length=100, unique=True, verbose_name="Numéro de l'appel")
    
    # Informations essentielles
    description = models.TextField(verbose_name="Informations essentielles")
    acheteur = models.CharField(max_length=200, verbose_name="Nom de l'acheteur")
    acheteur_telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone de l'acheteur")
    acheteur_email = models.EmailField(blank=True, null=True, verbose_name="Email de l'acheteur")
    
    # Dates importantes
    date_parution = models.DateField(default=timezone.now, verbose_name="Date de parution")
    date_limite = models.DateField(verbose_name="Date limite de réponse")
    
    # Filtres
    departement = models.CharField(max_length=3, choices=DEPARTEMENT_CHOICES, verbose_name="Département")
    type_avis = models.CharField(max_length=50, choices=TYPE_AVIS_CHOICES, verbose_name="Type d'avis")
    nature = models.CharField(max_length=50, choices=NATURE_CHOICES, verbose_name="Nature")
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='en_cours', verbose_name="Statut")
    
    # Information sur la source
    site_source = models.CharField(max_length=100, verbose_name="Site source")
    url_originale = models.URLField(verbose_name="URL originale", blank=True, null=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    # Méthodes utiles
    def __str__(self):
        return f"{self.numero} - {self.titre}"
    
    def jours_restants(self):
        """Calcule les jours restants avant la date limite"""
        from datetime import date
        if self.date_limite:
            jours = (self.date_limite - date.today()).days
            return max(jours, 0)
        return None
    
    def est_urgent(self):
        """Détermine si l'appel est urgent (moins de 7 jours restants)"""
        jours = self.jours_restants()
        return jours is not None and jours < 7

        


    source_id = models.CharField(max_length=255, unique=True, verbose_name="ID Source")
    import_date = models.DateTimeField(auto_now_add=True, verbose_name="Date d'import")
    last_seen = models.DateTimeField(auto_now=True, verbose_name="Dernière vue")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Méthode pour générer un ID unique basé sur les données du scraping
    @classmethod
    def generate_source_id(cls, numero, site_source, date_parution):
        """Génère un ID unique pour éviter les doublons"""
        base_string = f"{numero}|{site_source}|{date_parution}"

        return hashlib.md5(base_string.encode()).hexdigest()
    
    class Meta:
        # Ajouter un index pour optimiser les recherches
        indexes = [
            models.Index(fields=['source_id']),
            models.Index(fields=['date_parution']),
            models.Index(fields=['site_source']),
        ]