import stripe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from orders.models import Order
from .models import Payment
from .services import stripe_enabled


@login_required
@require_POST
def cash_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)

    if order.payment_method != 'cash':
        messages.error(request, "This order isn't set up for cash payment.")
        return redirect('orders:order_detail', order_id=order.id)

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
        messages.error(request, "Card payment isn't available right now.")
        return redirect('orders:order_detail', order_id=order.id)

    stripe.api_key = settings.STRIPE_SECRET_KEY
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        mode='payment',
        line_items=[{
            'price_data': {
                'currency': 'ron',
                'product_data': {'name': f'Order #{order.order_number}'},
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
    return render(request, 'payments/redirecting.html', {
        'order': order,
        'checkout_url': session.url,
    })


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
            messages.success(request, "Payment confirmed. Thank you!")
            return redirect('orders:order_success', order_number=order.order_number)

    messages.error(request, "We couldn't confirm your payment. Please try again.")
    return redirect('orders:order_detail', order_id=order.id)


@login_required
def stripe_cancel(request, order_number):
    order = get_object_or_404(Order, order_number=order_number, user=request.user)
    messages.warning(request, "Payment was cancelled. You can try again anytime from the order page.")
    return redirect('orders:order_detail', order_id=order.id)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """
    Confirmă plata independent de redirect-ul din browser — dacă userul închide
    tab-ul după plată, webhook-ul e singura cale prin care comanda nu rămâne
    blocată la 'pending' pentru totdeauna.
    """
    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse(status=200)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponseBadRequest('Invalid payload or signature.')

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_number = session.get('metadata', {}).get('order_number')
        if order_number and session.get('payment_status') == 'paid':
            order = Order.objects.filter(order_number=order_number).first()
            if order and order.payment_status != 'paid':
                order.payment_status = 'paid'
                order.save(update_fields=['payment_status'])
                Payment.objects.filter(order=order).update(status='paid')

    return HttpResponse(status=200)
