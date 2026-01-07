from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone_number', 'default_shipping_address']
        widgets = {
            'phone_number': forms.TextInput(attrs={'placeholder': 'Enter your phone number'}),
            'default_shipping_address': forms.TextInput(attrs={'placeholder': 'Enter your shipping address'}),
        }
