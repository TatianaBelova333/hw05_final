from django.contrib.auth import get_user_model
from django import forms

from core.utility.utils import hide_obscene_words
from .models import Post, Comment

User = get_user_model()


class PostForm(forms.ModelForm):
    """
    Form for authorised users to create or update a new post.

    """
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        error_messages = {
            'text': {'required': 'Кажется, Вы забыли что-то написать'}
        }

    @hide_obscene_words()
    def clean_text(self):
        data = self.cleaned_data['text']
        return data


class CommentForm(PostForm):
    """
    Form for authorised users to add comments to posts.

    """
    class Meta:
        model = Comment
        fields = ('text',)


class CommentAdminForm(CommentForm):
    class Meta:
        model = Comment
        fields = '__all__'
