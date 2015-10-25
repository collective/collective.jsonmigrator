# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import Matcher
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFCore.utils import getToolByName
from zope.interface import classProvides
from zope.interface import implements


class Owner(object):

    """ """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.memtool = getToolByName(self.context, 'portal_membership')

        if 'path-key' in options:
            pathkeys = options['path-key'].splitlines()
        else:
            pathkeys = defaultKeys(options['blueprint'], name, 'path')
        self.pathkey = Matcher(*pathkeys)

        if 'owner-key' in options:
            ownerkeys = options['owner-key'].splitlines()
        else:
            ownerkeys = defaultKeys(options['blueprint'], name, 'owner')
        self.ownerkey = Matcher(*ownerkeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            ownerkey = self.ownerkey(*item.keys())[0]

            if not pathkey or not ownerkey or \
               ownerkey not in item:    # not enough info
                yield item
                continue

            if item[ownerkey] is None or len(item[ownerkey]) != 2:
                # owner is None or something else went wrong
                yield item
                continue

            obj = self.context.unrestrictedTraverse(
                item[pathkey].lstrip('/'), None)
            if obj is None:             # path doesn't exist
                yield item
                continue

            if not IBaseObject.providedBy(obj):
                continue

            if item[ownerkey][0] and item[ownerkey][1]:
                try:
                    obj.changeOwnership(
                        self.memtool.getMemberById(item[ownerkey][1]))
                except Exception as e:
                    raise Exception('ERROR: %s SETTING OWNERSHIP TO %s' %
                                    (str(e), item[pathkey]))

                try:
                    obj.manage_setLocalRoles(item[ownerkey][1], ['Owner'])
                except Exception as e:
                    raise Exception('ERROR: %s SETTING OWNERSHIP2 TO %s' %
                                    (str(e), item[pathkey]))

            elif not item[ownerkey][0] and item[ownerkey][1]:
                try:
                    obj._owner = item[ownerkey][1]
                except Exception as e:
                    raise Exception('ERROR: %s SETTING __OWNERSHIP TO %s' %
                                    (str(e), item[pathkey]))

            yield item
