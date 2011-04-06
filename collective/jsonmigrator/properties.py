
from zope.interface import implements
from zope.interface import classProvides

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import defaultKeys

from Acquisition import aq_base
from ZODB.POSException import ConflictError
from Products.Archetypes.interfaces import IBaseObject


class Properties(object):
    """ """

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

        if 'properties-key' in options:
            propertieskeys = options['properties-key'].splitlines()
        else:
            propertieskeys = defaultKeys(
                    options['blueprint'], name, 'properties')
        self.propertieskey = Matcher(*propertieskeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            propertieskey = self.propertieskey(*item.keys())[0]

            if not pathkey or not propertieskey or \
               propertieskey not in item:
                # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(
                            item[pathkey].lstrip('/'), None)
            if obj is None:
                # path doesn't exist
                yield item; continue

            if not IBaseObject.providedBy(obj) and \
               not getattr(aq_base(obj), '_delProperty', False):
                continue

            for prop in item[propertieskey]:
                if getattr(aq_base(obj), prop[0], None) is not None:
                    # if object have a attribute equal to property, do nothing
                    continue

                try:
                    if obj.hasProperty(prop[0]):
                        obj._updateProperty(prop[0], prop[1])
                    else:
                        obj._setProperty(prop[0], prop[1], prop[2])
                except ConflictError:
                    raise
                except Exception, e:
                    raise Exception('Failed to set property %s type %s'
                            ' to %s at object %s. ERROR: %s' % \
                            (prop[0], prop[1], prop[2], str(obj), str(e)))

            yield item
