from unittest import mock

from django.test import TestCase
from django.conf import settings

from core.utility.utils import hide_obscene_words


class TestHideWordsDecorator(TestCase):
    """Test suite for the hide_obscene_words function."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.default_grawlix = settings.GRAWLIX
        cls.russian_words = ['утро', 'работа', 'чай']
        cls.english_words = ['morning', 'work', 'tea']

    def test_hide_words_case_insensitive(self):
        """Test that hide_obscene_words decorator is case-insensitive."""
        grawlix = TestHideWordsDecorator.default_grawlix
        obscene_words = (
            TestHideWordsDecorator.russian_words,
            TestHideWordsDecorator.english_words,
        )

        original_texts = ('Доброе УтРо', 'Good moRNing')
        expected_texts = (f'Доброе {grawlix}', f'Good {grawlix}')

        for words, original_text, expected_text in zip(
                obscene_words, original_texts, expected_texts
        ):
            with self.subTest(
                obscene_word=words,
                original_text=original_text,
                expected_text=expected_text,
            ):
                func = mock.Mock(return_value=original_text)
                call = hide_obscene_words(words)(func)()
                self.assertEqual(call, expected_text)

    def test_hide_words_empty_list_or_str(self):
        """
        Test that hide_obscene_words decorator returns the unchanged result of
        the decorated function if obscene_words parameter is an empty list
        or a string.

        """
        original_text = 'Доброе утро.'
        obscene_words_params = ([], 'string')
        func = mock.Mock(return_value=original_text)
        for obscene_words in obscene_words_params:
            with self.subTest(obscene_words=obscene_words):
                call = hide_obscene_words(obscene_words)(func)()
                self.assertEqual(call, original_text)

    def test_hide_words_decorated_func_returns_not_str(self):
        """
        Test that hide_obscene_words decorator raises TypeError
        if the decorated does not return a string.

        """
        with self.assertRaises(TypeError):
            hide_obscene_words(TestHideWordsDecorator.russian_words)(mock.Mock(
                return_value=[1]))()

    def test_hide_words_wrapped_func_return_empty_str(self):
        """
        Test that hide_obscene_words decorator returns an empty string if
        the decorated function returns an empty string.

        """
        func = mock.Mock(return_value='')
        call = hide_obscene_words(TestHideWordsDecorator.russian_words)(func)()
        self.assertEqual(call, '')

    def test_hide_words_post_text_without_obscene_words(self):
        """
        Test that hide_obscene_words decorator does not change the behavior of
        the decorated function if the returned value of the decorated function
        does not contain obscene words.

        """
        obscene_words = (
            TestHideWordsDecorator.russian_words,
            TestHideWordsDecorator.english_words,
        )
        original_texts = ('Добрый день!', 'Good afternoon!')

        for words, original_text in zip(obscene_words, original_texts):
            with self.subTest(
                obscene_word=words,
                original_text=original_text,
            ):
                func = mock.Mock(return_value=original_text)
                call = hide_obscene_words(words)(func)()
                self.assertEqual(call, original_text)

    def test_hide_words_forms_of_obscene_words_lang_ru(self):
        """
        Test that hide_obscene_words decorator hides various forms of
        obscene words (Russian).

        """
        grawlix = TestHideWordsDecorator.default_grawlix
        obscene_words = TestHideWordsDecorator.russian_words
        original_text = 'Утром я выпью чая и пойду на работу'
        expected_text = f'{grawlix}м я выпью {grawlix} и пойду на {grawlix}'
        func = mock.Mock(return_value=original_text)
        call = hide_obscene_words(obscene_words)(func)()
        self.assertEqual(call, expected_text)

    def test_hide_words_text_contains_digits_underscore_punct(self):
        grawlix = TestHideWordsDecorator.default_grawlix
        obscene_words = (
            TestHideWordsDecorator.russian_words,
            TestHideWordsDecorator.english_words,
        )
        original_texts = (
            'Утром1 я выпью чай_ и пойду на работу!',
            'In the morning34 I will drink tea_ and go to work!'
        )
        expected_texts = (
            f'{grawlix}м1 я выпью {grawlix}_ и пойду на {grawlix}!',
            f'In the {grawlix}34 I will drink {grawlix}_ and go to {grawlix}!',
        )
        for words, original_text, expected_text in zip(
                obscene_words, original_texts, expected_texts
        ):
            with self.subTest(
                obscene_word=words,
                original_text=original_text,
                expected_text=expected_text,
            ):
                func = mock.Mock(return_value=original_text)
                call = hide_obscene_words(words)(func)()
                self.assertEqual(call, expected_text)
