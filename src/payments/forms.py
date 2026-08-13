from django import forms

from .services import stripe_enabled


class PaymentMethodForm(forms.Form):
    METHOD_CHOICES = (
        ('cash', 'Cash on delivery'),
        ('stripe', 'Card'),
    )
    method = forms.ChoiceField(choices=METHOD_CHOICES, widget=forms.RadioSelect, initial='cash')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not stripe_enabled():
            self.fields['method'].choices = [
                choice for choice in self.METHOD_CHOICES if choice[0] != 'stripe'
            ]
