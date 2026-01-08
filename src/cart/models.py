from django.db import models
from django.conf import settings
from products.models import Variant

class CartItem(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )
    variant = models.ForeignKey(
        Variant,
        on_delete=models.CASCADE
    )
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'session_key', 'variant')

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

