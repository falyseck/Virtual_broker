from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime, timedelta
from cloudinary.models import CloudinaryField

# 1. Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('proprietaire', 'Propriétaire'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='user',
    )

    def __str__(self):
        return self.username


# 2. Annonce (Logement à louer ou vendre)


class Annonce(models.Model):
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    localisation = models.CharField(max_length=100)
    image = CloudinaryField('image', blank=True, null=True)
    date_postee = models.DateTimeField(auto_now_add=True) # to be changed to auto_now_add=True after migration

    def __str__(self):
        return self.titre



class RendezVous(models.Model):
    annonce = models.ForeignKey('Annonce', on_delete=models.CASCADE, verbose_name="Annonce concernée")
    client = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Client")
    date_rdv = models.DateTimeField(verbose_name="Date et heure")
    duree = models.PositiveIntegerField(
        default=30,
        validators=[MinValueValidator(15), MaxValueValidator(120)],
        verbose_name="Durée (minutes)"
    )
    client_phone = models.CharField("Téléphone du client", max_length=20, blank=True)
    client_name = models.CharField("Nom complet du client", max_length=100, blank=True)
    proprietaire_phone = models.CharField("Téléphone du propriétaire", max_length=20, blank=True)
    proprietaire_name = models.CharField("Nom du propriétaire", max_length=100, blank=True)
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
    ]
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default='en_attente',
        verbose_name="Statut"
    )
    notes = models.TextField(blank=True, verbose_name="Notes supplémentaires")

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['date_rdv']

    def __str__(self):
        return f"RDV #{self.id} - {self.annonce.titre} ({self.date_rdv.strftime('%d/%m/%Y %H:%M')})"