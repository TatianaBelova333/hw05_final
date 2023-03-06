from http import HTTPStatus
import shutil
import tempfile

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile

from posts.forms import PostForm, CommentForm
from posts.tests.factories import (PostFactory, GroupFactory,
                                   ObsceneWordFactory, UserFactory)
from posts.models import Post, Comment


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    """Test suite for the PostForm form."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = PostFactory()
        cls.group = GroupFactory()
        cls.user = cls.post.author
        cls.another_user = UserFactory()
        cls.form = PostForm()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        ObsceneWordFactory.create_batch(size=3)

    def setUp(self):
        self.guest_user = Client()

        self.authorised_post_author = Client()
        self.authorised_post_author.force_login(PostFormTests.user)

        self.authorised_user = Client()
        self.authorised_user.force_login(PostFormTests.another_user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_empty_post_form(self):
        """Tests that the empty PostForm form has the required fields."""
        form = PostFormTests.form
        self.assertIn('text', form.fields)
        self.assertIn('group', form.fields)
        self.assertNotIn('id', form.fields)
        self.assertNotIn('author', form.fields)

    def test_create_post_success(self):
        """
        Test that a valid PostForm form creates a new post
        with the required text field and optional group field.

        """
        small_gif = PostFormTests.small_gif
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        start_time = timezone.now()
        forms_data = {
            'with_group': {
                'text': 'Тестовый текст',
                'group': PostFormTests.group.id,
            },
            'without_group': {
                'text': 'Другой Тестовый текст',
            },
            'with_image': {
                'text': 'Еще один текст поста',
                'group': PostFormTests.group.id,
                'image': uploaded,
            },
        }
        for form_data in forms_data.values():
            with self.subTest(form_data=form_data):
                post_count = Post.objects.count()
                response = self.authorised_user.post(
                    reverse('posts:post_create'),
                    data=form_data,
                    follow=True,
                )
                self.assertRedirects(
                    response,
                    reverse(
                        'posts:profile',
                        kwargs={
                            'username': PostFormTests.another_user.username,
                        },
                    )
                )
                self.assertEqual(Post.objects.count(), post_count + 1)

                self.assertTrue(
                    Post.objects.filter(
                        text=form_data['text'],
                        group=form_data.get('group'),
                        author=PostFormTests.another_user,
                        pub_date__range=(start_time, timezone.now()),
                        image=(f'posts/{uploaded.name}'
                               if form_data.get('image') else ''),
                    ).exists()
                )

    def test_clean_text_create_post(self):
        """
        Test that the forbidden words are hidden with grawlix in post texts.

        """
        grawlix = settings.GRAWLIX

        original_text = 'Утро начинается с кофе.'
        censored_text = f'{grawlix} начинается с {grawlix}.'

        form_data = {
            'text': original_text,
        }
        self.authorised_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertTrue(
            Post.objects.filter(
                text=censored_text,
                group=form_data.get('group'),
                author=PostFormTests.another_user,
            ).exists()
        )

    def test_create_post_form_blank_fields(self):
        """Test the PostForm with fields left blank."""
        forms_data = {
            'with_group': {
                'group': PostFormTests.group.id,
            },
            'without_group': {
                'text': '',
            },
        }
        for form_data in forms_data.values():
            with self.subTest(form_data=form_data):
                post_count = Post.objects.count()
                response = self.authorised_user.post(
                    reverse('posts:post_create'),
                    data=form_data,
                    follow=True,
                )
                self.assertEqual(Post.objects.count(), post_count)
                self.assertFormError(
                    response,
                    'form',
                    'text',
                    'Кажется, Вы забыли что-то написать',
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_update_post_form_success(self):
        """Test that a valid PostForm form updates an exisiting post."""
        post_to_update = PostFormTests.post
        updated_text = 'Тестовый текст для проверки обновления поста'
        updated_group = GroupFactory()

        small_gif = PostFormTests.small_gif
        uploaded = SimpleUploadedFile(
            name='small_1.gif',
            content=small_gif,
            content_type='image/gif'
        )

        form_data = {
            'text': updated_text,
            'group': updated_group.id,
            'image': uploaded,
        }
        response = self.authorised_post_author.post(
            reverse('posts:post_edit', kwargs={'post_id': post_to_update.id}),
            data=form_data,
            follow=True,
        )

        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post_to_update.id},
            )
        )
        self.assertTrue(
            Post.objects.filter(
                id=post_to_update.id,
                author=post_to_update.author,
                text=updated_text,
                group=updated_group,
                pub_date=post_to_update.pub_date,
                image=f'posts/{uploaded.name}',
            ).exists()
        )

    def test_post_create_form_by_unauthorised_user(self):
        """Test that an unauthorised user cannot create a new post."""
        post_count_before = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': GroupFactory(),
        }
        response = self.guest_user.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_count_after = Post.objects.count()
        redirect_path = ''.join(
            (reverse('users:login'),
             '?next=',
             reverse('posts:post_create'))
        )

        self.assertRedirects(
            response,
            redirect_path,
        )
        self.assertEqual(post_count_before, post_count_after)

    def test_post_update_form_by_unauthorised_user(self):
        """Test that an unauthorised user cannot update an existing post."""
        post_to_update = PostFormTests.post

        small_gif = PostFormTests.small_gif
        uploaded = SimpleUploadedFile(
            name='small_2.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост',
            'group': GroupFactory(),
            'image': uploaded,
        }
        response = self.guest_user.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': post_to_update.id}
            ),
            data=form_data,
            follow=True,
        )

        redirect_path = ''.join(
            (reverse('users:login'),
             '?next=',
             reverse('posts:post_edit', kwargs={'post_id': post_to_update.id}))
        )

        post_attempted_update = Post.objects.get(pk=post_to_update.id)

        data = (
            (post_to_update.text, post_attempted_update.text),
            (post_to_update.group, post_attempted_update.group),
            (post_to_update.pub_date, post_attempted_update.pub_date),
            (post_to_update.author, post_attempted_update.author),
            (post_to_update.image, post_attempted_update.image)
        )

        self.assertRedirects(
            response,
            redirect_path,
        )

        for post_to_update, post_attempted_update in data:
            with self.subTest(post_to_update=post_to_update,
                              post_attempted_update=post_attempted_update):
                self.assertEqual(post_to_update, post_attempted_update)

    def test_post_update_form_by_not_post_author(self):
        """Test that an authorised user cannot update posts of other users."""
        post_to_update = PostFormTests.post

        small_gif = PostFormTests.small_gif
        uploaded = SimpleUploadedFile(
            name='small_3.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост',
            'group': GroupFactory(),
            'image': uploaded,
        }

        self.authorised_user.post(
            reverse(
                'posts:post_edit', kwargs={'post_id': post_to_update.id}
            ),
            data=form_data,
            follow=True,
        )
        post_attempted_update = Post.objects.get(pk=post_to_update.id)

        data = (
            (post_to_update.text, post_attempted_update.text),
            (post_to_update.group, post_attempted_update.group),
            (post_to_update.pub_date, post_attempted_update.pub_date),
            (post_to_update.author, post_attempted_update.author),
            (post_to_update.image, post_attempted_update.image),
        )

        for post_to_update, post_attempted_update in data:
            with self.subTest(post_to_update=post_to_update,
                              post_attempted_update=post_attempted_update):
                self.assertEqual(post_to_update, post_attempted_update)


class CommentFormTests(TestCase):
    """Test suite for the CommentForm form."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.post = PostFactory(text='Пост', image=None)
        cls.user = UserFactory(username='Noname')
        cls.form = CommentForm()
        ObsceneWordFactory.create_batch(size=3)

    def setUp(self):
        self.guest_user = Client()

        self.authorised_user = Client()
        self.authorised_user.force_login(CommentFormTests.user)

    def test_empty_post_form(self):
        """Tests that the empty CommentForm form has the required fields."""
        form = CommentFormTests.form
        self.assertIn('text', form.fields)
        self.assertNotIn('id', form.fields)
        self.assertNotIn('author', form.fields)

    def test_comment_create_form_by_unauthorised_user(self):
        """
        Test that an unauthorised user cannot leave comments to posts.

        """
        post = CommentFormTests.post
        comment_count_before = post.comments.count()

        form_data = {
            'text': 'Тестовый коментарий',
        }
        response = self.guest_user.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True,
        )
        redirect_path = ''.join(
            (reverse('users:login'),
             '?next=',
             reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id},
            ))
        )

        self.assertRedirects(
            response,
            redirect_path,
        )
        self.assertEqual(post.comments.count(), comment_count_before)

    def test_comment_create_form_by_authorised_user(self):
        """
        Test that an authorised user can leave comments to posts.

        """
        author = CommentFormTests.user
        post = CommentFormTests.post
        comment_count_before = post.comments.count()
        start_time = timezone.now()

        form_data = {
            'text': 'Тестовый коментарий',
        }
        response = self.authorised_user.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True,
        )
        redirect_path = reverse(
            'posts:post_detail',
            kwargs={'post_id': post.id},
        )

        self.assertRedirects(
            response,
            redirect_path,
        )
        self.assertEqual(post.comments.count(), comment_count_before + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=post,
                text=form_data['text'],
                author=author,
                pub_date__range=(start_time, timezone.now()),
            ).exists()
        )

    def test_clean_text_create_comment(self):
        """
        Test that the forbidden words are hidden with grawlix in comments.

        """
        author = CommentFormTests.user
        post = CommentFormTests.post
        grawlix = settings.GRAWLIX

        original_text = 'Утро начинается с кофе.'
        censored_text = f'{grawlix} начинается с {grawlix}.'

        form_data = {
            'text': original_text,
        }
        self.authorised_user.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': post.id}
            ),
            data=form_data,
            follow=True,
        )
        self.assertTrue(
            Comment.objects.filter(
                text=censored_text,
                author=author,
                post=post,
            ).exists()
        )
