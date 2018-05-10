# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Products.CMFPlone.utils import safe_unicode
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import traverse
from ZODB.POSException import ConflictError
from zope.interface import classProvides
from zope.interface import implements


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
                yield item
                continue

            path = safe_unicode(item[pathkey].lstrip('/')).encode('ascii')
            obj = traverse(self.context, path, None)

            if obj is None:
                # path doesn't exist
                yield item
                continue

            if not getattr(aq_base(obj), '_setProperty', False):
                yield item
                continue

            for pid, pvalue, ptype in item[propertieskey]:
                if getattr(aq_base(obj), pid, None) is not None:
                    # if object have a attribute equal to property, do nothing
                    continue

                if ptype == 'string':
                    pvalue = safe_unicode(pvalue).encode('utf-8')
                try:
                    if obj.hasProperty(pid):
                        obj._updateProperty(pid, pvalue)
                    else:
                        obj._setProperty(pid, pvalue, ptype)
                except ConflictError:
                    raise
                except Exception as e:
                    raise Exception('Failed to set property "%s" type "%s"'
                                    ' to "%s" at object %s. ERROR: %s' %
                                    (pid, ptype, pvalue, str(obj), str(e)))

            yield item
