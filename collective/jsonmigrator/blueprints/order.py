# -*- coding: utf-8 -*-
from Acquisition import aq_base
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from zope.app.container.contained import notifyContainerModified
from zope.interface import classProvides, implements


class OrderSection(object):
    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.every = int(options.get('every', 1000))
        self.previous = previous
        self.context = transmogrifier.context
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.poskey = defaultMatcher(options, 'pos-key', name, 'gopip')
        # Position of items without a position value
        self.default_pos = int(options.get('default-pos', 1000000))

    def __iter__(self):
        # Store positions in a mapping containing an id to position mapping for
        # each parent path {parent_path: {item_id: item_pos}}.
        positions_mapping = {}
        for item in self.previous:
            keys = item.keys()
            pathkey = self.pathkey(*keys)[0]
            poskey = self.poskey(*keys)[0]
            if not (pathkey and poskey):
                yield item
                continue

            item_id = item[pathkey].split('/')[-1]
            parent_path = '/'.join(item[pathkey].split('/')[:-1])
            if parent_path not in positions_mapping:
                positions_mapping[parent_path] = {}
            positions_mapping[parent_path][item_id] = item[poskey]

            yield item

        # Set positions on every parent
        for path, positions in positions_mapping.items():

            # Normalize positions
            ordered_keys = sorted(positions.keys(), key=lambda x: positions[x])
            normalized_positions = {}
            for pos, key in enumerate(ordered_keys):
                normalized_positions[key] = pos

            # TODO: After the new collective.transmogrifier release (>1.4), the
            # utils.py provides a traverse method.
            # from collective.transmogrifier.utils import traverse
            # parent = traverse(self.context, path)
            parent = self.context.unrestrictedTraverse(path.lstrip('/'))
            if not parent:
                continue

            parent_base = aq_base(parent)

            if hasattr(parent_base, 'getOrdering'):
                ordering = parent.getOrdering()
                # Only DefaultOrdering of p.folder is supported
                if (not hasattr(ordering, '_order')
                        and not hasattr(ordering, '_pos')):
                    continue
                order = ordering._order()
                pos = ordering._pos()
                order.sort(key=lambda x: normalized_positions.get(
                    x, pos.get(x, self.default_pos)))
                for i, id_ in enumerate(order):
                    pos[id_] = i

                notifyContainerModified(parent)
