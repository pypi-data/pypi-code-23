from __future__ import unicode_literals

import base64
import posixpath

from collections import defaultdict, deque
from datetime import datetime
from operator import attrgetter

try:
    from urllib.parse import urlsplit
except ImportError:
    from urlparse import urlsplit


DATE_FORMAT = '%Y%m%d'


class ContentSet(object):
    def __init__(self, contentset_id=None, name=None, description=None, is_default=None):
        self.contentset_id = contentset_id
        self.name = name
        self.description = description
        self.is_default = is_default

    @classmethod
    def from_dict(cls, data):
        """Create a ContentSet instance from the API response data"""
        return cls(
            contentset_id=data['id'],
            name=data['name'],
            description=data['description'],
            is_default=bool(data['isDefault']))

    def __repr__(self):
        return (
            '{name}(contentset_id={self.contentset_id!r},'
            ' name={self.name!r}, description=...,'
            ' is_default={self.is_default!r})'
        ).format(name=self.__class__.__name__, self=self)


class ArticleNode(object):
    def __init__(self, article=None):
        self.article = article
        self._children = []

    @property
    def children(self):
        return self._children

    def append_child(self, node):
        self._children.append(node)

    @classmethod
    def from_list(cls, article_list):
        """Create a ArticleNode tree from a list of Article instances"""
        article_map = defaultdict(list)
        for article in article_list:
            article_map[article.parent_reference].append(article)

        root = ArticleNode()
        stack = deque([('', root)])
        while stack:
            external_reference, parent_node = stack.popleft()
            for article in sorted(article_map[external_reference], key=attrgetter('position')):
                child_node = ArticleNode(article)
                parent_node.append_child(child_node)
                stack.appendleft((article.external_reference, child_node))
        return root

    def __iter__(self):
        yield self
        for child in self.children:
            for node in child:
                yield node

    def __repr__(self):
        return '{name}(article={self.article!r})'.format(name=self.__class__.__name__, self=self)


class Article(object):
    def __init__(self, external_reference, short_title, title, article_text,
                 parent_reference, position, last_change_date, canonicaltag, tags):
        self.external_reference = external_reference
        self.short_title = short_title
        self.title = title
        self.article_text = article_text
        self.parent_reference = parent_reference
        self.position = position
        self.last_change_date = last_change_date
        self.canonicaltag = canonicaltag
        self.tags = tags

    @property
    def path(self):
        return urlsplit(self.canonicaltag).path

    @property
    def slug(self):
        return posixpath.basename(self.path.rstrip('/'))

    @classmethod
    def from_dict(cls, data):
        """Create an Article instance from the API response data"""
        return cls(
            external_reference=data['externalReference'],
            short_title=data['shortTitle'],
            title=data['title'],
            article_text=data['articleText'],
            parent_reference=data['parentReference'],
            position=data['position'],
            last_change_date=datetime.strptime(data['lastChangeDate'], DATE_FORMAT).date(),
            canonicaltag=data['canonicaltag'],
            tags=data['tags']
        )

    def __repr__(self):
        return (
            '{name}(external_reference={self.external_reference!r},'
            ' short_title={self.short_title!r}, title={self.title!r},'
            ' article_text=..., parent_reference={self.parent_reference!r},'
            ' position={self.position!r}, last_change_date=...,'
            ' canonicaltag=..., tags=...)'
        ).format(name=self.__class__.__name__, self=self)


class Image(object):
    def __init__(self, image_id, data, content_type, name, creation_date):
        self.image_id = image_id
        self.data = data
        self.content_type = content_type
        self.name = name
        self.creation_date = creation_date

    @classmethod
    def from_dict(cls, data):
        """Create an Image instance from the API response data"""
        return cls(
            image_id=data['imageID'],
            data=data['data'],
            content_type=data['type'],
            name=data['name'],
            creation_date=datetime.strptime(data['creationDate'], DATE_FORMAT).date())

    def as_binary(self):
        """"Convert the base64 encoded image data to binary"""
        return base64.decodestring(self.data.encode('ascii'))

    def __repr__(self):
        return (
            '{name}(image_id={self.image_id!r}, data=...,'
            ' content_type={self.content_type!r},'
            ' name={self.name!r}, creation_date=...)'
        ).format(name=self.__class__.__name__, self=self)
