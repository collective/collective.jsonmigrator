# -*- coding: utf-8 -*-
from Products.CMFPlone.utils import safe_unicode
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from zope.interface import classProvides
from zope.interface import implements

import base64

try:
    from Products.Archetypes.interfaces import IBaseObject
except ImportError:
    IBaseObject = None


class DataFields(object):

    """
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.datafield_prefix = options.get('datafield-prefix', '_datafield_')
        self.root_path_length = len(self.context.getPhysicalPath())

    def __iter__(self):
        for item in self.previous:

            # not enough info
            if '_path' not in item:
                yield item
                continue

            path = safe_unicode(item['_path'].lstrip('/')).encode('ascii')
            obj = traverse(self.context, path, None)

            # path doesn't exist
            if obj is None:
                yield item
                continue

            if IBaseObject and IBaseObject.providedBy(obj):
                for key in item.keys():

                    if not key.startswith(self.datafield_prefix):
                        continue

                    fieldname = key[len(self.datafield_prefix):]

                    field = obj.getField(fieldname)
                    if field is None:
                        continue
                    value = base64.b64decode(item[key]['data'])

                    # XXX: handle other data field implementations
                    field_value = field.get(obj)
                    if not hasattr(field_value, 'data') or (
                            value != field_value.data):
                        field.set(obj, value)
                        obj.setFilename(item[key]['filename'], fieldname)
                        obj.setContentType(
                            item[key]['content_type'], fieldname)

            yield item
