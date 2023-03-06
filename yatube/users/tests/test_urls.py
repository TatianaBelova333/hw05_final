from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings

from posts.tests.factories import UserFactory


class UserURLTests(TestCase):
    """Tests for the URLs of the `users` app."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory(username='OtherUser')

        cls.public_url_template = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/logout/': 'users/logged_out.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
        }

        cls.private_url_template = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(UserURLTests.user)

    def test_public_urls_exist_anonymous(self):
        """Test public URLs of the `users` app for an anonymous user."""
        for url in UserURLTests.public_url_template.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_public_urls_use_correct_template_anonymous(self):
        """Test that the public URLs use correct HTML-templates."""
        for url, template in UserURLTests.public_url_template.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_private_urls_exist_authorised_user(self):
        """
        Test private URLs for password_change and
        password_reset_done for an authorised user.

        """
        for url in UserURLTests.private_url_template.keys():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_urls_redirect_anonymous_user(self):
        """
        Test URL redirection for password_change and
        password_reset_done for an anonymous user.

        """
        login_url = reverse(settings.LOGIN_URL)
        for url in UserURLTests.private_url_template.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'{login_url}?next={url}')

    def test_public_urls_use_correct_template_anonymous(self):
        """Test that the public urls use correct HTML-templates."""
        for url, template in UserURLTests.public_url_template.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_private_urls_use_correct_template_authorised(self):
        """Test that the private urls use correct HTML-templates."""
        for url, template in UserURLTests.private_url_template.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
