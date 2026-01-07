from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Variant

# Home view → latest products
def home(request):
    latest_products = Product.objects.filter(is_active=True).order_by('-created_at')[:8]
    context = {
        'latest_products': latest_products
    }
    return render(request, 'products/home.html', context)


# Catalog / product list
def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(is_active=True)

    # SEARCH
    query = request.GET.get('q')
    if query:
        products = products.filter(name__icontains=query)

    # CATEGORY filter
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # PRICE filter
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    if min_price:
        products = products.filter(base_price__gte=min_price)
    if max_price:
        products = products.filter(base_price__lte=max_price)

    context = {
        'products': products,
        'categories': categories
    }
    return render(request, 'products/product_list.html', context)


# Product detail view
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variants = Variant.objects.filter(product=product, is_active=True)

    context = {
        'product': product,
        'variants': variants
    }
    return render(request, 'products/product_detail.html', context)


