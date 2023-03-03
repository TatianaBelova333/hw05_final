from django.db import IntegrityError
from django.test import TestCase

from posts.tests.factories import ObsceneWordFactory


class ObsceneWordModelTests(TestCase):
    """Test suite for the ObsceneWord model."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.obscene_word = ObsceneWordFactory(word='COfFee')

    def test_added_word_is_lowercase(self):
        """Tests that a new word is saved as lowercase."""
        added_word = ObsceneWordModelTests.obscene_word
        self.assertEqual(added_word.word, 'coffee')

    def test_verbose_name(self):
        """Test that the field verbose_name is correct."""
        obscene_word = ObsceneWordModelTests.obscene_word

        field_verbose = {'word': 'Запрещенное слово'}
        for field, expected_value in field_verbose.items():
            self.assertEqual(
                obscene_word._meta.get_field(field).verbose_name,
                expected_value,
            )

    def test_object_name_is_text_field(self):
        """Test __str__ method of the ObsceneWord model."""
        obscene_word = ObsceneWordModelTests.obscene_word
        expected_object_name = f'Запрещенное слово: {obscene_word.word}'
        self.assertEqual(expected_object_name, str(obscene_word))

    def test_word_field_is_unique(self):
        """Test that the word field is unique."""
        with self.assertRaises(IntegrityError):
            ObsceneWordFactory(word='coffee')

    def test_ordering_by_word_asc(self):
        """Test the ordering of words in alphabetic order."""
        obscene_word = ObsceneWordModelTests.obscene_word
        ordering = obscene_word._meta.ordering
        self.assertEqual(ordering[0], 'word')
