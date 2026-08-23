from django import forms
from .models import Review, NewsletterSubscriber


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(
        choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(5, 0, -1)],
        widget=forms.RadioSelect,
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share what you thought about this product (optional)'}),
        }


class NewsletterSubscribeForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'you@example.com'}),
        }
