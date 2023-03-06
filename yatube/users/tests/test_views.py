from django.urls import reverse
from django.test import TestCase, Client
from django import forms

from posts.tests.factories import UserFactory


class UsersViewsTests(TestCase):
    """Tests for the pages of the users app."""

    def setUp(self):
        self.guest_client = Client()

        self.authorised_user = Client()
        self.authorised_user.force_login(UserFactory())

        self.public_tmpl_reverse_name = {
            'users/signup.html': reverse('users:signup'),
            'users/login.html': reverse('users:login'),
            'users/logged_out.html': reverse('users:logout'),
            'users/password_reset_done.html': reverse(
                'users:password_reset_done'),
            'users/password_reset_form.html': reverse(
                'users:password_reset'),

        }
        self.private_tmpl_reverse_name = {
            'users/password_change_form.html': reverse(
                'users:password_change'),
            'users/password_change_done.html': reverse(
                'users:password_change_done'),
        }

    def test_public_users_pages_use_correct_template(self):
        """
        Test that the pages of the `users` app use the correct templates.

        """
        for template, reverse_name in self.public_tmpl_reverse_name.items():
            with self.subTest(reverse_name=reverse_name, template=template):
                self.assertTemplateUsed(
                    self.guest_client.get(reverse_name),
                    template,
                )

    def test_private_users_pages_use_correct_template(self):
        """
        Test that the pages of the `users` app use the correct templates.

        """
        for template, reverse_name in self.private_tmpl_reverse_name.items():
            with self.subTest(reverse_name=reverse_name, template=template):
                self.assertTemplateUsed(
                    self.authorised_user.get(reverse_name),
                    template,
                )

    def test_user_signup_context(self):
        """
        Test that the HTML-template for signup page
        uses correct context.

        """
        reverse_name = reverse('users:signup')
        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.CharField,
            'password1': forms.CharField,
            'password2': forms.CharField,
        }

        response = self.authorised_user.get(reverse_name)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
