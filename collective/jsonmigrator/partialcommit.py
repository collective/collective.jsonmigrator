from zope.interface import implements
from zope.interface import classProvides
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
import transaction
import logging


class PartialCommit(object):

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.step = int(options.get('every', 100))

    def __iter__(self):
        count = 1
        for item in self.previous:
            yield item
            if count % self.step == 0:
                transaction.commit()
                logging.info('Committed after %s' % count)
            count += 1

