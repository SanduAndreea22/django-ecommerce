from django.contrib import admin
from .models import Category, Product, Variant, ProductImage, WishlistItem, Review, NewsletterSubscriber


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


# =========================
# WISHLIST ADMIN
# =========================

@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    list_filter = ('added_at',)
    search_fields = ('user__username', 'product__name')


# =========================
# REVIEW ADMIN
# =========================

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')


# =========================
# NEWSLETTER ADMIN
# =========================

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    search_fields = ('email',)

