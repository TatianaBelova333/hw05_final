from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.core.exceptions import PermissionDenied

from core.utility.utils import get_page_obj, remove_hashtag_links
from .forms import PostForm, CommentForm
from .models import Group, Post, Follow

User = get_user_model()


def index(request):
    """
    Display the index page with posts (:model:`posts.Post` instances)
    filtered by publication date(desc) with 10 ea. per page.

    """
    template = 'posts/index.html'

    post_list = Post.objects.select_related('author', 'group').all()
    page_obj = get_page_obj(request=request, obj=post_list)

    context = {'page_obj': page_obj}

    return render(
        request=request,
        template_name=template,
        context=context,
    )


#  ради эксперимента
def hashtag_posts(request, hashtag):
    """
    Display posts by hashtags.

    """
    template = 'posts/hashtag_index.html'
    post_list = Post.objects.select_related(
        'author', 'group'
    ).filter(text__icontains=f'#{hashtag}').all()
    page_obj = get_page_obj(request=request, obj=post_list)

    return render(
        request=request,
        template_name=template,
        context={
            'page_obj': page_obj,
            'hashtag': hashtag,
        },
    )


def group_posts(request, slug):
    """
    Display posts (:model:`posts.Post` instances) filtered
    by pulication date(desc) that belong to a particular group
    (:model:`posts.Group` instance).

    Args:
        slug(str): the slug of a particular :model:`posts.Group` instance.

    """
    template = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    page_obj = get_page_obj(request=request, obj=post_list)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(
        request=request,
        template_name=template,
        context=context,
    )


def profile(request, username):
    """
    Display all posts (:model:`posts.Post` instances) filtered
    by group (:model:`posts.Group` instance).

    Args:
        slug(str): the slug of an individual :model:`posts.Group` instance.

    """
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    author_posts = author.posts.select_related('group').all()
    page_obj = get_page_obj(request=request, obj=author_posts)

    following = request.user.is_authenticated and Follow.objects.filter(
        user=request.user, author=author).exists()

    context = {
        'author': author,
        'page_obj': page_obj,
        'following': following,
    }
    return render(
        request=request,
        template_name=template,
        context=context,
    )


def post_detail(request, post_id):
    """
    Display page with information about a particular post.

    Args:
        post_id(int): :model:`posts.Post` instance pk.

    """
    template = 'posts/post_detail.html'
    form = CommentForm()
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        pk=post_id,
    )
    comments = post.comments.select_related('author').all()

    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(
        request=request,
        template_name=template,
        context=context,
    )


@login_required
def post_create(request):
    """
    Create a new Post instance (:model:`posts.Post`) by an authorised user.

    """
    template = 'posts/create_post.html'
    user = request.user

    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.author = user
        instance.save()
        return redirect(
            'posts:profile',
            username=user.username,
        )
    return render(
        request=request,
        template_name=template,
        context={'form': form}
    )


@login_required
def post_edit(request, post_id):
    """
    Update a particular Post instance (:model:`posts.Post`)
    by the post onwer.

    """
    template = 'posts/update_post.html'
    post = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        pk=post_id
    )
    post.text = remove_hashtag_links(post.text)
    if request.user != post.author:
        raise PermissionDenied()

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post.save()
        return redirect(
            'posts:post_detail',
            post_id=post_id,
        )

    return render(
        request=request,
        template_name=template,
        context={'form': form},
    )


@login_required
def add_comment(request, post_id):
    """
    Add comments to posts by authoorised users.

    """
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect(
        'posts:post_detail',
        post_id=post_id
    )


@login_required
def follow_index(request):
    """
    Display list with posts of the authors followed by the request user.

    """
    current_user = request.user
    post_list = Post.objects.select_related(
        'author', 'group'
    ).filter(author__following__user=request.user)

    page_obj = get_page_obj(request=request, obj=post_list)

    context = {
        'page_obj': page_obj,
        'user': current_user,
    }
    return render(
        request=request,
        template_name='posts/follow.html',
        context=context,
    )


@login_required
def profile_follow(request, username):
    """
    Add post author to the request user's subscriptions.

    """
    author = get_object_or_404(User, username=username)
    user = request.user
    if user != author:
        Follow.objects.get_or_create(user=request.user, author=author)

    return redirect(
        'posts:profile',
        username=username,
    )


@login_required
def profile_unfollow(request, username):
    """
    Remove post author from the request user's subscriptions.

    """
    author = get_object_or_404(User, username=username)
    author_followers = Follow.objects.filter(
        author=author,
    ).values_list('user', flat=True)
    if request.user.pk in author_followers:
        Follow.objects.filter(user=request.user, author=author).delete()

    return redirect(
        'posts:profile',
        username=username,
    )
