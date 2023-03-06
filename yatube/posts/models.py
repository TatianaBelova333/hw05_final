from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from pytils.translit import slugify

User = get_user_model()


class TextBaseModel(models.Model):
    """
    Abstract text class.

    """
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True,
    )
    text = models.TextField()

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        limit = settings.TEXT_STR_LIMIT
        return self.text[:limit]


class Group(models.Model):
    """
    A group for creating posts according to bloggers' interests.

    """
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        unique=True,
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name='slug',
        blank=True,
    )
    description = models.TextField(verbose_name='Описание')

    class Meta:
        verbose_name = 'Сообщество'
        verbose_name_plural = 'Сообщества'

    def __str__(self) -> str:
        return f'Группа: {self.title}'

    def save(self, *args, **kwargs):
        """
        Create slug from the title field value
        truncated to the max_length specified by the slug field
        if the slug field left blank.

        """
        if not self.slug:
            max_length = Group._meta.get_field('slug').max_length
            self.slug = slugify(self.title)[:max_length]
        super().save(*args, **kwargs)


class Post(TextBaseModel):
    """
    Posts created by bloggers, related to :model:`posts.Group`.

    """
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст нового поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta(TextBaseModel.Meta):
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(TextBaseModel):
    """Comments to the posts."""
    post = models.ForeignKey(
        Post,
        verbose_name='Пост',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст нового комментария',
    )

    class Meta(TextBaseModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    """
    Model for users following other users.

    """
    is_cleaned = False

    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )

    class Meta:
        unique_together = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        user_name = self.user.get_username()
        author_name = self.author.get_username()
        return f'{user_name} - {author_name}'

    def clean(self):
        """
        Raise ValidatioError if the user and the author are
        the same User instance.

        """
        self.is_cleaned = True
        if self.user == self.author:
            raise ValidationError(
                'Пользователь не может подписаться на самого себя'
            )
        super(Follow, self).clean()

    def save(self, *args, **kwargs):
        """
        Does not save an Follow instance if the user and the author are
        the same User instance.

        """
        if not self.is_cleaned:
            self.full_clean()
        super(Follow, self).save(*args, **kwargs)
