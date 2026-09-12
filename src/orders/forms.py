from django import forms
from .models import ShippingAddress

class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = [
            'full_name', 'phone', 'address_line_1', 'address_line_2',
            'city', 'postal_code', 'country'
        ]
        widgets = {field: forms.TextInput(attrs={'class': 'form-control'}) for field in fields}
        labels = {'address_line_2': 'Address Line 2 (optional)'}
