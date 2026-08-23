from django.db.models import Sum

from .models import CartItem


def cart_count(request):
    """Numărul total de produse din coș, afișat ca badge lângă 'Cart' în navbar."""
    if request.user.is_authenticated:
        items = CartItem.objects.filter(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            return {'cart_count': 0}
        items = CartItem.objects.filter(session_key=session_key)

    total = items.aggregate(total=Sum('quantity'))['total'] or 0
    return {'cart_count': total}
