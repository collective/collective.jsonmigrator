from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import defaultMatcher


class OrderSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.every = int(options.get('every', 1000))
        self.previous = previous
        self.context = transmogrifier.context
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.poskey = defaultMatcher(options, 'pos-key', name, 'gopip')

    def __iter__(self):
        items = []
        for item in self.previous:
            items.append(item)
            yield item

        for item in items:
            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]
            poskey = self.poskey(*keys)[0]
            parent = self.context.unrestrictedTraverse(
                '/'.join(item[pathkey].split('/')[:-1]), None)
            if parent and item[poskey]:
                objectid = item[pathkey].split('/')[-1:]
                parent.moveObjectToPosition(objectid, item[poskey])
