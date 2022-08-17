from collective.jsonmigrator import logger
from collective.transmogrifier.interfaces import ISection
from collective.transmogrifier.interfaces import ISectionBlueprint
from urllib import error
from urllib import parse
from urllib import request
from zope.interface import implementer
from zope.interface import provider

import base64
import json
import threading
import time


@provider(ISectionBlueprint)
@implementer(ISection)
class CatalogSourceSection:

    """A source section which creates items from a remote Plone site by
    querying it's catalog.
    """

    def __init__(self, transmogrifier, name, options, previous):
        self.previous = previous
        self.options = options
        self.context = transmogrifier.context

        self.remote_url = self.get_option("remote-url", "http://localhost:8080")
        remote_username = self.get_option("remote-username", "admin")
        remote_password = self.get_option("remote-password", "admin")

        catalog_path = self.get_option("catalog-path", "/Plone/portal_catalog")
        self.site_path_length = len("/".join(catalog_path.split("/")[:-1]))

        catalog_query = self.get_option("catalog-query", None)
        catalog_query = " ".join(catalog_query.split())
        catalog_query = base64.b64encode(catalog_query)

        self.remote_skip_paths = self.get_option("remote-skip-paths", "").split()
        self.queue_length = int(self.get_option("queue-size", "10"))

        # Install a basic auth handler
        auth_handler = request.HTTPBasicAuthHandler()
        auth_handler.add_password(
            realm="Zope",
            uri=self.remote_url,
            user=remote_username,
            passwd=remote_password,
        )
        opener = request.build_opener(auth_handler)
        request.install_opener(opener)

        req = request.Request(
            f"{self.remote_url}{catalog_path}/get_catalog_results",
            parse.urlencode({"catalog_query": catalog_query}),
        )
        try:
            f = request.urlopen(req)
            resp = f.read()
        except error.URLError:
            raise

        self.item_paths = sorted(json.loads(resp))

    def get_option(self, name, default):
        """Get an option from the request if available and fallback to the
        transmogrifier config.
        """
        request = getattr(self.context, "REQUEST", None)
        if request is not None:
            value = request.form.get(
                "form.widgets." + name.replace("-", "_"),
                self.options.get(name, default),
            )
        else:
            value = self.options.get(name, default)
        if isinstance(value, str):
            value = value.encode("utf8")
        return value

    def __iter__(self):
        for item in self.previous:
            yield item

        queue = QueuedItemLoader(
            self.remote_url, self.item_paths, self.remote_skip_paths, self.queue_length
        )
        queue.start()

        for item in queue:
            if not item:
                continue
            index = self.site_path_length
            item["_path"] = item["_path"][index:]
            yield item


class QueuedItemLoader(threading.Thread):
    def __init__(self, remote_url, paths, remote_skip_paths, queue_length):
        super().__init__()

        self.remote_url = remote_url
        self.paths = list(paths)
        self.remote_skip_paths = remote_skip_paths
        self.queue_length = queue_length

        self.queue = []
        self.finished = len(paths) == 0

    def __iter__(self):
        while not self.finished or len(self.queue) > 0:
            while len(self.queue) == 0:
                time.sleep(0.0001)

            yield self.queue.pop(0)

    def run(self):
        while not self.finished:
            while len(self.queue) >= self.queue_length:
                time.sleep(0.0001)

            path = self.paths.pop(0)
            if not self._skip_path(path):
                item = self._load_path(path)
                self.queue.append(item)

            if len(self.paths) == 0:
                self.finished = True

    def _skip_path(self, path):
        for skip_path in self.remote_skip_paths:
            if path.startswith(skip_path):
                return True
        return False

    def _load_path(self, path):
        item_url = f"{self.remote_url}{parse.quote(path)}/get_item"
        try:
            f = request.urlopen(item_url)
            item_json = f.read()
        except error.URLError as e:
            logger.error(f"Failed reading item from {item_url}. {e}")
            return None
        try:
            item = json.loads(item_json)
        except json.JSONDecodeError:
            logger.error(f"Could not decode item from {item_url}.")
            return None
        return item
