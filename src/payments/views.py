from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from orders.models import Order
from .models import Payment

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


