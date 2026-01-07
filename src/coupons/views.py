from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Coupon
from .forms import CouponApplyForm

def apply_coupon(request):
    if request.method == 'POST':
        form = CouponApplyForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code'].upper()
            order_total = request.session.get('cart_total', 0)  # totalul curent din sesiune
            try:
                coupon = Coupon.objects.get(code=code)
                if coupon.is_valid(order_total):
                    request.session['coupon_code'] = coupon.code
                    request.session['coupon_discount'] = float(coupon.calculate_discount(order_total))
                    messages.success(request, f"Cuponul {coupon.code} a fost aplicat!")
                    return redirect('cart:view_cart')
                else:
                    messages.error(request, "Cuponul nu este valid sau nu se aplică la această comandă.")
            except Coupon.DoesNotExist:
                messages.error(request, "Codul cupon nu există.")
    else:
        form = CouponApplyForm()
    return render(request, 'coupons/apply_coupon.html', {'form': form})

