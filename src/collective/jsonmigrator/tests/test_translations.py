"""Tests for blueprint Translations."""
from collective.jsonmigrator.blueprints.translations import Translations
from collective.jsonmigrator.testing import JSONMIGRATOR_PAM_INTEGRATION_TESTING
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.transmogrifier import Transmogrifier
from plone import api
from plone.app.multilingual.interfaces import ITranslatable
from plone.app.multilingual.interfaces import ITranslationManager
from plone.uuid.interfaces import IMutableUUID
from Products.CMFPlone.utils import get_installer
from zope.component import getUtility

import unittest


def set_uid(obj, uid):
    mutable_uuid = IMutableUUID(obj)
    mutable_uuid.set(uid)
    obj.reindexObject()


class TestTranslationsBlueprint(unittest.TestCase):
    """Tests for blueprint Translations."""

    layer = JSONMIGRATOR_PAM_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.document_en_uid = "1a0f056909ce4d4b8b49ad14c33befb2"
        self.document_es_uid = "2a0f056909ce4d4b8b49ad14c33befb2"
        self.document_pt_uid = "3a0f056909ce4d4b8b49ad14c33befb2"
        self.not_exist_uid = "9a0f056909ce4d4b8b49ad14c33befb9"
        with api.env.adopt_roles(["Manager"]):
            self.document_en = api.content.create(
                self.portal, "Document", "document_en"
            )
            set_uid(self.document_en, self.document_en_uid)
            self.document_en.setLanguage("en")
            self.document_es = api.content.create(
                self.portal, "Document", "document_es"
            )
            set_uid(self.document_es, self.document_es_uid)
            self.document_es.setLanguage("es")
            self.document_pt = api.content.create(
                self.portal, "Document", "document_pt"
            )
            set_uid(self.document_pt, self.document_pt_uid)
            self.document_pt.setLanguage("pt")

    def test_pam_installed(self):
        product = "plone.app.multilingual"
        qi = get_installer(self.portal)
        installed = qi.is_product_installed(product)
        self.assertTrue(installed)

    def test_document_is_translatable(self):
        self.assertTrue(ITranslatable.providedBy(self.document_en))

    def test_get_utility_translations(self):
        translations = getUtility(
            ISectionBlueprint, "collective.jsonmigrator.translations"
        )
        self.assertEqual(Translations, translations)

    def create_translations_blueprint(self, items):
        transmogrifier = Transmogrifier(self.portal)
        options = {"blueprint": "collective.jsonmigrator.transtations"}
        return Translations(transmogrifier, "translations", options, items)

    def get_translations_after_blueprint(self, items):
        translations = self.create_translations_blueprint(items)
        for _ in translations:
            pass
        manager = ITranslationManager(self.document_en)
        return manager.get_translations()

    def test_default_translations_key(self):
        translations = self.create_translations_blueprint([])
        item = {"_translations": None}
        translationskey = translations.translationskey(*list(item.keys()))[0]
        self.assertEqual(translationskey, "_translations")

    def test_es_translation_set(self):
        items = [
            {
                "_translations": {"es": self.document_es_uid},
                "_path": "/document_en",
            }
        ]
        obj_translations = self.get_translations_after_blueprint(items)
        self.assertEqual(
            obj_translations, {"en": self.document_en, "es": self.document_es}
        )

    def test_es_and_pt_translation_set(self):
        items = [
            {
                "_translations": {
                    "es": self.document_es_uid,
                    "pt": self.document_pt_uid,
                },
                "_path": "/document_en",
            }
        ]
        obj_translations = self.get_translations_after_blueprint(items)
        self.assertEqual(
            obj_translations,
            {"en": self.document_en, "es": self.document_es, "pt": self.document_pt},
        )

    def test_translation_already_set(self):
        manager = ITranslationManager(self.document_en)
        manager.register_translation("es", self.document_es_uid)
        items = [
            {
                "_translations": {
                    "es": self.document_es_uid,
                },
                "_path": "/document_en",
            }
        ]
        obj_translations = self.get_translations_after_blueprint(items)
        self.assertEqual(
            obj_translations,
            {"en": self.document_en, "es": self.document_es},
        )

    def test_two_items_translation(self):
        items = [
            {
                "_translations": {
                    "es": self.document_es_uid,
                },
                "_path": "/document_en",
            },
            {
                "_translations": {
                    "pt": self.document_pt_uid,
                },
                "_path": "/document_es",
            },
        ]
        obj_translations = self.get_translations_after_blueprint(items)
        self.assertEqual(
            obj_translations,
            {"en": self.document_en, "es": self.document_es, "pt": self.document_pt},
        )

    def test_one_item_per_iterator_iteration(self):
        items = [
            {
                "_translations": {
                    "es": self.document_es_uid,
                },
                "_path": "/document_en",
            },
            {
                "_translations": {
                    "pt": self.document_pt_uid,
                },
                "_path": "/document_es",
            },
        ]
        translations = self.create_translations_blueprint(items)
        num_iterations = 0
        for _ in translations:
            num_iterations += 1
        self.assertEqual(num_iterations, 2)

    def test_translate_object_not_exist(self):
        items = [
            {
                "_translations": {
                    "es": self.not_exist_uid,
                },
                "_path": "/document_en",
            }
        ]
        obj_translations = self.get_translations_after_blueprint(items)
        self.assertEqual(
            obj_translations,
            {"en": self.document_en},
        )

    def test_translations_key_not_found(self):
        items = [
            {
                "_path": "/document_en",
            }
        ]
        obj_translations = self.get_translations_after_blueprint(items)
        self.assertEqual(
            obj_translations,
            {"en": self.document_en},
        )
