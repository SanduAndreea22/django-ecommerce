import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from orders.models import Order
from .models import Payment
from .services import stripe_enabled


@login_required
@require_POST
def cash_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    # Creăm Payment ca plătit automat
    payment, created = Payment.objects.get_or_create(
        order=order,
        defaults={
            'method': 'cash',
            'amount': order.total_after_discount,
            'status': 'paid'
        }
    )

    # Actualizăm statusul comenzii
    order.payment_status = 'paid'
    order.status = 'pending'
    order.save()

    return redirect('orders:order_success', order_number=order.order_number)


@login_required
def stripe_checkout(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if order.payment_status == 'paid':
        return redirect('orders:order_success', order_number=order.order_number)

    if not stripe_enabled():
        messages.error(request, "Plata cu cardul nu este disponibilă momentan.")
        return redirect('orders:order_detail', order_id=order.id)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',
        line_items=[{
            'price_data': {
                'currency': 'ron',
                'product_data': {'name': f'Comandă #{order.order_number}'},
                'unit_amount': int(order.total_after_discount * 100),
            },
            'quantity': 1,
        }],
        success_url=request.build_absolute_uri(
            reverse('payments:stripe_success', args=[order.order_number])
        ) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(
            reverse('payments:stripe_cancel', args=[order.order_number])
        ),
        metadata={'order_number': order.order_number},
    )
    return redirect(session.url)


@login_required
def stripe_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    session_id = request.GET.get('session_id')

    if stripe_enabled() and session_id:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        session = stripe.checkout.Session.retrieve(session_id)
        if (
            session.payment_status == 'paid'
            and session.metadata.get('order_number') == order.order_number
        ):
            order.payment_status = 'paid'
            order.save(update_fields=['payment_status'])
            Payment.objects.filter(order=order).update(status='paid')
            messages.success(request, "Plata a fost confirmată. Mulțumim!")
            return redirect('orders:order_success', order_number=order.order_number)

    messages.error(request, "Nu am putut confirma plata. Te rugăm să reîncerci.")
    return redirect('orders:order_detail', order_id=order.id)


@login_required
def stripe_cancel(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    messages.warning(request, "Plata a fost anulată. Poți reîncerca oricând din pagina comenzii.")
    return redirect('orders:order_detail', order_id=order.id)
