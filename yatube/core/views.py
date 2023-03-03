from django.shortcuts import render


def page_not_found(request, exception):
    """Custom 404-page."""
    return render(
        request=request,
        template_name='core/404.html',
        context={'path': request.path},
        status=404,
    )


def csrf_failure(request, reason=''):
    return render(
        request=request,
        template_name='core/403csrf.html',
    )
