# -*- coding: utf-8 -*-
"""Tests for utils."""
from collective.jsonmigrator.blueprints.utils import convert_path
from collective.jsonmigrator.blueprints.utils import remove_first_bar

import unittest


class TestUtils(unittest.TestCase):
    """Test for function of utils.py."""

    def test_convert_path(self):
        """Test function convert_path."""
        self.assertEqual("/plone/test", convert_path("/plone/test"))

    def test_convert_path_unicode(self):
        """Validates that the convert_path function convert
        unicode to string."""
        path = convert_path(u"/plone/en")
        self.assertEqual(str, type(path))

    def test_convert_path_not_ascii(self):
        """Validates that the convert_path function raises an exception when
        it receives a path that is not an ascii."""
        self.assertRaises(Exception, convert_path, "/plone/testç")

    def test_convert_path_exception_message(self):
        """Test exception message."""
        ex = None
        try:
            convert_path("/plone/testç")
        except AssertionError as e:
            ex = e
        self.assertEqual(
            'The path "/plone/testç" contains non-ascii characters.',
            str(ex),
        )

    def test_convert_path_unicode_exception_message(self):
        """Test exception message when the path is unicode."""
        ex = None
        try:
            convert_path(u"/plone/testç")
        except AssertionError as e:
            ex = e
        self.assertEqual(
            'The path "/plone/testç" contains non-ascii characters.',
            str(ex),
        )

    def test_remove_first_bar(self):
        """Tests if the remove_first_bar function removes the first bar."""
        self.assertEqual("plone/en", remove_first_bar("/plone/en"))

    def test_remove_first_bar_converte(self):
        """Tests whether the remove_first_bar function
        converts unicode to string."""
        path = remove_first_bar(u"/plone/en")
        self.assertEqual(str, type(path))

    def test_remove_first_bar_exception_message(self):
        """Test exception message."""
        ex = None
        try:
            remove_first_bar(u"/plone/testç")
        except AssertionError as e:
            ex = e
        self.assertEqual(
            'The path "/plone/testç" contains non-ascii characters.',
            str(ex),
        )
