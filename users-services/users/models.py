from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('vendeur', 'Vendeur'),
        ('acheteur', 'Acheteur'),
    )

    VALIDATION_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('refused', 'Refused'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='acheteur')
    validation_status = models.CharField(max_length=20, choices=VALIDATION_CHOICES, default='pending')
    rejection_reason = models.TextField(blank=True, null=True, verbose_name="Motif du refus")

    def __str__(self):
        return self.username

class VendorProfile(models.Model):
    # Utilisation de related_name pour faciliter l'accès depuis l'objet User
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor_profile')
    company_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    license_number = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"Profil Vendeur de {self.user.username}"

class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    company_name = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    buyer_type = models.CharField(max_length=64, blank=True, null=True)
    registration_number = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return f"Profil Acheteur de {self.user.username}"

# --- SIGNALS POUR CRÉATION AUTOMATIQUE ---
# Ce code s'exécute automatiquement après chaque création d'utilisateur

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'vendeur':
            VendorProfile.objects.create(user=instance)
        elif instance.role == 'acheteur':
            BuyerProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'vendeur' and hasattr(instance, 'vendor_profile'):
        instance.vendor_profile.save()
    elif instance.role == 'acheteur' and hasattr(instance, 'buyer_profile'):
        instance.buyer_profile.save()