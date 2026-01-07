from django.contrib import admin
from .models import CartItem

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('variant', 'quantity', 'user', 'session_key')
    list_filter = ('user',)
