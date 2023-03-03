from django.utils import timezone


def year(request):
    """Add HTML template variable with the current year."""
    return {
        'year': timezone.now().year,
    }
