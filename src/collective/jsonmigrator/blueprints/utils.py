# -*- coding: utf-8 -*-
"""Functions utils."""
from Products.CMFPlone.utils import safe_unicode


def convert_path(path):
    """Convert path to a valid ascii string.
    If it contains non-ascii characters, raises an Exception."""
    try:
        if path.isascii():
            return safe_unicode(path)
    except AttributeError:
        # BBB: Python 2 string doesn't have isascii method.
        try:
            return safe_unicode(path).encode("ascii")
        except (UnicodeDecodeError, UnicodeEncodeError):
            pass
    _path = path
    if not isinstance(_path, str):
        _path = _path.encode("utf-8")
    raise AssertionError(
        'The path "{0}" contains non-ascii characters.'.format(
            _path,
        ),
    )


def remove_first_bar(path):
    """Removes the first bar from a path.
    If given a unicode, convert to string."""
    return convert_path(path).lstrip("/")
