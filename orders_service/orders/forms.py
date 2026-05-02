from django import forms
from .models import Order, OrderItem

class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['quantity']

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['phone', 'delivery_address', 'city', 'delivery_note', 'payment_method']

class VendorOrderUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['estimated_delivery', 'vendor_note']
        widgets = {
            'estimated_delivery': forms.DateInput(attrs={'type': 'date'})
        }