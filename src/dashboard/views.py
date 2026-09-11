from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from django.shortcuts import render
from django.utils import timezone

from orders.models import Order, OrderItem
from products.models import Variant

LOW_STOCK_THRESHOLD = 5


def staff_required(view_func):
    """
    Diferit de user_passes_test(is_staff, login_url=...): un user autentificat
    dar fără is_staff primea acolo un redirect spre login (confuz — "de ce mi se
    cere din nou să mă loghez?"). Aici userii anonimi sunt trimiși la login, dar
    userii autentificați neautorizați primesc direct 403.
    """
    @wraps(view_func)
    @login_required(login_url='accounts:login')
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("You don't have access to this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped


@staff_required
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
