from decimal import Decimal

from django.db import transaction
from django.shortcuts import render
from django.utils.crypto import get_random_string
from cart.models import CartItem
from cart.views import merge_session_cart_to_user
from coupons.models import Coupon
from products.models import Variant
from .models import OrderItem
from payments.forms import PaymentMethodForm
from payments.models import Payment
from .forms import ShippingAddressForm
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Order

# ==========================
# CHECKOUT
# ==========================
@login_required
def checkout_view(request):
    user = request.user
    # Mutăm și aici itemele rămase în coșul de sesiune (dinainte de login) la user,
    # ca la un checkout direct (fără să treci prin /cart/ după login) coșul să nu
    # apară fals gol.
    merge_session_cart_to_user(request)
    cart_items = CartItem.objects.filter(user=user).select_related('variant__product')

    if not cart_items.exists():
        messages.warning(request, "Your cart is empty!")
        return redirect('cart:cart_detail')

    subtotal = sum(
        (item.variant.price_override or item.variant.product.base_price) * item.quantity
        for item in cart_items
    )

    # Discount-ul afișat e mereu recalculat din cuponul din sesiune + subtotalul curent,
    # niciodată citit ca valoare fixă din sesiune (putea rămâne stale/exploatabil dacă
    # coșul se schimba după aplicarea cuponului).
    coupon_code = request.session.get('coupon_code')
    coupon = Coupon.objects.filter(code=coupon_code).first() if coupon_code else None
    if coupon and not coupon.is_valid(subtotal):
        coupon = None
    discount = coupon.calculate_discount(subtotal) if coupon else Decimal('0')
    total_after_discount = max(subtotal - discount, 0)

    if request.method == 'POST':
        shipping_form = ShippingAddressForm(request.POST)
        payment_form = PaymentMethodForm(request.POST)

        if shipping_form.is_valid() and payment_form.is_valid():
            payment_method = payment_form.cleaned_data['method']
            is_cash = payment_method == 'cash'

            with transaction.atomic():
                # Blocăm variantele implicate și reverificăm stocul sub lock,
                # ca să evităm suprastocarea la checkout-uri concurente.
                variant_ids = [item.variant_id for item in cart_items]
                locked_variants = {
                    v.id: v for v in
                    Variant.objects.select_for_update().filter(id__in=variant_ids)
                }

                for item in cart_items:
                    variant = locked_variants[item.variant_id]
                    if item.quantity > variant.stock_quantity:
                        messages.error(
                            request,
                            f"Not enough stock for {item.variant.product.name} ({item.variant.size}/{item.variant.color}). "
                            f"Only {variant.stock_quantity} left. Please adjust your cart before continuing."
                        )
                        return render(request, 'orders/checkout.html', {
                            'cart_items': cart_items,
                            'subtotal': subtotal,
                            'discount': discount,
                            'total': total_after_discount,
                            'shipping_form': shipping_form,
                            'payment_form': payment_form,
                        })

                # Blocăm și rândul cuponului, ca să evităm ca două checkout-uri simultane
                # să treacă amândouă de verificarea max_uses pentru un cupon cu o singură
                # folosire disponibilă (recalculăm discountul sub lock, nu doar la POST inițial).
                order_coupon = None
                order_discount = Decimal('0')
                if coupon:
                    locked_coupon = Coupon.objects.select_for_update().get(pk=coupon.pk)
                    if locked_coupon.is_valid(subtotal):
                        order_coupon = locked_coupon
                        order_discount = locked_coupon.calculate_discount(subtotal)
                order_total = max(subtotal - order_discount, 0)

                order_number = get_random_string(10).upper()

                # Creare comandă
                order = Order.objects.create(
                    user=user,
                    order_number=order_number,
                    total_amount=order_total,
                    discount_amount=order_discount,
                    coupon=order_coupon,
                    payment_status='paid' if is_cash else 'pending',
                    payment_method=payment_method,
                    status='pending'
                )

                # Creare OrderItems și scădere stoc
                for item in cart_items:
                    variant = locked_variants[item.variant_id]
                    price = item.variant.price_override or item.variant.product.base_price
                    OrderItem.objects.create(
                        order=order,
                        variant=variant,
                        price_at_purchase=price,
                        quantity=item.quantity
                    )

                    # scade stocul
                    variant.stock_quantity -= item.quantity
                    variant.save()

                if order_coupon:
                    order_coupon.increment_usage()

                # Salvăm shipping
                shipping_address = shipping_form.save(commit=False)
                shipping_address.order = order
                shipping_address.save()

                # Creăm Payment
                Payment.objects.create(
                    order=order,
                    method=payment_method,
                    amount=order_total,
                    status='paid' if is_cash else 'pending'
                )

                # Golim coșul și sesiunea
                cart_items.delete()

            request.session.pop('coupon_code', None)
            request.session.pop('cart_discount', None)

            if is_cash:
                messages.success(request, "Your order was placed successfully!")
                return redirect('orders:order_success', order_number=order.order_number)

            return redirect('payments:stripe_checkout', order_number=order.order_number)

    else:
        shipping_form = ShippingAddressForm()
        payment_form = PaymentMethodForm()

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total_after_discount,
        'shipping_form': shipping_form,
        'payment_form': payment_form,
    }
    return render(request, 'orders/checkout.html', context)


# ==========================
# ORDER SUCCESS
# ==========================
@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


# ==========================
# ORDER HISTORY
# ==========================
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


# ==========================
# ORDER DETAIL
# ==========================
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order.objects.prefetch_related('items__variant__product'),
        id=order_id, user=request.user
    )
    return render(request, 'orders/order_detail.html', {'order': order})


# ==========================
# CANCEL ORDER  ✅
# ==========================
@login_required
@require_POST
def cancel_order(request, order_id):
    with transaction.atomic():
        order = get_object_or_404(
            Order.objects.select_for_update().prefetch_related('items__variant'),
            id=order_id, user=request.user
        )

        if order.status != 'pending':
            messages.error(request, 'This order can no longer be cancelled.')
            return redirect('orders:order_detail', order_id=order.id)

        # Anulăm comanda
        order.status = 'cancelled'
        order.save()

        # Restaurăm stocul pentru fiecare variantă, cu lock, ca să evităm ca o
        # anulare dublă (dublu-click/tab-uri concurente) să restaureze stocul de două ori.
        variant_ids = [item.variant_id for item in order.items.all() if item.variant_id]
        locked_variants = {
            v.id: v for v in Variant.objects.select_for_update().filter(id__in=variant_ids)
        }
        for item in order.items.all():
            variant = locked_variants.get(item.variant_id)
            if variant:
                variant.stock_quantity += item.quantity
                variant.save()

    messages.success(request, 'Your order was cancelled and the stock has been restored.')
    return redirect('orders:order_detail', order_id=order.id)

@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('shipping_address', 'user').prefetch_related('items__variant__product'),
        id=order_id, user=request.user
    )

    html_string = render_to_string('orders/invoice.html', {'order': order})
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{order.order_number}.pdf"'
    return response


