from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'method', 'amount', 'status', 'created_at')
    list_filter = ('method', 'status', 'created_at')
    search_fields = ('order__order_number',)
    readonly_fields = ('order', 'method', 'amount', 'created_at')
