from random import randrange
import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django import forms
from django.core.cache import cache

from posts.tests.factories import (PostFactory, UserFactory, GroupFactory,
                                   CommentFactory, FollowFactory)
from posts.models import Post, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    """Tests for the views of the `post` app."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.another_user = UserFactory(username='OtherUser')
        cls.another_group = GroupFactory(title='hobby')
        cls.post = PostFactory()
        PostFactory.create_batch(size=5, author=cls.post.author)
        PostFactory.create_batch(
            size=5,
            author=cls.another_user,
            group=cls.another_group,
        )
        CommentFactory.create_batch(size=2, post=cls.post)
        CommentFactory.create_batch(
            size=3, post=PostFactory(text='another post')
        )
        FollowFactory(user=cls.another_user, author=cls.post.author)
        FollowFactory(user=cls.another_user, author=UserFactory())
        FollowFactory(user=cls.post.author, author=cls.another_user)

        cls.public_tmpl_view = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_posts',
                kwargs={'slug': PostPagesTests.post.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.another_user.username}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.pk}
            ),
        }
        cls.private_tmpl_view = {
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/update_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.pk}
            ),
            'posts/follow.html': reverse('posts:follow_index'),
        }

    def setUp(self):
        cache.clear()
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.another_user)

        self.authorized_post_author = Client()
        self.authorized_post_author.force_login(PostPagesTests.post.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_public_views_use_correct_template_anonymous(self):
        """Test that the public pages use correct HTML-templates."""
        for template, reverse_name in PostPagesTests.public_tmpl_view.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_private_views_use_correct_template(self):
        """Test that the private pages use correct HTML-templates."""
        for template, reverse_name in PostPagesTests.private_tmpl_view.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_post_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_context(self):
        """
        Test that the HTML-template for the index page
        uses correct context.

        """
        post = Post.objects.order_by('-pub_date').first()
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        data = (
            (first_object.text, post.text),
            (first_object.pub_date, post.pub_date),
            (first_object.author, post.author),
            (first_object.image, post.image),
            (first_object.group, post.group),
        )
        for actual_value, expected_value in data:
            with self.subTest(
                actual_value=actual_value,
                expected_value=expected_value
            ):
                self.assertEqual(actual_value, expected_value)

    def test_group_posts_page_context(self):
        """
        Test that the HTML-template for the index page
        uses correct context.

        """
        page_group = PostPagesTests.another_group
        first_post_on_page = Post.objects.filter(
            group=page_group
        ).order_by('-pub_date').first()

        response = self.guest_client.get(
            reverse(
                'posts:group_posts',
                kwargs={'slug': page_group.slug})
        )

        page_obj = response.context['page_obj']
        group = response.context['group']
        first_object = page_obj[0]
        data = (
            (first_object.text, first_post_on_page.text),
            (first_object.pub_date, first_post_on_page.pub_date),
            (first_object.author, first_post_on_page.author),
            (first_object.group, first_post_on_page.group),
            (first_object.image, first_post_on_page.image),
            (group, page_group),
        )
        self.assertTrue(
            all(map(lambda post: post.group == page_group, page_obj)),
            'На странице должны быть посты только одной группы',
        )
        for actual_value, expected_value in data:
            with self.subTest(
                actual_value=actual_value,
                expected_value=expected_value
            ):
                self.assertEqual(actual_value, expected_value)

    def test_profile_page_context(self):
        """
        Test that the HTML-template for the profile page
        uses correct context.

        """
        profile_user = PostPagesTests.another_user
        first_post_on_page = (Post.objects.filter(author=profile_user).
                              order_by('-pub_date').first())
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': profile_user.username})
        )
        page_obj = response.context['page_obj']
        author = response.context['author']
        first_object = page_obj[0]
        data = (
            (first_object.text, first_post_on_page.text),
            (first_object.pub_date, first_post_on_page.pub_date),
            (first_object.author, first_post_on_page.author),
            (first_object.group, first_post_on_page.group),
            (first_object.image, first_post_on_page.image),
            (author, profile_user),
        )
        self.assertTrue(
            all(map(lambda post: post.author == profile_user, page_obj)),
            'На странице должны быть посты только одного авторы',
        )
        for actual_value, expected_value in data:
            with self.subTest(
                actual_value=actual_value,
                expected_value=expected_value
            ):
                self.assertEqual(actual_value, expected_value)

    def test_post_detail_page_context(self):
        """
        Test that the HTML-template for the post_detail page
        use correct context.

        """
        detailed_post = PostPagesTests.post

        reverse_name = reverse(
            'posts:post_detail',
            kwargs={'post_id': PostPagesTests.post.pk}
        )
        response = self.guest_client.get(reverse_name)

        post_context = response.context['post']
        form_context = response.context['form']
        comments_context = response.context['comments']

        data = (
            (detailed_post.text, post_context.text),
            (detailed_post.pub_date, post_context.pub_date),
            (detailed_post.author, post_context.author),
            (detailed_post.group, post_context.group),
            (detailed_post.image, post_context.image),
            (list(detailed_post.comments.all()), list(comments_context)),

        )
        self.assertTrue(
            all(map(
                lambda comment: comment.post == detailed_post, comments_context
            )),
            'На странице должны быть комментарии к одному посту',
        )
        self.assertIsInstance(
            form_context.fields['text'], forms.fields.CharField
        )

        for actual_value, expected_value in data:
            with self.subTest(
                actual_value=actual_value,
                expected_value=expected_value
            ):
                self.assertEqual(actual_value, expected_value)

    def test_post_create_update_pages_context(self):
        """
        Test that the HTML-template for the post_edit and post_create pages
        use correct context.

        """
        reverse_names = (
            reverse('posts:post_create'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.pk})
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for url in reverse_names:
            response = self.authorized_post_author.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value, url=url):
                    form_field = response.context['form'].fields[value]
                    self.assertIsInstance(form_field, expected)

    def test_created_post_appear_on_public_pages(self):
        """
        Test that the created post appear on public pages.

        """
        group = PostPagesTests.another_group
        user = PostPagesTests.another_user

        new_post = PostFactory(
            text='Новый пост',
            group=group,
            author=user,
        )
        reverse_names = [
            reverse('posts:index'),
            reverse(
                'posts:group_posts',
                kwargs={'slug': group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': user.username}
            ),
        ]

        for reverse_name in reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(new_post, response.context['page_obj'][0])

    def test_created_comment_appear_on_post_detail_page(self):
        """
        Test that the created comment appear on post_detail page.

        """
        post = PostPagesTests.post
        user = PostPagesTests.another_user

        new_comment = CommentFactory(
            text='Новый комментарий',
            post=post,
            author=user,
        )
        reverse_name = reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id}
        )

        response = self.authorized_client.get(reverse_name)
        self.assertEqual(new_comment, response.context['comments'][0])

    def test_follow_index_page_context(self):
        """
        Test follow_index page context.

        """
        user = PostPagesTests.another_user

        followed_authors = Follow.objects.filter(
            user=user).values_list('author', flat=True)

        first_post_on_page = Post.objects.filter(
            author__in=followed_authors).order_by('-pub_date').first()
        reverse_name = reverse('posts:follow_index')
        response = self.authorized_client.get(reverse_name)
        page_obj = response.context['page_obj']
        context_user = response.context['user']
        first_object = page_obj[0]

        data = (
            (first_object.text, first_post_on_page.text),
            (first_object.pub_date, first_post_on_page.pub_date),
            (first_object.author, first_post_on_page.author),
            (first_object.group, first_post_on_page.group),
            (first_object.image, first_post_on_page.image),
            (user, context_user),
        )
        self.assertTrue(
            all(map(
                lambda post: post.author.id in followed_authors, page_obj
            )),
            ('На странице должны быть посты только тех авторов,'
             'на которых подписан пользователь'),
        )
        for actual_value, expected_value in data:
            with self.subTest(
                actual_value=actual_value,
                expected_value=expected_value
            ):
                self.assertEqual(actual_value, expected_value)

    def test_created_post_appear_in_followers_feed(self):
        """
        Test that the created post appears on the author's follower's
        follow_index page.

        """
        author = PostPagesTests.post.author

        new_post = PostFactory(
            text='Пост для подписчиков',
            author=author,
        )

        reverse_name = reverse('posts:follow_index')
        response = self.authorized_client.get(reverse_name)
        self.assertEqual(new_post, response.context['page_obj'][0])

    def test_created_post_does_not_appear_in_not_follower_feed(self):
        """
        Test that the created post does not appear on the
        follow_index page of users who do not follow the author.

        """
        author = PostPagesTests.post.author
        not_follower = UserFactory(username='not_a_follower')

        new_post = PostFactory(
            text='Пост для неподписчиков',
            author=author,
        )

        reverse_name = reverse('posts:follow_index')
        not_follower_authorised = Client()
        not_follower_authorised.force_login(not_follower)

        response = not_follower_authorised.get(reverse_name)
        self.assertNotIn(new_post, response.context['page_obj'])

    def test_profile_follow_page(self):
        """
        Test that an authorised user can start following an author.

        """
        author = UserFactory(username='new_author')
        user = PostPagesTests.another_user
        user_subscriptions_total = user.follower.count()

        reverse_name = reverse(
            'posts:profile_follow',
            kwargs={'username': author.username}
        )
        self.authorized_client.get(reverse_name)
        self.assertEqual(user.follower.count(), user_subscriptions_total + 1)
        self.assertIn(author, (obj.author for obj in user.follower.all()))

    def test_profile_unfollow_page(self):
        """
        Test that an authorised user can start unfollowing an author.

        """
        author = UserFactory(username='followed_author')
        user = PostPagesTests.another_user
        FollowFactory(user=user, author=author)
        user_subscriptions_total = user.follower.count()

        reverse_name = reverse(
            'posts:profile_unfollow',
            kwargs={'username': author.username}
        )
        self.authorized_client.get(reverse_name)
        self.assertEqual(user.follower.count(), user_subscriptions_total - 1)
        self.assertNotIn(author, (obj.author for obj in user.follower.all()))

    def test_authorised_user_cannot_follow_himself(self):
        """
        Test that an authorised user cannot start following himself.

        """
        user = PostPagesTests.another_user
        user_subscriptions_total = user.follower.count()

        reverse_name = reverse(
            'posts:profile_follow',
            kwargs={'username': user.username}
        )
        self.authorized_client.get(reverse_name)
        self.assertEqual(user.follower.count(), user_subscriptions_total)
        self.assertNotIn(user, (obj.author for obj in user.follower.all()))


class PaginatorViewsTests(TestCase):
    """Test suite for the paginator."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.posts_num_on_page = settings.TOTAL_ON_PAGE
        cls.extra_num = randrange(1, cls.posts_num_on_page)
        cls.batch_size = cls.posts_num_on_page + cls.extra_num

        cls.group = GroupFactory()
        cls.user = UserFactory()
        cls.another_user = UserFactory(username='another_user')
        cls.posts = PostFactory.create_batch(
            size=cls.batch_size,
            group=cls.group,
            author=cls.another_user,
        )
        FollowFactory(user=cls.user, author=cls.another_user)

        cls.reverse_names = (
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': cls.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': cls.another_user.username}
            ),
            reverse('posts:follow_index'),
        )

    def setUp(self):
        cache.clear()

        self.authorised_client = Client()
        self.authorised_client.force_login(PaginatorViewsTests.user)

    # если убрать этот класс, в репозитории появляются временные файлы
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_views_first_page(self):
        """
        Test that the first page of the index, group_posts, and profile views
        contains the default number of posts.

        """
        for reverse_name in PaginatorViewsTests.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    PaginatorViewsTests.posts_num_on_page,
                )

    def test_views_second_page(self):
        """
        Test the second page of the index, group_posts, and profile views
        contains the correct number of posts.

        """
        for reverse_name in PaginatorViewsTests.reverse_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorised_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    PaginatorViewsTests.extra_num,
                )


