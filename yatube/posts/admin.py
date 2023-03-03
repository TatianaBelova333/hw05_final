from django.contrib import admin
from django.contrib import messages
from django.core.exceptions import ValidationError

from posts.forms import CommentAdminForm

from .models import Post, Group, Comment, Follow


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'description',
    )
    list_display_links = ('title',)
    prepopulated_fields = {"slug": ("title",)}
    empty_value_display = '-пусто-'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
        'image',
    )
    search_fields = ('text',)
    list_filter = ('pub_date', 'author')
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'post'
    )
    search_fields = ('text',)
    list_filter = ('pub_date', 'post__id')
    form = CommentAdminForm


class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')

    def message_user(self, *args):
        pass

    def save_model(self, request, obj, form, change):
        try:
            super().save_model(request, obj, form, change)
        except ValidationError:
            messages.add_message(
                request,
                messages.INFO,
                'Пользователь не может подписаться на самого себя',
            )


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
