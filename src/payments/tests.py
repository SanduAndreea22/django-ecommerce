from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from orders.models import Order
from .models import Payment

User = get_user_model()


class CashPaymentSecurityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass12345')
        self.other = User.objects.create_user(username='other', email='other@example.com', password='pass12345')
        self.order = Order.objects.create(
            user=self.owner,
            order_number='ORD123',
            total_amount=50,
            payment_status='pending',
            payment_method='cash',
            status='pending',
        )

    def test_anonymous_cannot_mark_order_paid(self):
        response = self.client.post(reverse('payments:cash_payment', args=[self.order.order_number]))
        self.assertNotEqual(response.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'pending')

    def test_other_user_cannot_mark_someone_elses_order_paid(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse('payments:cash_payment', args=[self.order.order_number]))
        self.assertEqual(response.status_code, 404)
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'pending')

    def test_get_request_is_rejected(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('payments:cash_payment', args=[self.order.order_number]))
        self.assertEqual(response.status_code, 405)

    def test_owner_can_mark_own_order_paid(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('payments:cash_payment', args=[self.order.order_number]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')


@override_settings(STRIPE_SECRET_KEY='sk_test_fake', STRIPE_PUBLISHABLE_KEY='pk_test_fake')
class StripeCheckoutTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass12345')
        self.other = User.objects.create_user(username='other', email='other@example.com', password='pass12345')
        self.order = Order.objects.create(
            user=self.owner,
            order_number='ORD-STRIPE-1',
            total_amount=50,
            payment_status='pending',
            payment_method='stripe',
            status='pending',
        )
        Payment.objects.create(order=self.order, method='stripe', amount=50, status='pending')

    @patch('payments.views.stripe.checkout.Session.create')
    def test_stripe_checkout_shows_redirect_page_with_hosted_session_link(self, mock_create):
        mock_create.return_value = SimpleNamespace(url='https://checkout.stripe.com/test-session')
        self.client.force_login(self.owner)

        response = self.client.get(reverse('payments:stripe_checkout', args=[self.order.order_number]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://checkout.stripe.com/test-session')
        mock_create.assert_called_once()

    def test_other_user_cannot_start_stripe_checkout_for_someone_elses_order(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse('payments:stripe_checkout', args=[self.order.order_number]))
        self.assertEqual(response.status_code, 404)

    @patch('payments.views.stripe.checkout.Session.retrieve')
    def test_stripe_success_marks_order_paid_when_session_confirms_payment(self, mock_retrieve):
        mock_retrieve.return_value = SimpleNamespace(
            payment_status='paid',
            metadata={'order_number': self.order.order_number},
        )
        self.client.force_login(self.owner)

        response = self.client.get(
            reverse('payments:stripe_success', args=[self.order.order_number]),
            {'session_id': 'cs_test_123'},
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'paid')
        self.assertRedirects(
            response,
            reverse('orders:order_success', args=[self.order.order_number]),
            fetch_redirect_response=False,
        )

    @patch('payments.views.stripe.checkout.Session.retrieve')
    def test_stripe_success_does_not_mark_paid_when_session_unpaid(self, mock_retrieve):
        mock_retrieve.return_value = SimpleNamespace(
            payment_status='unpaid',
            metadata={'order_number': self.order.order_number},
        )
        self.client.force_login(self.owner)

        self.client.get(
            reverse('payments:stripe_success', args=[self.order.order_number]),
            {'session_id': 'cs_test_123'},
        )

        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'pending')

    def test_stripe_cancel_keeps_order_pending(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('payments:stripe_cancel', args=[self.order.order_number]))
        self.assertRedirects(response, reverse('orders:order_detail', args=[self.order.id]))
        self.order.refresh_from_db()
        self.assertEqual(self.order.payment_status, 'pending')


class StripeDisabledTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner2', email='owner2@example.com', password='pass12345')
        self.order = Order.objects.create(
            user=self.owner,
            order_number='ORD-NOSTRIPE',
            total_amount=50,
            payment_status='pending',
            payment_method='stripe',
            status='pending',
        )

    def test_stripe_checkout_redirects_away_when_not_configured(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('payments:stripe_checkout', args=[self.order.order_number]))
        self.assertRedirects(response, reverse('orders:order_detail', args=[self.order.id]))
