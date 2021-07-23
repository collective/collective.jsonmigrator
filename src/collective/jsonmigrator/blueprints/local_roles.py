# -*- coding: utf-8 -*-
from AccessControl.interfaces import IRoleManager
from collective.jsonmigrator.blueprints.utils import remove_first_bar
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import traverse
from zope.interface import implementer
from zope.interface import provider


@provider(ISectionBlueprint)
@implementer(ISection)
class LocalRoles(object):
    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

        if "path-key" in options:
            pathkeys = options["path-key"].splitlines()
        else:
            pathkeys = defaultKeys(options["blueprint"], name, "path")
        self.pathkey = Matcher(*pathkeys)

        if "local-roles-key" in options:
            roleskeys = options["local-roles-key"].splitlines()
        else:
            roleskeys = defaultKeys(options["blueprint"], name, "ac_local_roles")
        self.roleskey = Matcher(*roleskeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*list(item.keys()))[0]
            roleskey = self.roleskey(*list(item.keys()))[0]

            if not pathkey or not roleskey or roleskey not in item:  # not enough info
                yield item
                continue

            path = remove_first_bar(item[pathkey])
            obj = traverse(self.context, path, None)

            # path doesn't exist
            if obj is None:
                yield item
                continue

            if IRoleManager.providedBy(obj):
                for principal, roles in item[roleskey].items():
                    if roles:
                        obj.manage_addLocalRoles(principal, roles)
                        obj.reindexObjectSecurity()

            yield item
