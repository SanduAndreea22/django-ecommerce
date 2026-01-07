from django.contrib import admin
from .models import Category, Product, Variant, ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'is_active')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}

class VariantInline(admin.TabularInline):
    model = Variant
    extra = 1

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [VariantInline, ProductImageInline]

@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'color', 'stock_quantity', 'is_active')
    list_filter = ('size', 'color', 'is_active')

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'is_main')
