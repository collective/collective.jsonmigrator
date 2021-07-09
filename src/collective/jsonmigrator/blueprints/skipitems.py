# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection, ISectionBlueprint
from zope.interface import implementer, provider


@provider(ISectionBlueprint)
@implementer(ISection)
class SkipItems(object):
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.first = int(options.get("first", 0))

    def __iter__(self):
        count = 1
        for item in self.previous:
            if count > self.first:
                yield item
            count += 1
