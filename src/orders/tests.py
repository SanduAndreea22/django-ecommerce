from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from cart.models import CartItem
from coupons.models import Coupon
from products.models import Category, Product, Variant
from .models import Order

User = get_user_model()


class CheckoutTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', email='buyer@example.com', password='pass12345')
        self.client.force_login(self.user)

        category = Category.objects.create(name='Cat', slug='cat')
        self.product = Product.objects.create(name='Prod', slug='prod', category=category, base_price=Decimal('20.00'))
        self.variant = Variant.objects.create(
            product=self.product, size='M', color='Red', stock_quantity=3, sku='SKU-1'
        )

        self.shipping_data = {
            'full_name': 'John Doe',
            'phone': '0700000000',
            'address_line_1': 'Str. Exemplu 1',
            'address_line_2': '',
            'city': 'Bucuresti',
            'postal_code': '010101',
            'country': 'Romania',
            'method': 'cash',
        }

    def test_checkout_decrements_stock_and_creates_order(self):
        CartItem.objects.create(user=self.user, variant=self.variant, quantity=2)

        response = self.client.post(reverse('orders:checkout'), self.shipping_data)

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 1)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 1)
        self.assertFalse(CartItem.objects.filter(user=self.user).exists())
        self.assertEqual(response.status_code, 302)

    def test_checkout_blocks_when_stock_insufficient(self):
        CartItem.objects.create(user=self.user, variant=self.variant, quantity=10)

        self.client.post(reverse('orders:checkout'), self.shipping_data)

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 3)
        self.assertEqual(Order.objects.filter(user=self.user).count(), 0)

    def test_checkout_applies_coupon_discount_and_increments_usage(self):
        coupon = Coupon.objects.create(
            code='SAVE10',
            discount_type='fixed',
            discount_value=Decimal('5.00'),
            max_uses=1,
            used_count=0,
            valid_from=timezone.now() - timezone.timedelta(days=1),
            valid_to=timezone.now() + timezone.timedelta(days=1),
        )
        CartItem.objects.create(user=self.user, variant=self.variant, quantity=1)

        session = self.client.session
        session['coupon_code'] = coupon.code
        session['cart_discount'] = '5.00'
        session.save()

        self.client.post(reverse('orders:checkout'), self.shipping_data)

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.discount_amount, Decimal('5.00'))
        self.assertEqual(order.total_amount, Decimal('15.00'))
        self.assertEqual(order.coupon, coupon)

        coupon.refresh_from_db()
        self.assertEqual(coupon.used_count, 1)

    @override_settings(STRIPE_SECRET_KEY='sk_test_fake', STRIPE_PUBLISHABLE_KEY='pk_test_fake')
    def test_checkout_with_stripe_creates_pending_order_and_redirects_to_stripe_flow(self):
        CartItem.objects.create(user=self.user, variant=self.variant, quantity=1)
        data = dict(self.shipping_data, method='stripe')

        response = self.client.post(reverse('orders:checkout'), data)

        order = Order.objects.get(user=self.user)
        self.assertEqual(order.payment_method, 'stripe')
        self.assertEqual(order.payment_status, 'pending')
        self.assertRedirects(
            response,
            reverse('payments:stripe_checkout', args=[order.order_number]),
            fetch_redirect_response=False,
        )

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 2)

    def test_checkout_rejects_stripe_when_not_configured(self):
        CartItem.objects.create(user=self.user, variant=self.variant, quantity=1)
        data = dict(self.shipping_data, method='stripe')

        self.client.post(reverse('orders:checkout'), data)

        self.assertFalse(Order.objects.filter(user=self.user).exists())

    def test_cancel_order_restores_stock(self):
        CartItem.objects.create(user=self.user, variant=self.variant, quantity=2)
        self.client.post(reverse('orders:checkout'), self.shipping_data)
        order = Order.objects.get(user=self.user)

        self.variant.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 1)

        self.client.post(reverse('orders:cancel_order', args=[order.id]))

        self.variant.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(self.variant.stock_quantity, 3)
        self.assertEqual(order.status, 'cancelled')
