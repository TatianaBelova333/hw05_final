from http import HTTPStatus

from django.urls import reverse
from django.test import TestCase, Client


class StaticPagesURLTests(TestCase):
    """Tests for the static pages of the about app."""

    def setUp(self):
        self.guest_client = Client()
        self.url_template = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def test_about_url_exists_at_desired_location(self):
        """Test the urls of the `about` app."""
        for url in self.url_template.keys():
            with self.subTest(url=url):
                self.assertEqual(
                    self.guest_client.get(url).status_code,
                    HTTPStatus.OK
                )

    def test_about_url_uses_correct_template(self):
        """Test the templates for the urls of the `about` app."""
        for url, template in self.url_template.items():
            with self.subTest(url=url, template=template):
                self.assertTemplateUsed(
                    self.guest_client.get(url),
                    template,
                )


class PagesViewsTests(TestCase):
    """Tests for the static pages of the about app."""

    def setUp(self):
        self.guest_client = Client()
        self.template_reverse_name = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech'),
        }

    def test_about_pages_accessible_by_name(self):
        """
        Test that the pages of the `about` app are accessible by their names.

        """
        for reverse_name in self.template_reverse_name.values():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(
                    self.guest_client.get(reverse_name).status_code,
                    HTTPStatus.OK
                )

    def test_about_pages_use_correct_template(self):
        """
        Test that the pages of the `about` app use the correct templates.

        """
        for template, reverse_name in self.template_reverse_name.items():
            with self.subTest(reverse_name=reverse_name, template=template):
                self.assertTemplateUsed(
                    self.guest_client.get(reverse_name),
                    template,
                )
