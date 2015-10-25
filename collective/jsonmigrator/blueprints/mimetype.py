# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import Matcher
from Products.Archetypes.interfaces import IBaseObject
from zope.interface import classProvides
from zope.interface import implements


class Mimetype(object):

    """
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

        if 'path-key' in options:
            pathkeys = options['path-key'].splitlines()
        else:
            pathkeys = defaultKeys(options['blueprint'], name, 'path')
        self.pathkey = Matcher(*pathkeys)

        if 'mimetype-key' in options:
            mimetypekeys = options['mimetype-key'].splitlines()
        else:
            mimetypekeys = defaultKeys(
                options['blueprint'], name, 'format')
        self.mimetypekey = Matcher(*mimetypekeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            mimetypekey = self.mimetypekey(*item.keys())[0]

            if not pathkey or not mimetypekey or \
               mimetypekey not in item:
                # not enough info
                yield item
                continue

            obj = self.context.unrestrictedTraverse(
                item[pathkey].lstrip('/'), None)
            if obj is None:
                # path doesn't exist
                yield item
                continue

            if IBaseObject.providedBy(obj):
                obj.setFormat(item[mimetypekey])

            yield item
