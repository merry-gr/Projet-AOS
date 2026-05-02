from django.db import models

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('preparing', 'Preparing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Cash on Delivery'),
        ('card', 'Card'),
        ('transfer', 'Bank Transfer'),
    ]

    buyer_id = models.IntegerField()   # ✅ instead of FK
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    phone = models.CharField(max_length=20)
    delivery_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    delivery_note = models.TextField(blank=True, null=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')

    estimated_delivery = models.DateField(blank=True, null=True)
    vendor_note = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Order #{self.id} - User {self.buyer_id} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product_id = models.IntegerField()   # ✅ instead of FK
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Product {self.product_id} x {self.quantity}"