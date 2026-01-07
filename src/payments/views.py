from django.shortcuts import get_object_or_404, redirect, render
from orders.models import Order
from .models import Payment

def cash_payment(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)

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


