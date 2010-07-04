
import time
import os
import simplejson
import logging
import transaction

from DateTime import DateTime
from Acquisition import aq_base
from ZODB.POSException import ConflictError

from zope.interface import implements
from zope.interface import classProvides

from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.utils import Matcher
from collective.transmogrifier.utils import defaultMatcher
from collective.transmogrifier.utils import defaultKeys
from collective.transmogrifier.utils import resolvePackageReferenceOrFile

from Products.CMFCore.utils import getToolByName
from Products.Archetypes.interfaces import IBaseObject

DATAFIELD = '_datafield_'
STATISTICSFIELD = '_statistics_field_prefix_'


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

        for item3 in sorted([int(i)
                                for i in os.listdir(self.path)
                                    if not i.startswith('.')]):

            for item2 in sorted([int(j[:-5])
                                    for j in os.listdir(os.path.join(self.path, str(item3)))
                                        if j.endswith('.json')]):

                f = open(os.path.join(self.path, str(item3), str(item2)+'.json'))
                item = simplejson.loads(f.read())
                f.close()

                for key in item.keys():
                    if key.startswith(self.datafield_prefix):
                        item[key] = os.path.join(self.path, item[key])

                yield item

class SkipItems(object):

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
	self.first = int(options.get('first', 0))

    def __iter__(self):
        count = 1
        for item in self.previous:
            if count > self.first:
                yield item
            count += 1

class PartialCommit(object):

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.step = int(options.get('every', 100))

    def __iter__(self):
        count = 1
        for item in self.previous:
            yield item
            if count % self.step == 0:
                transaction.commit()
            count += 1

class Statistics(object):
    """ This has to be placed in the pipeline just after all sources
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.stats = {'START_TIME':     int(time.time()),
                      'TIME_LAST_STEP': 0,
                      'STEP':           options.get('log-step', 25),
                      'OBJ_COUNT':      0,
                      'EXISTED':        0,
                      'ADDED':          0,
                      'NOT-ADDED':      0,}
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.statistics_prefix = options.get('statisticsfield-prefix', STATISTICSFIELD)
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

    def __iter__(self):
        for item in self.previous:

            self.stats['OBJ_COUNT'] += 1

            yield item

            #if self.statistics_prefix + 'existed' in item and item[self.statistics_prefix + 'existed']:
            #    self.stats['EXISTED'] += 1
            #else:
            #    keys = item.keys()
            #    pathkey = self.pathkey(*keys)[0]
            #    path = item[pathkey]
            #    path = path.encode('ASCII')
            #    context = self.context.unrestrictedTraverse(path, None)
            #    if context is not None and path == '/'.join(context.getPhysicalPath()):
            #        self.stats['ADDED'] += 1
            #    else:
            #        self.stats['NOT-ADDED'] += 1

            if self.stats['OBJ_COUNT'] % self.stats['STEP'] == 0:

                keys = item.keys()
                pathkey = self.pathkey(*keys)[0]
                path = item.get(pathkey, 'Unknown')
                logging.warning('Migrating now: %s' % path)

                now = int(time.time())
                stat = 'COUNT: %d; ' % self.stats['OBJ_COUNT']
                stat += 'TOTAL TIME: %d; ' % (now - self.stats['START_TIME'])
                stat += 'STEP TIME: %d; ' % (now - self.stats['TIME_LAST_STEP'])
                self.stats['TIME_LAST_STEP'] = now
                stat += 'EXISTED: %d; ADDED: %d; NOT-ADDED: %d' % (
                                               self.stats['EXISTED'],
                                               self.stats['ADDED'],
                                               self.stats['NOT-ADDED'])
                logging.warning(stat)


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
        self.wftool = getToolByName(self.context, 'portal_workflow')

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

                # get back datetime stamp and set the workflow history
                for workflow in item_tmp[workflowhistorykey]:
                    for k, workflow2 in enumerate(item_tmp[workflowhistorykey][workflow]):
                        item_tmp[workflowhistorykey][workflow][k]['time'] = DateTime(item_tmp[workflowhistorykey][workflow][k]['time'])
                obj.workflow_history.data = item_tmp[workflowhistorykey]

                # update security
                workflows = self.wftool.getWorkflowsFor(obj)
                if workflows:
                    workflows[0].updateRoleMappingsFor(obj)

            yield item


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
                        if getattr(aq_base(obj), prop[0], None) is not None:
                            # if object have a attribute equal to property, do nothing
                            continue
                        try:
                            if obj.hasProperty(prop[0]):
                                obj._updateProperty(prop[0], prop[1])
                            else:
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
                    if len(value) != len(field.get(obj)):
                        field.set(obj, value)

            yield item
