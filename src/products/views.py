from decimal import Decimal, InvalidOperation

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Product, Category, Variant

PRODUCTS_PER_PAGE = 12


def _parse_price(value):
    if not value:
        return None
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


# Home view → latest products
def home(request):
    latest_products = Product.objects.filter(is_active=True).prefetch_related('images').order_by('-created_at')[:8]
    context = {
        'latest_products': latest_products
    }
    return render(request, 'products/home.html', context)


# Catalog / product list
def product_list(request):
    products = Product.objects.filter(is_active=True).select_related('category').prefetch_related('images')
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
    min_price = _parse_price(request.GET.get('min'))
    max_price = _parse_price(request.GET.get('max'))
    if min_price is not None:
        products = products.filter(base_price__gte=min_price)
    if max_price is not None:
        products = products.filter(base_price__lte=max_price)

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories
    }
    return render(request, 'products/product_list.html', context)


# Product detail view
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related('images'),
        slug=slug, is_active=True
    )
    variants = Variant.objects.filter(product=product, is_active=True)

    context = {
        'product': product,
        'variants': variants
    }
    return render(request, 'products/product_detail.html', context)


