from django.contrib import admin
from .models import Category, Product, Variant, ProductImage


# =========================
# INLINE
# =========================

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1
    fields = (
        'size',
        'color',
        'price_override',
        'stock_quantity',
        'sku',
        'is_active',
    )
    readonly_fields = ()
    show_change_link = True


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'is_main')


# =========================
# CATEGORY ADMIN
# =========================

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# =========================
# PRODUCT ADMIN
# =========================

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'base_price',
        'is_active',
        'created_at',
    )
    list_filter = ('is_active', 'category')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VariantInline, ProductImageInline]
    date_hierarchy = 'created_at'


# =========================
# VARIANT ADMIN (optional separat)
# =========================

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'size',
        'color',
        'price_override',
        'stock_quantity',
        'sku',
        'is_active',
    )
    list_filter = ('is_active', 'product')
    search_fields = ('product__name', 'sku')

