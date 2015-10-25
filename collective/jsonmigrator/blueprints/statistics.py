# -*- coding: utf-8 -*-
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import defaultMatcher
from zope.interface import classProvides
from zope.interface import implements

import logging
import time

STATISTICSFIELD = '_statistics_field_prefix_'


class Statistics(object):

    """ This has to be placed in the pipeline just after all sources
    """

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.stats = {'START_TIME': int(time.time()),
                      'TIME_LAST_STEP': 0,
                      'STEP': options.get('log-step', 25),
                      'OBJ_COUNT': 0,
                      'EXISTED': 0,
                      'ADDED': 0,
                      'NOT-ADDED': 0, }
        self.pathkey = defaultMatcher(options, 'path-key', name, 'path')
        self.statistics_prefix = options.get(
            'statisticsfield-prefix',
            STATISTICSFIELD)
        self.transmogrifier = transmogrifier
        self.name = name
        self.options = options
        self.previous = previous
        self.context = transmogrifier.context

    def __iter__(self):
        for item in self.previous:

            self.stats['OBJ_COUNT'] += 1

            yield item

            # if self.statistics_prefix + 'existed' in item and item[
            #       self.statistics_prefix + 'existed']:
            #    self.stats['EXISTED'] += 1
            # else:
            #    keys = item.keys()
            #    pathkey = self.pathkey(*keys)[0]
            #    path = item[pathkey]
            #    path = path.encode('ASCII')
            #    context = self.context.unrestrictedTraverse(path, None)
            #    if context is not None and path == '/'.join(
            #           context.getPhysicalPath()):
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
                stat += 'STEP TIME: %d; ' % (now -
                                             self.stats['TIME_LAST_STEP'])
                self.stats['TIME_LAST_STEP'] = now
                stat += 'EXISTED: %d; ADDED: %d; NOT-ADDED: %d' % (
                    self.stats['EXISTED'],
                    self.stats['ADDED'],
                    self.stats['NOT-ADDED'])
                logging.warning(stat)
