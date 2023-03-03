from django.db import models


class ObsceneWord(models.Model):
    """
    Words that must be censored in post texts.

    """
    word = models.CharField(
        max_length=25,
        verbose_name='Запрещенное слово',
        unique=True,
        error_messages={'unique': 'Такое слово уже есть.'}
    )

    class Meta:
        verbose_name = 'Запрещенное слово'
        verbose_name_plural = 'Запрещенные слова'
        ordering = ('word',)

    def __str__(self) -> str:
        return f'Запрещенное слово: {self.word}'

    def save(self, *args, **kwargs):
        """Make all words lowercase for convience."""
        self.word = self.word.lower()
        super().save(*args, **kwargs)
