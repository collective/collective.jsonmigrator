from collective.jsonmigrator.blueprints.utils import remove_first_bar
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import traverse
from zope.interface import implementer
from zope.interface import provider


@provider(ISectionBlueprint)
@implementer(ISection)
class DataFields:

    """ """

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.context = transmogrifier.context
        self.datafield_prefix = options.get("datafield-prefix", "_datafield_")
        self.root_path_length = len(self.context.getPhysicalPath())

    def __iter__(self):
        for item in self.previous:

            # not enough info
            if "_path" not in item:
                yield item
                continue

            path = remove_first_bar(item["_path"])
            obj = traverse(self.context, path, None)

            # path doesn't exist
            if obj is None:
                yield item
                continue

            yield item
