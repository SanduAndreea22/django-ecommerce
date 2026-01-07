from django.contrib import admin
from .models import Order, OrderItem, ShippingAddress


# =========================
# INLINE
# =========================

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'variant',
        'price_at_purchase',
        'quantity',
        'total_price',
    )

    def total_price(self, obj):
        return obj.total_price
    total_price.short_description = 'Total'


class ShippingAddressInline(admin.StackedInline):
    model = ShippingAddress
    extra = 0
    can_delete = False
    readonly_fields = (
        'full_name',
        'phone',
        'address_line_1',
        'address_line_2',
        'city',
        'postal_code',
        'country',
    )


# =========================
# ORDER ADMIN
# =========================

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'status',
        'payment_method',
        'payment_status',
        'total_after_discount',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_method',
        'payment_status',
        'created_at',
    )

    search_fields = (
        'order_number',
        'user__username',
        'user__email',
    )

    date_hierarchy = 'created_at'

    readonly_fields = (
        'order_number',
        'user',
        'total_amount',
        'discount_amount',
        'coupon',
        'created_at',
        'total_after_discount',
    )

    fieldsets = (
        ('Order Info', {
            'fields': (
                'order_number',
                'user',
                'created_at',
            )
        }),
        ('Status', {
            'fields': (
                'status',
                'payment_method',
                'payment_status',
            )
        }),
        ('Totals', {
            'fields': (
                'total_amount',
                'discount_amount',
                'total_after_discount',
                'coupon',
            )
        }),
    )

    inlines = [OrderItemInline, ShippingAddressInline]

    actions = ['mark_as_paid', 'mark_as_shipped', 'mark_as_cancelled']

    # =========================
    # ADMIN ACTIONS
    # =========================

    @admin.action(description='Mark selected orders as PAID')
    def mark_as_paid(self, request, queryset):
        queryset.update(payment_status='paid', status='paid')

    @admin.action(description='Mark selected orders as SHIPPED')
    def mark_as_shipped(self, request, queryset):
        queryset.update(status='shipped')

    @admin.action(description='Cancel selected orders')
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')


