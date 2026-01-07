from django import forms

class PaymentMethodForm(forms.Form):
    METHOD_CHOICES = (
        ('cash', 'Cash / Ramburs'),
    )
    method = forms.ChoiceField(choices=METHOD_CHOICES, widget=forms.RadioSelect, initial='cash')
