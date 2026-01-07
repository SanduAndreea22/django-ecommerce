from django.contrib import admin
from .models import CartItem


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'session_key',
        'variant',
        'quantity',
        'added_at',
    )

    list_filter = (
        'added_at',
    )

    search_fields = (
        'user__username',
        'session_key',
        'variant__product__name',
        'variant__sku',
    )

    readonly_fields = (
        'user',
        'session_key',
        'variant',
        'quantity',
        'added_at',
    )

    ordering = ('-added_at',)
