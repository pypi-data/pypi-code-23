from __future__ import unicode_literals

import datetime
import json
import random
import unittest

from opvoeden_api import models

from . import utils


class TestModelRepr(unittest.TestCase):
    def test_contentset(self):
        obj = models.ContentSet(
            contentset_id=1, name='Example',
            description='Example description', is_default=False)
        self.assertRegexpMatches(
            repr(obj),
            r"^ContentSet\(contentset_id=1, name=u?'Example', description=..., is_default=False\)$")

    def test_article(self):
        obj = models.Article(
            external_reference=1, short_title='Example', title='Example article',
            article_text='Example description', parent_reference='', position=1,
            last_change_date=datetime.date.today(), canonicaltag='https://example.com/article/',
            tags=['tag1', 'tag2'])
        self.assertRegexpMatches(
            repr(obj),
            r"^Article\(external_reference=1, short_title=u?'Example',"
            r" title=u?'Example article', article_text=...,"
            r" parent_reference=u?'', position=1,"
            r" last_change_date=..., canonicaltag=..., tags=...\)$")

    def test_article_node(self):
        obj = models.ArticleNode()
        self.assertEqual('ArticleNode(article=None)', repr(obj))

    def test_image(self):
        obj = models.Image(
            image_id=1, data='R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=',
            content_type='image/gif', name='pixel.gif', creation_date=datetime.date.today())
        self.assertRegexpMatches(
            repr(obj),
            r"^Image\(image_id=1, data=..., content_type=u?'image/gif',"
            r" name=u?'pixel.gif', creation_date=...\)$")


class TestArticle(unittest.TestCase):
    def setUp(self):
        self.article = models.Article(
            external_reference=1, short_title='Example', title='Example article',
            article_text='Example description', parent_reference='', position=1,
            last_change_date=datetime.date.today(), canonicaltag='https://example.com/foo/bar/',
            tags=['tag1', 'tag2'])

    def test_path(self):
        self.assertEqual('/foo/bar/', self.article.path)

    def test_slug(self):
        self.assertEqual('bar', self.article.slug)


class TestArticleNode(unittest.TestCase):
    def setUp(self):
        data = utils.data('contentset_detail.json')
        article_list = json.loads(data, object_hook=models.Article.from_dict)
        self.tree = models.ArticleNode.from_list(article_list)

    def test_root_has_no_article(self):
        self.assertIsNone(self.tree.article, 'Root node article should be None')

    def test_nesting(self):
        root = self.tree
        self.assertEqual(len(root.children), 2, 'Expected root node to have 1 child')
        self.assertEqual('/article/', root.children[0].article.path)

        child = root.children[0]
        self.assertEqual(len(child.children), 2, 'Expected first child node to have 2 children')
        self.assertEqual('/article/more/', child.children[0].article.path)
        self.assertEqual('/article/extra/', child.children[1].article.path)

        grandchild = child.children[0]
        self.assertEqual(len(grandchild.children), 0, 'Expected first grandchild node to have 0 children')

        grandchild = child.children[1]
        self.assertEqual(len(grandchild.children), 1, 'Expected second grandchild node to have 1 child')
        self.assertEqual('/article/extra/deep/', grandchild.children[0].article.path)

    def test_iterator(self):
        self.assertEqual([1, 2, 3, 4, 5], [node.article.external_reference for node in self.tree if node.article])


class TestArticleNodeReversedOrder(TestArticleNode):
    """
    Tree building and iteration still works if the article
    list is reversed.

    """
    def setUp(self):
        data = utils.data('contentset_detail.json')
        article_list = json.loads(data, object_hook=models.Article.from_dict)
        self.tree = models.ArticleNode.from_list(reversed(article_list))


class TestArticleNodeRandomOrder(TestArticleNode):
    """
    Tree building and iteration still works if the article
    list is shuffled.

    """
    def setUp(self):
        data = utils.data('contentset_detail.json')
        article_list = json.loads(data, object_hook=models.Article.from_dict)
        rand = random.Random(42)
        rand.shuffle(article_list)
        self.tree = models.ArticleNode.from_list(article_list)


class TestImage(unittest.TestCase):
    def setUp(self):
        self.image = models.Image(
            image_id=1, data='R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=',
            content_type='image/gif', name='pixel.gif', creation_date=datetime.date.today())

    def test_as_binary(self):
        self.assertEqual(
            b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            self.image.as_binary())
