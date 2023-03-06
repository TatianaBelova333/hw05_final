from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from users.forms import CreationForm
from posts.tests.factories import UserFactory

User = get_user_model()


class CreationFormTests(TestCase):
    """Test suite for the CreationForm form."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()

    def setUp(self):
        self.guest_user = Client()

        self.authorised_user = Client()
        self.authorised_user.force_login(UserFactory())

    def test_empty_creation_form(self):
        """Tests that the empty CreationForm form has the required fields."""
        form = CreationFormTests.form
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('username', form.fields)
        self.assertIn('email', form.fields)

    def test_sign_up_new_user_success(self):
        """
        Test that a valid CreationForm form creates a new user.

        """
        forms_data = {
            'required_fields': {
                'username': 'user89',
                'password1': 'Xfrwdooo1947',
                'password2': 'Xfrwdooo1947',
                'first_name': '',
                'last_name': '',
                'email': '',
            },
            'all_fields': {
                'username': 'user2',
                'first_name': 'Liza',
                'last_name': 'Kudrow',
                'email': 'liza34@mail.ru',
                'password1': 'Xfrwdooo1956',
                'password2': 'Xfrwdooo1956',
            },
        }
        for form_data in forms_data.values():
            with self.subTest(form_data=form_data):
                user_count = User.objects.count()
                response = self.guest_user.post(
                    reverse('users:signup'),
                    data=form_data,
                    follow=True,
                )
                self.assertEqual(User.objects.count(), user_count + 1)

                self.assertRedirects(
                    response,
                    reverse('posts:index'),
                )

                self.assertTrue(
                    User.objects.filter(
                        username=form_data['username'],
                        first_name=form_data.get('first_name'),
                        last_name=form_data.get('last_name'),
                        email=form_data.get('email'),
                    ).exists()
                )
