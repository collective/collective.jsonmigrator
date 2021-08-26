# -*- coding: utf-8 -*-
from collective.jsonmigrator.blueprints.utils import remove_first_bar
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import traverse
from zope.interface import implementer
from zope.interface import provider


try:
    from plone.app.multilingual.interfaces import ITranslationManager
except ImportError:
    # BBB Plone 4.3 whit Archetypes
    from plone.multilingual.interfaces import ITranslationManager


@provider(ISectionBlueprint)
@implementer(ISection)
class Translations(object):
    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

        if "path-key" in options:
            pathkeys = options["path-key"].splitlines()
        else:
            pathkeys = defaultKeys(options["blueprint"], name, "path")
        self.pathkey = Matcher(*pathkeys)

        if "translations-key" in options:
            translationskey = options["translations-key"].splitlines()
        else:
            translationskey = defaultKeys(options["blueprint"], name, "translations")
        self.translationskey = Matcher(*translationskey)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*list(item.keys()))[0]
            translationskey = self.translationskey(*list(item.keys()))[0]

            if (
                not pathkey or not translationskey or translationskey not in item
            ):  # not enough info
                yield item
                continue

            if item[translationskey] is None:
                # translations is None
                yield item
                continue

            path = remove_first_bar(item[pathkey])
            obj = traverse(self.context, path, None)

            if obj is None:
                yield item
                continue

            manager = ITranslationManager(obj)
            for language, uid in item[translationskey].items():
                if not manager.get_translation(language):
                    try:
                        manager.register_translation(language, uid)
                    except TypeError:
                        # UID not found
                        pass

            yield item
