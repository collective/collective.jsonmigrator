from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
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
            # remove me, kept for BBB reasons
            yield item
