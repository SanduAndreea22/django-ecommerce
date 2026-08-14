from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Category, Product, Variant, WishlistItem

User = get_user_model()


class WishlistTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='buyer', email='buyer@example.com', password='pass12345')
        category = Category.objects.create(name='Cat', slug='cat')
        self.product = Product.objects.create(name='Prod', slug='prod', category=category, base_price=10)

    def test_anonymous_cannot_toggle_wishlist(self):
        response = self.client.post(reverse('products:toggle_wishlist', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(WishlistItem.objects.exists())

    def test_toggle_adds_and_removes_item(self):
        self.client.force_login(self.user)
        self.client.post(reverse('products:toggle_wishlist', args=[self.product.id]))
        self.assertTrue(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

        self.client.post(reverse('products:toggle_wishlist', args=[self.product.id]))
        self.assertFalse(WishlistItem.objects.filter(user=self.user, product=self.product).exists())

    def test_wishlist_view_only_shows_own_items(self):
        other = User.objects.create_user(username='other', email='other@example.com', password='pass12345')
        WishlistItem.objects.create(user=other, product=self.product)

        self.client.force_login(self.user)
        response = self.client.get(reverse('products:wishlist'))
        self.assertNotContains(response, 'Remove')

    def test_wishlist_shows_quick_add_for_single_variant_product(self):
        Variant.objects.create(product=self.product, size='One Size', color='N/A', stock_quantity=5, sku='SKU-1')
        WishlistItem.objects.create(user=self.user, product=self.product)

        self.client.force_login(self.user)
        response = self.client.get(reverse('products:wishlist'))
        self.assertContains(response, 'Add to cart')

    def test_wishlist_hides_quick_add_for_multi_variant_product(self):
        Variant.objects.create(product=self.product, size='S', color='Red', stock_quantity=5, sku='SKU-1')
        Variant.objects.create(product=self.product, size='M', color='Red', stock_quantity=5, sku='SKU-2')
        WishlistItem.objects.create(user=self.user, product=self.product)

        self.client.force_login(self.user)
        response = self.client.get(reverse('products:wishlist'))
        self.assertNotContains(response, 'Add to cart')
