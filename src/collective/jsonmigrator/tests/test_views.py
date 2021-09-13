# -*- coding: utf-8 -*-
"""Tests for views."""
from collective.jsonmigrator.testing import COLLECTIVE_JSONMIGRATOR_INTEGRATION_TESTING
from plone import api

import unittest


class TestJSONMigratorView(unittest.TestCase):
    """Test for JSONMigratorView."""

    layer = COLLECTIVE_JSONMIGRATOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

    def test_jsonmigratorview_load(self):
        """Test if view is load."""
        jsonmigratorview = api.content.get_view(
            "jsonmigrator",
            self.portal,
            self.request,
        )
        html = jsonmigratorview()
        self.assertIn("form.widgets.config:list", html)
