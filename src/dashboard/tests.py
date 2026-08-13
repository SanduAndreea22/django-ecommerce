from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from orders.models import Order

User = get_user_model()


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.staff = User.objects.create_user(
            username='staffuser', email='staff@example.com', password='pass12345', is_staff=True
        )
        self.customer = User.objects.create_user(
            username='customer', email='customer@example.com', password='pass12345'
        )
        Order.objects.create(
            user=self.customer,
            order_number='ORD1',
            total_amount=Decimal('30.00'),
            payment_status='paid',
            payment_method='cash',
            status='pending',
        )

    def test_anonymous_redirected(self):
        response = self.client.get(reverse('dashboard:stats'))
        self.assertEqual(response.status_code, 302)

    def test_non_staff_redirected(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse('dashboard:stats'))
        self.assertEqual(response.status_code, 302)

    def test_staff_can_view_stats(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('dashboard:stats'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '30.00')
