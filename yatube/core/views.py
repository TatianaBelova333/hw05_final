from http import HTTPStatus
from django.shortcuts import render


def page_not_found(request, exception):
    """Custom 404-page."""
    return render(
        request=request,
        template_name='core/404.html',
        status=HTTPStatus.NOT_FOUND,
    )


def csrf_failure(request, reason=''):
    """Custom crf-failure page."""
    return render(
        request=request,
        template_name='core/403csrf.html',
    )


def permission_denied(request, exception):
    """Custom 403-page."""
    return render(
        request=request,
        template_name='core/403.html',
        status=HTTPStatus.FORBIDDEN,
    )


def server_failure(request, exception):
    """Custom 500-page."""
    return render(
        request=request,
        template_name='core/500.html',
        status=HTTPStatus.BAD_REQUEST,
    )
