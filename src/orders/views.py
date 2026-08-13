import logging
from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.shortcuts import render
from django.utils.crypto import get_random_string
from cart.models import CartItem
from coupons.models import Coupon
from products.models import Variant
from .models import OrderItem
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

logger = logging.getLogger(__name__)


def _send_order_confirmation_email(order):
    if not order.user or not order.user.email:
        return
    try:
        message = render_to_string('orders/order_confirmation_email.txt', {'order': order})
        send_mail(
            subject=f"Comanda ta #{order.order_number} a fost plasată",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send order confirmation email for order %s", order.order_number)

# ==========================
# CHECKOUT
# ==========================
@login_required
def checkout_view(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user).select_related('variant__product')

    if not cart_items.exists():
        messages.warning(request, "Coșul tău este gol!")
        return redirect('cart:cart_detail')

    subtotal = sum(
        (item.variant.price_override or item.variant.product.base_price) * item.quantity
        for item in cart_items
    )

    discount = Decimal(request.session.get('cart_discount', '0'))
    total_after_discount = max(subtotal - discount, 0)

    if request.method == 'POST':
        shipping_form = ShippingAddressForm(request.POST)

        if shipping_form.is_valid():
            coupon_code = request.session.get('coupon_code')

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
                            f"Stoc insuficient pentru {item.variant.product.name} ({item.variant.size}/{item.variant.color}). "
                            f"Avem doar {variant.stock_quantity} buc."
                        )
                        return redirect('cart:cart_detail')

                coupon = None
                if coupon_code:
                    coupon = Coupon.objects.filter(code=coupon_code).first()
                    if coupon and not coupon.is_valid(subtotal):
                        coupon = None

                order_number = get_random_string(10).upper()

                # Creare comandă
                order = Order.objects.create(
                    user=user,
                    order_number=order_number,
                    total_amount=total_after_discount,
                    discount_amount=discount,
                    coupon=coupon,
                    payment_status='paid',  # cash → plătit la livrare
                    payment_method='cash',
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

                if coupon:
                    coupon.increment_usage()

                # Salvăm shipping
                shipping_address = shipping_form.save(commit=False)
                shipping_address.order = order
                shipping_address.save()

                # Creăm Payment
                Payment.objects.create(
                    order=order,
                    method='cash',
                    amount=total_after_discount,
                    status='paid'
                )

                # Golim coșul și sesiunea
                cart_items.delete()

            request.session.pop('coupon_code', None)
            request.session.pop('cart_discount', None)

            _send_order_confirmation_email(order)

            messages.success(request, "Comanda a fost plasată cu succes!")
            return redirect('orders:order_success', order_number=order.order_number)

    else:
        shipping_form = ShippingAddressForm()

    context = {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'total': total_after_discount,
        'shipping_form': shipping_form,
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
    order = get_object_or_404(
        Order.objects.prefetch_related('items__variant'),
        id=order_id, user=request.user
    )

    if order.status != 'pending':
        messages.error(request, 'Comanda nu mai poate fi anulată.')
        return redirect('orders:order_detail', order_id=order.id)

    # Anulăm comanda
    order.status = 'cancelled'
    order.save()

    # Restaurăm stocul pentru fiecare variantă
    for item in order.items.all():
        variant = item.variant
        if variant:
            variant.stock_quantity += item.quantity
            variant.save()

    messages.success(request, 'Comanda a fost anulată cu succes și stocul a fost restaurat.')
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


