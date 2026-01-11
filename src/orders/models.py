from django.db import models
from django.conf import settings  # <-- important
from products.models import Variant
from coupons.models import Coupon



class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('shipped', 'Shipped'),
        ('cancelled', 'Cancelled'),
    )
    PAYMENT_CHOICES = (
        ('paypal', 'PayPal'),
        ('cash', 'Cash'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # <-- folosește CustomUser
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='cash')
    payment_status = models.CharField(max_length=10, choices=(('pending','Pending'), ('paid','Paid')), default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    coupon = models.ForeignKey(Coupon, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order_number} - {self.user.username if self.user else 'Guest'}"

    @property
    def total_after_discount(self):
        return max(self.total_amount - self.discount_amount, 0)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    variant = models.ForeignKey(Variant, on_delete=models.SET_NULL, null=True)
    price_at_purchase = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.variant} x {self.quantity}"

    @property
    def total_price(self):
        if self.price_at_purchase is not None:
            price = self.price_at_purchase
        else:
            # fallback: dacă price_at_purchase lipsă, folosim price_override sau base_price
            price = self.variant.price_override if self.variant and self.variant.price_override is not None else self.variant.product.base_price
        return price * self.quantity


class ShippingAddress(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='shipping_address')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.full_name} - {self.city}"
