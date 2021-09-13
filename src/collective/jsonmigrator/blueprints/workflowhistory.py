# -*- coding: utf-8 -*-
from collective.jsonmigrator.blueprints.utils import remove_first_bar
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import traverse
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from zope.interface import implementer
from zope.interface import provider


try:
    from Products.Archetypes.interfaces import IBaseObject
except ImportError:
    IBaseObject = None

try:
    from plone.dexterity.interfaces import IDexterityContent

    dexterity_available = True
except ImportError:
    dexterity_available = False


@provider(ISectionBlueprint)
@implementer(ISection)
class WorkflowHistory(object):
    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.wftool = getToolByName(self.context, "portal_workflow")

        if "path-key" in options:
            pathkeys = options["path-key"].splitlines()
        else:
            pathkeys = defaultKeys(options["blueprint"], name, "path")
        self.pathkey = Matcher(*pathkeys)

        if "workflowhistory-key" in options:
            workflowhistorykeys = options["workflowhistory-key"].splitlines()
        else:
            workflowhistorykeys = defaultKeys(
                options["blueprint"], name, "workflow_history"
            )
        self.workflowhistorykey = Matcher(*workflowhistorykeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*list(item.keys()))[0]
            workflowhistorykey = self.workflowhistorykey(*list(item.keys()))[0]

            if (
                not pathkey or not workflowhistorykey or workflowhistorykey not in item
            ):  # not enough info
                yield item
                continue

            # traverse() available in version 1.5+ of collective.transmogrifier
            path = remove_first_bar(item[pathkey])
            obj = traverse(self.context, path, None)

            if obj is None or not getattr(obj, "workflow_history", False):
                yield item
                continue

            if (IBaseObject and IBaseObject.providedBy(obj)) or (
                dexterity_available and IDexterityContent.providedBy(obj)
            ):
                item_tmp = item

                # get back datetime stamp and set the workflow history
                for workflow in item_tmp[workflowhistorykey]:
                    for k, workflow2 in enumerate(
                        item_tmp[workflowhistorykey][workflow]
                    ):  # noqa
                        if "time" in item_tmp[workflowhistorykey][workflow][k]:
                            item_tmp[workflowhistorykey][workflow][k][
                                "time"
                            ] = DateTime(  # noqa
                                item_tmp[workflowhistorykey][workflow][k]["time"]
                            )  # noqa
                obj.workflow_history.data = item_tmp[workflowhistorykey]

                # update security
                workflows = self.wftool.getWorkflowsFor(obj)
                if workflows:
                    workflows[0].updateRoleMappingsFor(obj)

            yield item
