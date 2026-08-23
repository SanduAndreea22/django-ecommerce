from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST

from coupons.forms import CouponApplyForm
from coupons.models import Coupon
from products.models import Variant
from .models import CartItem

def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def _get_owned_cart_item(request, item_id):
    if request.user.is_authenticated:
        return get_object_or_404(CartItem, id=item_id, user=request.user)
    session_key = _get_session_key(request)
    return get_object_or_404(CartItem, id=item_id, session_key=session_key)

def _is_ajax(request):
    return request.headers.get('X-Requested-With') == 'XMLHttpRequest'

def _current_cart_count(request):
    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        items = CartItem.objects.filter(session_key=session_key) if session_key else CartItem.objects.none()
    return items.aggregate(total=Sum('quantity'))['total'] or 0

def _add_to_cart_response(request, success, message, level='success'):
    if _is_ajax(request):
        return JsonResponse({
            'success': success,
            'message': message,
            'cart_count': _current_cart_count(request),
        })
    getattr(messages, level)(request, message)
    return redirect('cart:cart_detail')

@require_POST
def add_to_cart(request):
    variant_id = request.POST.get('variant_id')
    if not variant_id or not variant_id.isdigit():
        return _add_to_cart_response(request, False, "Please choose a valid product option.", 'error')

    variant = Variant.objects.filter(id=variant_id, is_active=True).first()
    if not variant:
        return _add_to_cart_response(request, False, "This product option isn't available anymore.", 'error')

    if request.user.is_authenticated:
        cart_item, created = CartItem.objects.get_or_create(
            user=request.user,
            variant=variant
        )
    else:
        session_key = _get_session_key(request)
        cart_item, created = CartItem.objects.get_or_create(
            session_key=session_key,
            variant=variant
        )

    if not created:
        cart_item.quantity += 1

    if variant.stock_quantity <= 0:
        cart_item.delete()
        return _add_to_cart_response(
            request, False, f"{variant.product.name} is currently out of stock.", 'error'
        )

    adjusted = False
    if cart_item.quantity > variant.stock_quantity:
        cart_item.quantity = variant.stock_quantity
        adjusted = True

    cart_item.save()

    if adjusted:
        return _add_to_cart_response(
            request, True,
            f"Only {variant.stock_quantity} of {variant.product.name} left in stock — quantity adjusted.",
            'warning',
        )
    return _add_to_cart_response(request, True, f"{variant.product.name} added to your cart.")


def merge_session_cart_to_user(request):
    """Apelează la login pentru a muta produsele din sesiune la user logat"""
    if not request.user.is_authenticated:
        return

    session_key = request.session.session_key
    if not session_key:
        return

    session_items = CartItem.objects.filter(session_key=session_key)
    for item in session_items:
        existing_item = CartItem.objects.filter(user=request.user, variant=item.variant).first()
        if existing_item:
            existing_item.quantity += item.quantity
            existing_item.save()
        else:
            item.user = request.user
            item.session_key = None
            item.save()


def cart_detail(request):
    # Dacă user-ul e logat, mutăm itemele din sesiune în user
    if request.user.is_authenticated:
        merge_session_cart_to_user(request)
        items = CartItem.objects.filter(user=request.user).select_related('variant__product')
    else:
        session_key = _get_session_key(request)
        items = CartItem.objects.filter(session_key=session_key).select_related('variant__product')

    # Calculăm subtotal
    subtotal = Decimal('0.00')
    for item in items:
        price = item.variant.price_override or item.variant.product.base_price
        item.item_total = price * item.quantity
        subtotal += item.item_total

    # Formular aplicare cupon
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].upper()
            try:
                coupon = Coupon.objects.get(code=code)
                if coupon.is_valid(subtotal):
                    request.session['coupon_code'] = coupon.code
                    messages.success(request, f"Coupon {coupon.code} applied!")
                elif not coupon.is_active:
                    messages.error(request, "This coupon is no longer active.")
                elif coupon.valid_from > timezone.now() or coupon.valid_to < timezone.now():
                    messages.error(request, "This coupon has expired or isn't active yet.")
                elif coupon.max_uses is not None and coupon.used_count >= coupon.max_uses:
                    messages.error(request, "This coupon has already reached its usage limit.")
                elif subtotal < coupon.min_order_value:
                    messages.error(
                        request,
                        f"This coupon needs a minimum order of {coupon.min_order_value} RON "
                        f"(your cart is {subtotal} RON)."
                    )
                else:
                    messages.error(request, "This coupon can't be applied to your order.")
            except Coupon.DoesNotExist:
                messages.error(request, "This coupon code doesn't exist.")
    else:
        form = CouponApplyForm()

    # Recalculăm mereu discountul din cuponul din sesiune + subtotalul curent,
    # nu dintr-o valoare stocată — evită un discount rămas fix după ce coșul se schimbă.
    coupon_code = request.session.get('coupon_code')
    active_coupon = Coupon.objects.filter(code=coupon_code).first() if coupon_code else None
    if active_coupon and not active_coupon.is_valid(subtotal):
        active_coupon = None
        coupon_code = None
        request.session.pop('coupon_code', None)
    discount_amount = active_coupon.calculate_discount(subtotal) if active_coupon else Decimal('0.00')

    # Calculăm totalul
    total = subtotal - discount_amount

    context = {
        'items': items,
        'subtotal': subtotal,
        'discount': discount_amount,
        'coupon_code': coupon_code,
        'total': total,
        'form': form,
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def update_cart(request, item_id):
    item = _get_owned_cart_item(request, item_id)

    try:
        quantity = int(request.POST.get('quantity', 1))
    except (TypeError, ValueError):
        messages.error(request, "Please enter a valid quantity.")
        return redirect('cart:cart_detail')

    if quantity > item.variant.stock_quantity:
        quantity = item.variant.stock_quantity
        messages.warning(
            request,
            f"Only {item.variant.stock_quantity} of {item.variant.product.name} left in stock — quantity adjusted."
        )

    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()

    return redirect('cart:cart_detail')


@require_POST
def remove_from_cart(request, item_id):
    item = _get_owned_cart_item(request, item_id)
    item.delete()
    return redirect('cart:cart_detail')


