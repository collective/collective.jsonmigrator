# -*- coding: utf-8 -*-
from AccessControl.interfaces import IRoleManager
from collective.jsonmigrator import logger
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import defaultKeys
from zope.interface import classProvides
from zope.interface import implements


class Permissions(object):

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

        if 'perms-key' in options:
            permskeys = options['perms-key'].splitlines()
        else:
            permskeys = defaultKeys(
                options['blueprint'], name, 'permissions')
        self.permskey = Matcher(*permskeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            permskey = self.permskey(*item.keys())[0]

            if not pathkey or not permskey or \
               permskey not in item:    # not enough info
                yield item
                continue

            obj = self.context.unrestrictedTraverse(
                item[pathkey].lstrip('/'), None)
            if obj is None:             # path doesn't exist
                yield item
                continue

            if IRoleManager.providedBy(obj):
                for perm, perm_dict in item[permskey].items():
                    try:
                        obj.manage_permission(perm,
                                              roles=perm_dict['roles'],
                                              acquire=perm_dict['acquire'])
                    except ValueError:
                        # raise Exception('Error setting the perm "%s"' % perm)
                        logger.error(
                            'Error setting the perm "%s" on %s' %
                            (perm, item[pathkey]))

            yield item
