from datetime import datetime
from dateutil.tz import UTC


from django.contrib.auth import get_user_model
import factory
import factory.fuzzy

from posts.models import Group, Post, Comment, Follow
from core.models import ObsceneWord


User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Test class for User model"""

    class Meta:
        model = User

    first_name = "Vasily"
    last_name = "Ivanov"
    username = factory.Sequence(lambda n: f'user{n}')


class GroupFactory(factory.django.DjangoModelFactory):
    """Test class for Group model."""

    class Meta:
        model = Group

    title = factory.Sequence(lambda n: f'Литература{n}')
    description = 'Для любителей литературы'
    slug = factory.Sequence(lambda n: f'literatura{n}')


class PostFactory(factory.django.DjangoModelFactory):
    """Test class for Post model."""

    class Meta:
        model = Post

    text = factory.fuzzy.FuzzyText(prefix='Post', length=150)
    author = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    pub_date = factory.fuzzy.FuzzyDateTime(
        datetime(2008, 1, 1, tzinfo=UTC),
        datetime(2023, 2, 18, tzinfo=UTC)
    )
    image = factory.django.ImageField(color='blue', filename='example.jpg')


class CommentFactory(factory.django.DjangoModelFactory):
    """Test class for Comment model."""

    class Meta:
        model = Comment

    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)
    text = factory.Sequence(lambda n: f'коммент{n}')
    pub_date = factory.fuzzy.FuzzyDateTime(
        datetime(2008, 1, 1, tzinfo=UTC),
        datetime(2023, 2, 18, tzinfo=UTC)
    )


class ObsceneWordFactory(factory.django.DjangoModelFactory):
    """Test class for ObsceneWord model."""

    class Meta:
        model = ObsceneWord

    word = factory.Iterator(['кофе', 'утро', 'работа'])


class FollowFactory(factory.django.DjangoModelFactory):
    """Test class for Follow model."""

    class Meta:
        model = Follow

    user = factory.SubFactory(UserFactory)
