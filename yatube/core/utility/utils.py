import re
import functools
from typing import Iterable

from django.core.paginator import Paginator, Page
from django.conf import settings
from django.db.models.query import QuerySet
from django.http import HttpRequest
import pymorphy2

from core.models import ObsceneWord


OBSCENE_WORDS: QuerySet = ObsceneWord.objects.values_list(
    'word', flat=True)


def get_page_obj(request: HttpRequest, obj: QuerySet) -> Page:
    """
    Return a Page object with the given page number as per HttpRequest.

    """
    paginator = Paginator(object_list=obj, per_page=settings.TOTAL_ON_PAGE)
    page_num = request.GET.get('page')
    return paginator.get_page(page_num)


def hide_obscene_words(
    obscene_words: Iterable[str] = OBSCENE_WORDS,
    grawlix: str = settings.GRAWLIX,
) -> callable:
    """
    Check string for obscene words (both latin and cyrillic alphabetes)
    and various forms of obscene words (for cyrillics only) and
    replace them with grawlixes.

    """
    def decorator(func) -> callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> str:
            text: str = func(*args, **kwargs)
            if text and obscene_words and not isinstance(obscene_words, str):
                morph = pymorphy2.MorphAnalyzer(lang='ru')
                words_to_be_censored = obscene_words[:]
                all_words = re.findall(r'[a-zа-яё]+', text, flags=re.I)
                for word in all_words:
                    parsed_word = morph.parse(word)[0]
                    if parsed_word.normal_form in obscene_words:
                        words_to_be_censored.append(parsed_word.word)
                pattern = fr"{'|'.join(words_to_be_censored)}"
                censored_text: str = re.sub(
                    pattern, grawlix, text, flags=re.I,
                )
                return censored_text
            return text
        return wrapper
    return decorator
