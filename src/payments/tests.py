from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import Order

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
