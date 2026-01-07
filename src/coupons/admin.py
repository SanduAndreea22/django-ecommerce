from django.contrib import admin
from .models import Coupon


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'discount_type',
        'discount_value',
        'min_order_value',
        'used_count',
        'max_uses',
        'is_active',
        'valid_from',
        'valid_to',
    )

    list_filter = (
        'discount_type',
        'is_active',
        'valid_from',
        'valid_to',
    )

    search_fields = (
        'code',
    )

    readonly_fields = (
        'used_count',
    )

    fieldsets = (
        ('Coupon Code', {
            'fields': ('code',)
        }),
        ('Discount', {
            'fields': (
                'discount_type',
                'discount_value',
                'min_order_value',
            )
        }),
        ('Usage Limits', {
            'fields': (
                'max_uses',
                'used_count',
            )
        }),
        ('Validity', {
            'fields': (
                'is_active',
                'valid_from',
                'valid_to',
            )
        }),
    )

    actions = ['activate_coupons', 'deactivate_coupons']

    @admin.action(description='Activate selected coupons')
    def activate_coupons(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description='Deactivate selected coupons')
    def deactivate_coupons(self, request, queryset):
        queryset.update(is_active=False)

