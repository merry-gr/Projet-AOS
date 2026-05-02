from django.db import models
from django.contrib.auth.models import AbstractUser

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

    def __str__(self):
        return self.username


class VendorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    address = models.TextField()

    def __str__(self):
        return self.user.username


class BuyerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    address = models.TextField()

    def __str__(self):
        return self.user.username