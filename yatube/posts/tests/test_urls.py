from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
from django.core.cache import cache

from posts.tests.factories import PostFactory, UserFactory


class PostURLTests(TestCase):
    """Tests for the URLs of the `posts` app."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.other_user = UserFactory(username='OtherUser')
        cls.post = PostFactory(image=None)

        cls.public_url_template = {
            '/': 'posts/index.html',
            f'/group/{cls.post.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.other_user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }

        cls.private_url_template = {
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.pk}/edit/': 'posts/update_post.html',
            '/follow/': 'posts/follow.html',   # тесты для follow тоже есть
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.other_user)

        self.authorized_post_author = Client()
        self.authorized_post_author.force_login(PostURLTests.post.author)

    def test_public_urls_exist_anonymous(self):
        """Test public URLs of the `posts` app for an anonymous user."""

        for url in PostURLTests.public_url_template.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_urls_exist_authorised_post_author(self):
        """
        Test URLs for updating and creating posts by an authorised user.

        """
        for url in PostURLTests.private_url_template.keys():
            with self.subTest(url=url):
                response = self.authorized_post_author.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_urls_redirect_anonymous_on_login(self):
        """
        Test URL redirection for updating and creating posts
        by an anonymous user.

        """
        login_url = reverse(settings.LOGIN_URL)
        for url in PostURLTests.private_url_template.keys():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'{login_url}?next={url}')

    def test_add_comment_url_redirect_unathorised(self):
        """
        Test URL redirection of the add_commment url
        for an unauthorised user.

        """
        login_url = reverse(settings.LOGIN_URL)
        url = f'/posts/{PostURLTests.post.pk}/comment/'
        response = self.guest_client.get(url, follow=True)
        self.assertRedirects(response, f'{login_url}?next={url}')

    def test_add_comment_url_redirect_authorised(self):
        """
        Test URL redirection of the add_commment url
        for an authorised user.

        """
        url = f'/posts/{PostURLTests.post.pk}/comment/'
        redirect_url = f'/posts/{PostURLTests.post.pk}/'
        response = self.authorized_client.get(url, follow=True)
        self.assertRedirects(response, redirect_url)

    def test_public_urls_use_correct_template_anonymous(self):
        """Test that the public urls use correct HTML-templates."""
        for url, template in PostURLTests.public_url_template.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_private_urls_use_correct_template_post_author(self):
        """Test that the private urls use correct HTML-templates."""
        for url, template in PostURLTests.private_url_template.items():
            with self.subTest(url=url):
                response = self.authorized_post_author.get(url)
                self.assertTemplateUsed(response, template)

    def test_post_edit_url_forbidden_status_not_author(self):
        """
        Test post_edit url by not post author raises 403 error
        and returns a custom 403 page.

        """
        post_edit_url = f'/posts/{PostURLTests.post.pk}/edit/'
        template = 'core/403.html'
        response = self.authorized_client.get(post_edit_url, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertTemplateUsed(response, template)

    def test_invalid_url_use_custom_404page(self):
        """
        Test that an invalid URL returns a 404 custom page.
        """
        invalid_url = '/unexisting-page/'
        template = 'core/404.html'
        response = self.guest_client.get(invalid_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, template)
