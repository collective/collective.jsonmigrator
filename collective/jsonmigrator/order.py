from Acquisition import aq_base
from zope.interface import classProvides, implements
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import defaultMatcher
from zope.app.container.contained import notifyContainerModified

TEMP_ORDER_KEY = '_temp_gopip'


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
        # Store position in a temporaray attribute and keep a list of parents
        # that need to recalculate their ordering after all items were
        # processed.
        parents = set([])
        for item in self.previous:
            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]
            poskey = self.poskey(*keys)[0]
            if not (pathkey and poskey):
                yield item
                continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'),
                                                    None)
            if obj is None:
                yield item
                continue

            setattr(obj, TEMP_ORDER_KEY, item[poskey])
            parents.add('/'.join(item[pathkey].lstrip('/').split('/')[:-1]))
            yield item

        for item in parents:
            parent = self.context.unrestrictedTraverse(item)
            parent_base = aq_base(parent)

            if hasattr(parent_base, 'getOrdering'):
                ordering = parent.getOrdering()
                # Only DefaultOrdering of p.folder is supported
                if (not hasattr(parent_base, '_order') 
                    and not hasattr(parent_base, '_pos')):
                    continue
                order = ordering._order()
                pos = ordering._pos()

                def my_cmp(x, y):
                    # Keep the position of objects that do not have our order
                    # key.
                    posx = getattr(parent._getOb(x), TEMP_ORDER_KEY, None)
                    posy = getattr(parent._getOb(y), TEMP_ORDER_KEY, None)
                    if posx is None or posy is None:
                        return 0
                    return cmp(posx, posy)
                order.sort(my_cmp)
                for i, id_ in enumerate(order):
                    pos[id_] = i

                for id_ in parent.objectIds():
                    obj = parent._getOb(id_)
                    if hasattr(obj, TEMP_ORDER_KEY):
                        delattr(obj, TEMP_ORDER_KEY)

                notifyContainerModified(parent)
