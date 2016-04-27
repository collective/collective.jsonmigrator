# -*- coding: utf-8 -*-
from base64 import encodestring
from collective.jsonmigrator import logger
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from collective.transmogrifier.utils import resolvePackageReferenceOrFile
from zope.interface import classProvides
from zope.interface import implements

import httplib
import os.path
import pickle
import string
import urllib
import urllib2
import urlparse
import xmlrpclib

try:
    import json
except ImportError:
    import simplejson as json

_marker = object()
MEMOIZE_PROPNAME = '_memojito_'


def memoize(func):
    """A caching decorator which stores values in an attribute on the instance.
       Inspired by plone.memoize.instance
    """
    def memogetter(*args, **kwargs):
        inst = args[0]
        cache = getattr(inst, MEMOIZE_PROPNAME, _marker)
        if cache is _marker:
            setattr(inst, MEMOIZE_PROPNAME, dict())
            cache = getattr(inst, MEMOIZE_PROPNAME)
        key = (func.__name__, args[1:], frozenset(kwargs.items()))
        val = cache.get(key, _marker)
        if val is _marker:
            val = func(*args, **kwargs)
            cache[key] = val
            setattr(inst, MEMOIZE_PROPNAME, cache)
        return val
    return memogetter


class BasicAuth(xmlrpclib.Transport):

    def __init__(self, username=None, password=None, verbose=False):
        self.username = username
        self.password = password
        self.verbose = verbose
        self._use_datetime = True

    def request(self, host, handler, request_body, verbose):
        h = httplib.HTTP(host)

        h.putrequest("POST", handler)
        h.putheader("Host", host)
        h.putheader("User-Agent", self.user_agent)
        h.putheader("Content-Type", "text/xml")
        h.putheader("Content-Length", str(len(request_body)))

        if self.username is not None and self.password is not None:
            h.putheader("AUTHORIZATION", "Basic %s" % string.replace(
                encodestring("%s:%s" % (self.username, self.password)),
                "\012", ""))
        h.endheaders()

        if request_body:
            h.send(request_body)

        errcode, errmsg, headers = h.getreply()

        if errcode != 200:
            raise xmlrpclib.ProtocolError(
                host + handler,
                errcode, errmsg,
                headers
            )

        return self.parse_response(h.getfile())


class UrllibrpcException(Exception):

    """Raised when reading an url fails.
    """

    def __init__(self, code, url):
        self.code = code
        self.url = url

    def __str__(self):
        return '%s:%s' % (self.code, self.url)


class Urllibrpc(object):

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def __getattr__(self, item):
        def callable():
            scheme, netloc, path, params, query, fragment = urlparse.urlparse(
                self.url)
            if '@' not in netloc:
                netloc = '%s:%s@%s' % (self.username, self.password, netloc)
            if path.endswith("/"):
                path = path[:-1]
            path = path + '/' + item
            url = urlparse.urlunparse(
                (scheme, netloc, path, params, query, fragment))
            f = urllib.urlopen(url)
            content = f.read()
            if f.getcode() != 200:
                raise UrllibrpcException(f.getcode(), f.geturl())
            f.close()
            return content
        return callable


class RemoteSource(object):

    """ """

    name = 'collective.jsonmigrator.remotesource'
    _options = [
        ('remote-url', 'http://127.0.0.1:8080'),
        ('remote-username', 'admin'),
        ('remote-password', 'admin'),
        ('remote-path', '/Plone'),
        ('remote-crawl-depth', -1),
        ('remote-skip-path', ''),
    ]

    classProvides(ISectionBlueprint)
    implements(ISection)

    def __init__(self, transmogrifier, name, options, previous):
        self.name, self.options, self.previous = name, options, previous
        self.transmogrifier = transmogrifier
        self.context = transmogrifier.context
        for option, default in self._options:
            setattr(self, option.replace('-', '_'),
                    self.get_option(option, default))
        if type(self.remote_crawl_depth) in [str, unicode]:
            self.remote_crawl_depth = int(self.remote_crawl_depth)
        if type(self.remote_skip_path) in [str, unicode]:
            self.remote_skip_path = self.remote_skip_path.split()
        if self.remote_path[-1] == '/':
            self.remote_path = self.remote_path[:-1]

        # Load cached data from the given file
        self.cache = resolvePackageReferenceOrFile(options.get('cache', ''))
        if self.cache and os.path.exists(self.cache):
            cache_file = open(self.cache, 'rb')
            cache = pickle.load(cache_file)
            cache_file.close()
            setattr(self, MEMOIZE_PROPNAME, cache)

    def get_option(self, name, default):
        request = self.context.get('REQUEST', {})
        return request.get(
            'form.widgets.' + name.replace('-', '_'),
            self.options.get(name, default))

    @memoize
    def get_remote_item(self, path):
        remote_url = self.remote_url + self.remote_path
        if not remote_url.endswith('/'):
            remote_url += '/'
        if path.startswith('/'):
            path = path[1:]
        url = urllib2.urlparse.urljoin(remote_url, urllib.quote(path))
        # remote = xmlrpclib.Server(
        #         url,
        #         BasicAuth(self.remote_username, self.remote_password),
        #         )

        # XMLRPC seems to be causing unexplained Faults where urllib works
        remote = Urllibrpc(url, self.remote_username, self.remote_password)

        try:
            item = remote.get_item()
        except UrllibrpcException as e:
            logger.error("Failed reading url '%s' with error code %s." %
                         (e.url, e.code))
            return None, []

        try:
            subitems = remote.get_children()
        except UrllibrpcException as e:
            logger.error("Failed reading url '%s' with error code %s." %
                         (e.url, e.code))
            return item, []

        return item, subitems

    def get_items(self, path, depth=0):
        if path and path[-1] == '/':
            path = path[:-1]
        if self.remote_crawl_depth == -1 or depth <= self.remote_crawl_depth:

            item, subitems = self.get_remote_item(path)

            if item is None:
                logger.warn(':: Skipping -> %s. No remote data.' % path)
                return

            if item.startswith('ERROR'):
                logger.error(
                    "Could not get item '%s' from remote. Got %s." %
                    (path, item))
                return

            try:
                item = json.loads(item)
            except json.JSONDecodeError:
                logger.error(
                    "Could not decode item from path '%s' as JSON." % path)
                return
            logger.info(':: Crawling %s' % item['_path'])

            # item['_path'] is relative to domain root. we need relative to
            # plone root
            remote_url = self.remote_url
            _, _, remote_path, _, _, _ = urlparse.urlparse(remote_url)
            item['_path'] = item['_path'][len(remote_path):]
            if item['_path'].startswith('/'):
                item['_path'] = item['_path'][1:]

            if item['_type'] == "Plone Site":
                pass
            else:
                yield item

            if subitems.startswith('ERROR'):
                logger.error(
                    "Could not get subitems for '%s'. Got %s." %
                    (path, subitems))
                return

            for subitem_id in json.loads(subitems):
                subitem_path = path + '/' + subitem_id

                if subitem_path[len(self.remote_path):]\
                        in self.remote_skip_path:
                    logger.info(':: Skipping -> ' + subitem_path)
                    continue

                for subitem in self.get_items(subitem_path, depth + 1):
                    yield subitem

    def __iter__(self):
        for item in self.previous:
            yield item

        for item in self.get_items(self.remote_path):
            if item:
                yield item

        # Store cached items in a file
        if self.cache:
            cache = getattr(self, MEMOIZE_PROPNAME, _marker)
            cache_file = open(self.cache, 'wb')
            pickle.dump(cache, cache_file)
            cache_file.close()
