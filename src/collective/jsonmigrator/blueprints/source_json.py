from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import resolvePackageReferenceOrFile
from pathlib import Path
from zope.interface import implementer
from zope.interface import provider

import json
import os


DATAFIELD = "_datafield_"


@provider(ISectionBlueprint)
@implementer(ISection)
class JSONSource:

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

        self.path = Path(resolvePackageReferenceOrFile(options["path"]))
        if not self.path.is_dir():
            raise Exception(f"Path ({self.path}) does not exists.")

        self.datafield_prefix = options.get("datafield-prefix", DATAFIELD)

    def __iter__(self):
        for item in self.previous:
            yield item

        for item3 in sorted(
            int(i) for i in os.listdir(self.path) if not i.startswith(".")
        ):
            for item2 in sorted(
                    int(j[:-5])
                    for j in os.listdir(os.path.join(self.path, str(item3)))
                    if j.endswith(".json")
            ):
                f = open(os.path.join(self.path, str(item3), f"{item2}.json"))
                item = json.loads(f.read())
                f.close()

                yield item
