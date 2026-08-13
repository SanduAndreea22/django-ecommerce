from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegistrationTests(TestCase):
    def test_register_creates_active_user_and_logs_in(self):
        response = self.client.post(reverse('accounts:register'), {
            'first_name': 'Ana',
            'last_name': 'Pop',
            'username': 'anapop',
            'email': 'ana@example.com',
            'password1': 'S0meStrongPass!',
            'password2': 'S0meStrongPass!',
        })

        user = User.objects.get(username='anapop')
        self.assertTrue(user.is_active)
        self.assertRedirects(response, reverse('accounts:profile', args=[user.username]))

        # userul e deja autentificat, fără pas de confirmare prin email
        profile_response = self.client.get(reverse('accounts:profile', args=[user.username]))
        self.assertEqual(profile_response.status_code, 200)
