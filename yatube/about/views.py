from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """
    Return page with information about the author of the project.

    """
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """
    Return page with information about techologies
    used for creating the project.

    """
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tools"] = [
            'Python 3.9',
            'Django 2.2',
            'Bootstrap',
            'SQLite',
        ]

        return context
