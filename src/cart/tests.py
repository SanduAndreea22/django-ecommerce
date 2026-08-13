from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from products.models import Category, Product, Variant
from .models import CartItem

User = get_user_model()


class CartOwnershipTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', email='owner@example.com', password='pass12345')
        self.other = User.objects.create_user(username='other', email='other@example.com', password='pass12345')

        category = Category.objects.create(name='Cat', slug='cat')
        product = Product.objects.create(name='Prod', slug='prod', category=category, base_price=10)
        self.variant = Variant.objects.create(product=product, size='M', color='Red', stock_quantity=5, sku='SKU-1')

        self.item = CartItem.objects.create(user=self.owner, variant=self.variant, quantity=1)

    def test_add_to_cart_requires_post(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('cart:add_to_cart'))
        self.assertEqual(response.status_code, 405)

    def test_add_to_cart_uses_variant_from_post_body(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('cart:add_to_cart'), {'variant_id': self.variant.id})
        self.assertTrue(CartItem.objects.filter(user=self.owner, variant=self.variant).exists())

    def test_user_cannot_update_someone_elses_cart_item(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse('cart:update_cart', args=[self.item.id]), {'quantity': 5})
        self.assertEqual(response.status_code, 404)
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 1)

    def test_user_cannot_remove_someone_elses_cart_item(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse('cart:remove_from_cart', args=[self.item.id]))
        self.assertEqual(response.status_code, 404)
        self.assertTrue(CartItem.objects.filter(id=self.item.id).exists())

    def test_owner_can_update_own_cart_item(self):
        self.client.force_login(self.owner)
        self.client.post(reverse('cart:update_cart', args=[self.item.id]), {'quantity': 3})
        self.item.refresh_from_db()
        self.assertEqual(self.item.quantity, 3)

    def test_remove_from_cart_requires_post(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('cart:remove_from_cart', args=[self.item.id]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(CartItem.objects.filter(id=self.item.id).exists())
