from django.conf import settings


def stripe_enabled():
    """Cardul cu Stripe e disponibil doar dacă cheile de test mode sunt configurate."""
    return bool(settings.STRIPE_SECRET_KEY and settings.STRIPE_PUBLISHABLE_KEY)
