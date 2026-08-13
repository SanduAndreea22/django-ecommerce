from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from orders.models import Order, OrderItem
from products.models import Variant

LOW_STOCK_THRESHOLD = 5


def _is_staff(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(_is_staff, login_url='accounts:login')
def stats_view(request):
    orders = Order.objects.exclude(status='cancelled')

    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    total_orders = orders.count()

    today = timezone.localdate()
    orders_today = orders.filter(created_at__date=today).count()

    top_products = (
        OrderItem.objects
        .exclude(order__status='cancelled')
        .values('variant__product__name')
        .annotate(total_sold=Sum('quantity'))
        .order_by('-total_sold')[:5]
    )

    low_stock_variants = (
        Variant.objects
        .filter(is_active=True, stock_quantity__lte=LOW_STOCK_THRESHOLD)
        .select_related('product')
        .order_by('stock_quantity')[:10]
    )

    context = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'orders_today': orders_today,
        'top_products': top_products,
        'low_stock_variants': low_stock_variants,
        'low_stock_threshold': LOW_STOCK_THRESHOLD,
    }
    return render(request, 'dashboard/stats.html', context)
