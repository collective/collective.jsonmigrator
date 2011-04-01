import base64
from zope.interface import implements
from zope.interface import classProvides
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from Products.Archetypes.interfaces import IBaseObject


class DataFields(object):
    """
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.datafield_prefix = options.get('datafield-prefix', '_datafield_')

    def __iter__(self):
        for item in self.previous:

            # not enough info
            if '_path' not in item:
                yield item
                continue

            obj = self.context.unrestrictedTraverse(
                        item['_path'].lstrip('/'), None)

            # path doesn't exist
            if obj is None:
                yield item
                continue

            if IBaseObject.providedBy(obj):
                for key in item.keys():

                    if not key.startswith(self.datafield_prefix):
                        continue

                    fieldname = key[len(self.datafield_prefix):]
                    field = obj.getField(fieldname)
                    value = base64.b64decode(item[key]['data'])

                    if len(value) != len(field.get(obj)):
                        field.set(obj, value)
                        obj.setFilename(item[key]['filename'])
                        obj.setContentType(item[key]['content_type'])

            yield item

