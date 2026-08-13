from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .models import Product, Category, Variant, WishlistItem

PRODUCTS_PER_PAGE = 12

SORT_OPTIONS = {
    'newest': '-created_at',
    'price_asc': 'base_price',
    'price_desc': '-base_price',
    'name_asc': 'name',
}
DEFAULT_SORT = 'newest'


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

    # SORT
    sort = request.GET.get('sort')
    if sort not in SORT_OPTIONS:
        sort = DEFAULT_SORT
    products = products.order_by(SORT_OPTIONS[sort])

    paginator = Paginator(products, PRODUCTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'sort': sort,
    }
    return render(request, 'products/product_list.html', context)


# Product detail view
def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.prefetch_related('images'),
        slug=slug, is_active=True
    )
    variants = Variant.objects.filter(product=product, is_active=True)

    is_wishlisted = (
        request.user.is_authenticated
        and WishlistItem.objects.filter(user=request.user, product=product).exists()
    )

    context = {
        'product': product,
        'variants': variants,
        'is_wishlisted': is_wishlisted,
    }
    return render(request, 'products/product_detail.html', context)


# ==========================
# WISHLIST
# ==========================
@login_required
def wishlist_view(request):
    items = WishlistItem.objects.filter(user=request.user).select_related('product__category').prefetch_related('product__images')
    return render(request, 'products/wishlist.html', {'items': items})


@login_required
@require_POST
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    item, created = WishlistItem.objects.get_or_create(user=request.user, product=product)

    if not created:
        item.delete()
        messages.success(request, f"{product.name} a fost eliminat din wishlist.")
    else:
        messages.success(request, f"{product.name} a fost adăugat la wishlist.")

    next_url = request.POST.get('next')
    if not next_url or not url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        next_url = product.get_absolute_url()
    return redirect(next_url)


