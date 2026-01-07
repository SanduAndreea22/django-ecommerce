from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
from .models import Order, OrderItem, ShippingAddress
from payments.models import Payment
from .forms import ShippingAddressForm

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.crypto import get_random_string
from django.contrib.auth.decorators import login_required
from cart.models import CartItem
from .models import Order, OrderItem, ShippingAddress
from payments.models import Payment
from .forms import ShippingAddressForm

@login_required
def checkout_view(request):
    user = request.user
    cart_items = CartItem.objects.filter(user=user)

    if not cart_items.exists():
        return redirect('cart:cart_detail')

    subtotal = sum(
        (item.variant.price_override or item.variant.product.base_price) * item.quantity
        for item in cart_items
    )
    discount = request.session.get('cart_discount', 0)
    total_after_discount = max(subtotal - discount, 0)

    if request.method == 'POST':
        shipping_form = ShippingAddressForm(request.POST)

        if shipping_form.is_valid():
            order_number = get_random_string(10).upper()
            payment_method = 'cash'  # fixăm cash

            # Creăm comanda
            order = Order.objects.create(
                user=user,
                order_number=order_number,
                total_amount=total_after_discount,
                discount_amount=discount,
                payment_status='paid',  # cash → plătit la livrare
                payment_method=payment_method,
                status='pending'  # se schimbă când e livrat
            )

            # Creăm OrderItems
            for item in cart_items:
                price = item.variant.price_override or item.variant.product.base_price
                OrderItem.objects.create(
                    order=order,
                    variant=item.variant,
                    price_at_purchase=price,
                    quantity=item.quantity
                )

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

            # Golim coșul
            cart_items.delete()
            request.session.pop('coupon_code', None)
            request.session.pop('cart_discount', None)

            # Redirect la pagina de succes
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



@login_required
def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'orders/order_success.html', {'order': order})



@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

