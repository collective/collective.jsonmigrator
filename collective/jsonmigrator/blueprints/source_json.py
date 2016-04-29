# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import resolvePackageReferenceOrFile
from zope.interface import classProvides
from zope.interface import implements

import os

try:
    import json
except ImportError:
    import simplejson as json

DATAFIELD = '_datafield_'


class JSONSource(object):
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

        self.path = resolvePackageReferenceOrFile(options['path'])
        if self.path is None or not os.path.isdir(self.path):
            raise Exception('Path (' + str(self.path) + ') does not exists.')

        self.datafield_prefix = options.get('datafield-prefix', DATAFIELD)

    def __iter__(self):
        for item in self.previous:
            yield item

        for item3 in sorted([
            int(i) for i in os.listdir(self.path) if not i.startswith('.')
        ]):
            for item2 in sorted([
                int(j[:-5])
                for j in os.listdir(os.path.join(self.path, str(item3)))
                if j.endswith('.json')
            ]):

                f = open(os.path.join(
                    self.path, str(item3), '%s.json' % item2
                ))
                item = json.loads(f.read())
                f.close()

                yield item
