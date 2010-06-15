
import os
import simplejson

from DateTime import DateTime
from Acquisition import aq_base
from ZODB.POSException import ConflictError

from zope.interface import implements
from zope.interface import classProvides

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import resolvePackageReferenceOrFile

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseObject

DATAFIELD = '_datafield_'


class JSONSource(object):
    """ """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

        self.path = resolvePackageReferenceOrFile(options['path'])
        if self.path is None or not os.path.isdir(self.path):
            raise Exception, 'Path ('+str(self.path)+') does not exists.'

        self.datafield_prefix = options.get('datafield-prefix', DATAFIELD)

    def __iter__(self):
        for item in self.previous:
            yield item

        for item in sorted([int(i)
                                for i in os.listdir(self.path)
                                    if not i.startswith('.')]):

            for item2 in sorted([int(j[:-5])
                                    for j in os.listdir(os.path.join(self.path, str(item)))
                                        if j.endswith('.json')]):

                f = open(os.path.join(self.path, str(item), str(item2)+'.json'))
                item3 = simplejson.loads(f.read())
                f.close()

                for key in item3.keys():
                    if key.startswith(self.datafield_prefix):
                        item3[key] = os.path.join(self.path, item3[key])

                yield item3


class Mimetype(object):
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

        if 'mimetype-key' in options:
            mimetypekeys = options['mimetype-key'].splitlines()
        else:
            mimetypekeys = defaultKeys(options['blueprint'], name, 'content_type')
        self.mimetypekey = Matcher(*mimetypekeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            mimetypekey = self.mimetypekey(*item.keys())[0]

            if not pathkey or not mimetypekey or \
               mimetypekey not in item:      # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None:                     # path doesn't exist
                yield item; continue

            if IBaseObject.providedBy(obj):
                obj.setFormat(item[mimetypekey])

            yield item


class WorkflowHistory(object):
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

        if 'workflowhistory-key' in options:
            workflowhistorykeys = options['workflowhistory-key'].splitlines()
        else:
            workflowhistorykeys = defaultKeys(options['blueprint'], name, 'workflow_history')
        self.workflowhistorykey = Matcher(*workflowhistorykeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            workflowhistorykey = self.workflowhistorykey(*item.keys())[0]

            if not pathkey or not workflowhistorykey or \
               workflowhistorykey not in item:  # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None or not getattr(obj, 'workflow_history', False):
                yield item; continue

            if IBaseObject.providedBy(obj):
                item_tmp = item

                # get back datetime stamp
                for workflow in item_tmp[workflowhistorykey]:
                    for k, workflow2 in enumerate(item_tmp[workflowhistorykey][workflow]):
                        item_tmp[workflowhistorykey][workflow][k]['time'] = DateTime(item_tmp[workflowhistorykey][workflow][k]['time'])

                obj.workflow_history.data = item_tmp[workflowhistorykey]

            yield item


class WorkflowState(object):
    """ Set the workflow state
    * Sets the workflow state of a content to whatever state without executing any transition
    * Sets its security martix as expected
    * Reindexes content security

    http://glenfant.wordpress.com/2010/04/02/changing-workflow-state-quickly-on-cmfplone-content/
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context
        self.wftool = getToolByName(self.context, 'portal_workflow')

        if 'path-key' in options:
            pathkeys = options['path-key'].splitlines()
        else:
            pathkeys = defaultKeys(options['blueprint'], name, 'path')
        self.pathkey = Matcher(*pathkeys)

        if 'workflowstate-key' in options:
            workflowstatekeys = options['workflowstate-key'].splitlines()
        else:
            workflowstatekeys = defaultKeys(options['blueprint'], name, 'workflow_state')
        self.workflowstatekey = Matcher(*workflowstatekeys)


    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            workflowstatekey = self.workflowstatekey(*item.keys())[0]

            if not pathkey or not workflowstatekey or \
               workflowstatekey not in item:  # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None or not getattr(obj, 'workflow_history', False):
                yield item; continue

            if IBaseObject.providedBy(obj):
                state = item[workflowstatekey]
                self.changeWorkflowState(obj, state, portal_workflow = self.wftool)

            yield item

    def changeWorkflowState(self, content, state_id, acquire_permissions=False,
                            portal_workflow=None, **kw):
        """Change the workflow state of an object
        @param content: Content obj which state will be changed
        @param state_id: name of the state to put on content
        @param acquire_permissions: True->All permissions unchecked and on riles and
                                    acquired
                                    False->Applies new state security map
        @param portal_workflow: Provide workflow tool (optimisation) if known
        @param kw: change the values of same name of the state mapping
        @return: None
        """

        if portal_workflow is None:
            portal_workflow = getToolByName(content, 'portal_workflow')

        # Might raise IndexError if no workflow is associated to this type
        wfs = portal_workflow.getWorkflowsFor(content)
        if not wfs:
            return

        wf_def = wfs[0]
        wf_id= wf_def.getId()

        wf_state = {
            'action': None,
            'actor': None,
            'comments': "Setting state to %s" % state_id,
            'review_state': state_id,
            'time': DateTime(),
            }

        # Updating wf_state from keyword args
        for k in kw.keys():
            # Remove unknown items
            if not wf_state.has_key(k):
                del kw[k]
        if kw.has_key('review_state'):
            del kw['review_state']
        wf_state.update(kw)

        portal_workflow.setStatusOf(wf_id, content, wf_state)

        if acquire_permissions:
            # Acquire all permissions
            for permission in content.possible_permissions():
                content.manage_permission(permission, acquire=1)
        else:
            # Setting new state permissions
            wf_def.updateRoleMappingsFor(content)

        # Map changes to the catalogs
        content.reindexObject(idxs=['allowedRolesAndUsers', 'review_state'])
        return


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
            propertieskeys = defaultKeys(options['blueprint'], name, 'properties')
        self.propertieskey = Matcher(*propertieskeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            propertieskey = self.propertieskey(*item.keys())[0]

            if not pathkey or not propertieskey or \
               propertieskey not in item:   # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None:                 # path doesn't exist
                yield item; continue

            if IBaseObject.providedBy(obj):
                if getattr(aq_base(obj), '_delProperty', False):
                    for prop in item[propertieskey]:

                        if obj.hasProperty(prop[0]):
                            try:
                                obj._delProperty(prop[0])

                            # continue if the object already has this attribute
                            except AttributeError:
                                pass

                        if getattr(aq_base(obj), prop[0], None) is not None:
                            continue

                        try:
                            obj._setProperty(prop[0], prop[1], prop[2])
                        except ConflictError:
                            raise
                        except Exception, e:
                            raise Exception('Failed to set property %s type %s to %s at object %s. ERROR: %s' % \
                                                        (prop[0], prop[1], prop[2], str(obj), str(e)))

            yield item


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
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None:             # path doesn't exist
                yield item; continue

            if IBaseObject.providedBy(obj):

                if item[ownerkey][0] and item[ownerkey][1]:
                    try:
                        obj.changeOwnership(self.memtool.getMemberById(item[ownerkey][1]))
                    except Exception, e:
                        raise Exception('ERROR: %s SETTING OWNERSHIP TO %s' % (str(e), item[pathkey]))

                    try:
                        obj.manage_setLocalRoles(item[ownerkey][1], ['Owner'])
                    except Exception, e:
                        raise Exception('ERROR: %s SETTING OWNERSHIP2 TO %s' % (str(e), item[pathkey]))

                elif not item[ownerkey][0] and item[ownerkey][1]:
                    try:
                        obj._owner = item[ownerkey][1]
                    except Exception, e:
                        raise Exception('ERROR: %s SETTING __OWNERSHIP TO %s' % (str(e), item[pathkey]))

            yield item


class DataFields(object):
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

        self.datafield_prefix = options.get('datafield-prefix', DATAFIELD)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]

            if not pathkey:                     # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None:                     # path doesn't exist
                yield item; continue

            if IBaseObject.providedBy(obj):
                for key in item.keys():
                    if not key.startswith(self.datafield_prefix):
                        continue
                    if not os.path.exists(item[key]):
                        continue

                    fieldname = key[len(self.datafield_prefix):]
                    field = obj.getField(fieldname)
                    f = open(item[key])
                    value = f.read()
                    f.close()
                    field.set(obj, value)

            yield item