class CacheIndexPageTests(TestCase):
    """Test suite for the index page cache."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory(username='random_user')
        cls.group = GroupFactory()
        PostFactory.create_batch(
            size=15, author=cls.user, group=cls.group, image=None,
        )
        cls.post_to_be_deleted = PostFactory(
            text='TO BE DELETED',
            author=cls.user,
            group=cls.group,
            image=None,
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorised_client = Client()
        self.authorised_client.force_login(CacheIndexPageTests.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_deleted_data_remain_chached(self):
        """
        Test that after deleting a post, it is saved in cache
        until cache has been cleared.

        """
        first_response = self.guest_client.get(reverse('posts:index'))
        Post.objects.get(pk=self.post_to_be_deleted.pk).delete()
        second_response = self.guest_client.get(reverse('posts:index'))
        cache.clear()
        third_response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(first_response.content, second_response.content)
        self.assertNotEqual(first_response.content, third_response.content)

    def test_different_pages_return_different_cached_content(self):
        """
        Test that different pages return different cached content.

        """
        first_page_response = self.guest_client.get(reverse('posts:index'))
        second_page_response = self.guest_client.get(
            reverse('posts:index') + '?page=2',
        )
        self.assertNotEqual(
            first_page_response.content,
            second_page_response.content,
        )

    def test_different_users_get_different_cached_content(self):
        """
        Test that different users get different cached content.

        """
        unauthorised_response = self.guest_client.get(reverse('posts:index'))
        authorised_response = self.authorised_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(
            unauthorised_response.content,
            authorised_response.content,
        )
