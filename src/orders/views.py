from django.shortcuts import render
from django.utils.crypto import get_random_string
from cart.models import CartItem
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

# ==========================
# CHECKOUT
# ==========================
@login_required
def checkout_view(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items.exists():
        messages.warning(request, "Coșul tău este gol!")
        return redirect('cart:cart_detail')

    subtotal = sum(
        (item.variant.price_override or item.variant.product.base_price) * item.quantity
        for item in cart_items
    )

    discount = request.session.get('cart_discount', 0)
    total_after_discount = max(subtotal - discount, 0)

    if request.method == 'POST':
        shipping_form = ShippingAddressForm(request.POST)

        # verificare stoc
        for item in cart_items:
            if item.quantity > item.variant.stock_quantity:
                messages.error(
                    request,
                    f"Stoc insuficient pentru {item.variant.product.name} ({item.variant.size}/{item.variant.color}). "
                    f"Avem doar {item.variant.stock_quantity} buc."
                )
                return redirect('cart:cart_detail')

        if shipping_form.is_valid():
            order_number = get_random_string(10).upper()

            # Creare comandă
            order = Order.objects.create(
                user=user,
                order_number=order_number,
                total_amount=total_after_discount,
                discount_amount=discount,
                payment_status='paid',  # cash → plătit la livrare
                payment_method='cash',
                status='pending'
            )

            # Creare OrderItems și scădere stoc
            for item in cart_items:
                price = item.variant.price_override or item.variant.product.base_price
                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    price_at_purchase=price,
                    quantity=item.quantity
                )

                # scade stocul
                item.variant.stock_quantity -= item.quantity
                item.variant.save()

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
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


# ==========================
# CANCEL ORDER  ✅
# ==========================
@login_required
@require_POST
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

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
    order = get_object_or_404(Order, id=order_id, user=request.user)

    html_string = render_to_string('orders/invoice.html', {'order': order})
    html = HTML(string=html_string)
    pdf_file = html.write_pdf()

    response = HttpResponse(pdf_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Factura_{order.order_number}.pdf"'
    return response


