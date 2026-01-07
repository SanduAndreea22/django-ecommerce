from django.shortcuts import render, redirect, get_object_or_404
from products.models import Variant
from .models import CartItem

def _get_session_key(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key

def add_to_cart(request, variant_id):
    variant = get_object_or_404(Variant, id=variant_id)

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
    cart_item.save()
    return redirect('cart:cart_detail')


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

from coupons.forms import CouponApplyForm
from coupons.models import Coupon
from django.contrib import messages

def cart_detail(request):
    # Merge session cart dacă user-ul e logat
    if request.user.is_authenticated:
        merge_session_cart_to_user(request)
        items = CartItem.objects.filter(user=request.user)
    else:
        session_key = _get_session_key(request)
        items = CartItem.objects.filter(session_key=session_key)

    subtotal = 0
    for item in items:
        price = item.variant.price_override or item.variant.product.base_price
        item.item_total = price * item.quantity
        subtotal += item.item_total

    # Formular cupon
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].upper()
            try:
                coupon = Coupon.objects.get(code=code)
                if coupon.is_valid(subtotal):
                    request.session['coupon_code'] = coupon.code
                    request.session['coupon_discount'] = float(coupon.calculate_discount(subtotal))
                    messages.success(request, f"Cuponul {coupon.code} a fost aplicat!")
                else:
                    messages.error(request, "Cuponul nu este valid sau nu se aplică la această comandă.")
            except Coupon.DoesNotExist:
                messages.error(request, "Codul cupon nu există.")
    else:
        form = CouponApplyForm()

    coupon_code = request.session.get('coupon_code')
    discount_amount = request.session.get('coupon_discount', 0)
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

def update_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        item.quantity = quantity
        item.save()
    else:
        item.delete()

    return redirect('cart:cart_detail')


def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart:cart_detail')


