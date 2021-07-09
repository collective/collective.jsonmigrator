# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from zope.interface import implementer
from zope.interface import provider

import logging
import transaction


@provider(ISectionBlueprint)
@implementer(ISection)
class PartialCommit(object):
    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.step = int(options.get("every", 100))

    def __iter__(self):
        count = 1
        for item in self.previous:
            yield item
            if count % self.step == 0:
                transaction.commit()
                logging.info("Committed after %s" % count)
            count += 1
