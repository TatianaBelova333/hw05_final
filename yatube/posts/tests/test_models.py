from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings
from django.core.exceptions import ValidationError

from posts.tests.factories import (GroupFactory, PostFactory, CommentFactory,
                                   UserFactory, FollowFactory)


User = get_user_model()


class GroupModelTests(TestCase):
    """Test suite for the Group model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = GroupFactory(
            title='Ж' * 100,
            slug=None,
        )

    def test_verbose_name(self):
        """Test that the field verbose_name is correct."""
        group = GroupModelTests.group

        field_verboses = {
            'title': 'Название',
            'slug': 'slug',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_object_name_is_text_field(self):
        """Test __str__ method of the Group model."""
        group = GroupModelTests.group
        expected_object_name = f'Группа: {group.title}'
        self.assertEqual(expected_object_name, str(group))

    def test_title_convert_to_slug(self):
        """Test that the title cyrillic value converts into slug."""
        group = GroupModelTests.group
        max_length_slug = group._meta.get_field('slug').max_length
        slug = group.slug
        self.assertEqual(slug, 'zh' * (int(max_length_slug / 2)))

    def test_title_slug_maximum_length(self):
        """
        Test that the slug length does not exceed the slug field max_length.

        """
        group = GroupModelTests.group
        max_length_slug = group._meta.get_field('slug').max_length
        length_slug = len(group.slug)
        self.assertGreaterEqual(max_length_slug, length_slug)


class PostModelTests(TestCase):
    """Test suite for the Post model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = PostFactory(image=None)

    def test_verbose_name(self):
        """Test that the field verbose_name is correct."""
        post = PostModelTests.post

        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
            'pub_date': 'Дата публикации',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_object_name_is_text_field(self):
        """Test __str__ method of the Post model."""
        post = PostModelTests.post
        limit = settings.TEXT_STR_LIMIT
        expected_object_name = post.text[:limit]
        self.assertEqual(expected_object_name, str(post))

    def test_ordering_by_pub_date_desc(self):
        """Test the ordering of posts by pub_date in descening order."""
        post = PostModelTests.post
        ordering = post._meta.ordering
        self.assertEqual(ordering[0], '-pub_date')


class CommentModelTests(TestCase):
    """Test suite for the Comment model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.comment = CommentFactory(post=PostFactory(image=None))

    def test_verbose_name(self):
        """Test that the field verbose_name is correct."""
        comment = CommentModelTests.comment

        field_verboses = {
            'text': 'Текст комментария',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'pub_date': 'Дата публикации',
            'post': 'Пост',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_object_name_is_text_field(self):
        """Test __str__ method of the Comment model."""
        comment = CommentModelTests.comment
        limit = settings.TEXT_STR_LIMIT
        expected_object_name = comment.text[:limit]
        self.assertEqual(expected_object_name, str(comment))

    def test_ordering_by_pub_date_desc(self):
        """Test the ordering of comments by pub_date in descening order."""
        comment = CommentModelTests.comment
        ordering = comment._meta.ordering
        self.assertEqual(ordering[0], '-pub_date')


class FollowModelTests(TestCase):
    """Test suite for the Follow model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = UserFactory()
        cls.author = UserFactory(username='AnotherUser')
        cls.follow = FollowFactory(
            user=cls.user,
            author=cls.author,
        )

    def test_verbose_name(self):
        """Test that the field verbose_name is correct."""
        follow = FollowModelTests.follow

        field_verboses = {
            'user': 'Пользователь',
            'author': 'Автор',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_user_author_fields_unique_together(self):
        """
        Test that the user and author fields are unique together.

        """
        with self.assertRaises(ValidationError):
            FollowFactory(
                user=FollowModelTests.user,
                author=FollowModelTests.author
            )

    def test_clean_method_user_cannot_follow_himself(self):
        with self.assertRaises(ValidationError):
            FollowFactory(
                user=FollowModelTests.user,
                author=FollowModelTests.user,
            )
