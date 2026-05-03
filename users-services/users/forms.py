from django import forms
from .models import VendorProfile, BuyerProfile

class VendorProfileForm(forms.ModelForm):
    class Meta:
        model = VendorProfile
        fields = ['company_name', 'phone', 'address', 'license_number'] # Ajouté ici

class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = ['company_name', 'phone', 'address', 'registration_number'] # Ajouté ici