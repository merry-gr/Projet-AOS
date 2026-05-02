from django.db import models

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('medicament', 'Médicament'),
        ('materiel_medical', 'Matériel médical'),
        ('equipement_lourd', 'Équipement lourd'),
        ('consommable', 'Consommable médical'),
        ('diagnostic', 'Diagnostic'),
        ('mobilier', 'Mobilier médical'),
        ('laboratoire', 'Laboratoire'),
        ('protection', 'Protection / Hygiène'),
        ('implant', 'Implants / Chirurgie'),
        ('other', 'Autre'),
    ]

    vendor_id = models.IntegerField()  # ✅ instead of FK
    name = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    image = models.ImageField(upload_to='products/')
    image2 = models.ImageField(upload_to='products/', blank=True, null=True)
    image3 = models.ImageField(upload_to='products/', blank=True, null=True)
    image4 = models.ImageField(upload_to='products/', blank=True, null=True)

    def __str__(self):
        return self.name