# -*- coding: utf-8 -*-
from collections import namedtuple

from lxml import etree

from .exceptions import MissingFile


__all__ = (
    'parse_collection',
    'parse_litezip',
    'parse_module',
    'Collection',
    'Module',
)


MODULE_FILENAME = 'index.cnxml'
COLLECTION_FILENAME = 'collection.xml'

Collection = namedtuple('Collection', 'id, file, resources')
Module = namedtuple('Module', 'id, file, resources')


COLLECTION_NSMAP = {
    "bib": "http://bibtexml.sf.net/",
    "c": "http://cnx.rice.edu/cnxml",
    "cnxorg": "http://cnx.rice.edu/system-info",
    "col": "http://cnx.rice.edu/collxml",
    "data": "http://www.w3.org/TR/html5/dom.html#custom-data-attribute",
    "datadev": "http://dev.w3.org/html5/spec/#custom",
    "dc": "http://purl.org/dc/elements/1.1/",
    "epub": "http://www.idpf.org/2007/ops",
    "lrmi": "http://lrmi.net/the-specification",
    "m": "http://www.w3.org/1998/Math/MathML",
    "md": "http://cnx.rice.edu/mdml",
    "mod": "http://cnx.rice.edu/#moduleIds",
    "qml": "http://cnx.rice.edu/qml/1.0",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
}


def _parse_collection_id(elm_tree):
    """Given the parsed xml to an `ElementTree`,
    parse the id from the content.

    """
    xpath = '//md:content-id/text()'
    return [x for x in elm_tree.xpath(xpath, namespaces=COLLECTION_NSMAP)][0]


def _find_resources(directory, excludes=[]):
    """Return a list of resource paths from the directory.
    Ignore records via the list of `excludes`,
    which are callables that take a file parameter (as a `Path` instance).

    """
    return sorted([r for r in directory.glob('*')
                   if True not in [e(r) for e in excludes]])


def parse_module(path):
    """Parse the file structure to a data structure given the path to
    a module directory.

    """
    id = path.name
    file = path / MODULE_FILENAME

    if not file.exists():
        raise MissingFile(file)

    excludes = [
        lambda filepath: filepath.name == MODULE_FILENAME,
    ]
    resources = tuple(_find_resources(path, excludes=excludes))

    return Module(id, file, resources)


def parse_collection(path):
    """Parse a file structure to a data structure given the path to
    a collection directory.

    """
    file = path / COLLECTION_FILENAME
    if not file.exists():
        raise MissingFile(file)
    id = _parse_collection_id(etree.parse(file.open()))

    excludes = [
        lambda filepath: filepath.name == COLLECTION_FILENAME,
        lambda filepath: filepath.is_dir(),
    ]
    resources = tuple(_find_resources(path, excludes=excludes))

    return Collection(id, file, resources)


def parse_litezip(path):
    """Parse a litezip file structure to a data structure given the path
    to the litezip directory.

    """
    struct = [parse_collection(path)]
    struct.extend([parse_module(x) for x in path.iterdir()
                   if x.is_dir() and x.name.startswith('m')])
    return tuple(sorted(struct))
