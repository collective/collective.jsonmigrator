
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

        if 'format-key' in options:
            formatkeys = options['format-key'].splitlines()
        else:
            formatkeys = defaultKeys(options['blueprint'], name, 'format')
        self.formatkey = Matcher(*formatkeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            formatkey = self.formatkey(*item.keys())[0]

            if not pathkey or not formatkey or \
               formatkey not in item:      # not enough info
                yield item; continue
            
            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None:                     # path doesn't exist
                yield item; continue

            if IBaseObject.providedBy(obj):
                obj.setFormat(item[formatkey])

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
            workflowhistorykeys = defaultKeys(options['blueprint'], name, 'workflowhistory')
        self.workflowhistorykey = Matcher(*workflowhistorykeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            workflowhistorykey = self.workflowhistorykey(*item.keys())[0]

            if not pathkey or not workflowhistorykey or \
               workflowhistorykey not in item:  # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None:                     # path doesn't exist
                yield item; continue

            if IBaseObject.providedBy(obj):
                item_tmp = item

                # get back datetime stamp
                for workflow in item[workflowhistorykey]:
                    for k, workflow2 in enumerate(item[workflowhistorykey][workflow]):
                        item_tmp[workflowhistorykey][workflow][k]['time'] = DateTime(item[workflowhistorykey][workflow][k]['time'])

                obj.workflow_history.data = item_tmp[workflowhistorykey]

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
                        obj.changeOwnership(pm.getMemberById(item[ownerkey][1]))
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
        self.basepath = options.get('basepath', '')

        if 'path-key' in options:
            pathkeys = options['path-key'].splitlines()
        else:
            pathkeys = defaultKeys(options['blueprint'], name, 'path')
        self.pathkey = Matcher(*pathkeys)

        if 'datafield-key' in options:
            datafieldkeys = options['datafield-key'].splitlines()
        else:
            datafieldkeys = defaultKeys(options['blueprint'], name, 'datafield')
        self.datafieldkey = Matcher(*datafieldkeys)

    def __iter__(self):
        for item in self.previous:
            pathkey = self.pathkey(*item.keys())[0]
            datafieldkey = self.datafieldkey(*item.keys())[0]

            if not pathkey or not datafieldkey: # not enough info
                yield item; continue

            obj = self.context.unrestrictedTraverse(item[pathkey].lstrip('/'), None)
            if obj is None:                     # path doesn't exist
                yield item; continue

            if IBaseObject.providedBy(obj):
                for key in item.keys():
                    if not key.startswith(datafieldkey):
                        continue

                    fieldname = key[len(datafieldkey)+1:]
                    f = open(os.join.path(self.basepath, item[datafieldkey]))
                    value = f.read()
                    f.close()
                    field.set(obj, value)

            yield item


