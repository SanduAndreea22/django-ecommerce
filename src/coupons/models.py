from django.db import models
from django.utils import timezone

class Coupon(models.Model):
    DISCOUNT_TYPE = (
        ('percent', 'Percent'),
        ('fixed', 'Fixed amount'),
    )

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE, default='percent')
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_uses = models.PositiveIntegerField(null=True, blank=True)  # None = nelimitat
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()


    class Meta:
         ordering = ['-valid_from']

    def __str__(self):
        return f"{self.code} ({self.discount_type} - {self.discount_value})"

    def is_valid(self, order_total=None):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_from > now or self.valid_to < now:
            return False
        if self.max_uses is not None and self.used_count >= self.max_uses:
            return False
        if order_total is not None and order_total < self.min_order_value:
            return False
        return True

    def calculate_discount(self, order_total):
        if not self.is_valid(order_total):
            return 0
        if self.discount_type == 'percent':
            return round(order_total * (self.discount_value / 100), 2)
        elif self.discount_type == 'fixed':
            return min(self.discount_value, order_total)
        return 0

    def increment_usage(self):
        self.used_count += 1
        self.save()



