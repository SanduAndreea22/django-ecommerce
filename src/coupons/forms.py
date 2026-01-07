from django import forms

class CouponApplyForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        label='Cod cupon',
        widget=forms.TextInput(attrs={'placeholder': 'Introdu codul cupon'})
    )
