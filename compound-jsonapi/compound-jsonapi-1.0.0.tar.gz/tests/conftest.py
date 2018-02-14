import faker
import pytest

from marshmallow import fields, post_load

from compound_jsonapi import Schema, Relationship

from faker import Factory

fake = Factory.create()


class Obj(object):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class PageSchema(Schema):

    id = fields.Int()
    title = fields.Str(required=True)
    text = fields.Str()
    author = Relationship(schema='AuthorSchema',
                          required=True)
    comments = Relationship(schema='CommentSchema',
                            many=True,
                            required=True)

    class Meta():
        type_ = 'pages'


class CommentSchema(Schema):

    id = fields.Int()
    title = fields.Str(required=True)
    text = fields.Str()
    author = Relationship(schema='AuthorSchema',
                          required=True)
    page = Relationship(schema=PageSchema,
                        required=True)

    @post_load()
    def build_comment(self, data):
        return Obj(**data)

    class Meta():
        type_ = 'comments'


class AuthorSchema(Schema):

    id = fields.Int()
    name = fields.Str(required=True)
    interests = Relationship(schema='TagSchema',
                             many=True,
                             allow_none=True)

    @post_load()
    def build_author(self, data):
        return Obj(**data)

    class Meta():
        type_ = 'authors'


class TagSchema(Schema):

    id = fields.Int()
    tag = fields.Str(required=True)

    @post_load()
    def build_tag(self, data):
        return Obj(**data)

    class Meta():
        type_ = 'tags'


@pytest.yield_fixture
def author_schema():
    yield AuthorSchema


@pytest.yield_fixture
def author_jsonapi():
    yield {'data': {'type': 'authors',
                    'id': str(fake.random_int()),
                    'attributes': {'name': fake.name()}}}


@pytest.yield_fixture
def author_plain():
    yield {'id': fake.random_int(),
           'name': fake.name()}

@pytest.yield_fixture
def author_obj(author_plain):
    yield Obj(**author_plain)


@pytest.yield_fixture
def tag_schema():
    yield TagSchema


@pytest.yield_fixture
def tag_jsonapi():
    yield {'data': {'type': 'tags',
                    'id': str(fake.random_int()),
                    'attributes': {'tag': fake.word()}}}


@pytest.yield_fixture
def tag_plain():
    yield {'id': fake.random_int(),
           'tag': fake.word()}


@pytest.yield_fixture
def tags_jsonapi():
    yield {'data': [{'type': 'tags',
                     'id': str(fake.random_int()),
                     'attributes': {'tag': fake.word()}} for _ in range(0, 3)]}


@pytest.yield_fixture
def tags_plain():
    yield [{'id': fake.random_int(), 'tag': fake.word()} for _ in range(0, 3)]


@pytest.yield_fixture
def author_with_interests_jsonapi(author_jsonapi, tags_jsonapi):
    author_jsonapi['data']['relationships'] = {'interests': {'data': [{'type': part['type'], 'id': part['id']} for part in tags_jsonapi['data']]}}
    author_jsonapi['included'] = tags_jsonapi['data']
    yield author_jsonapi


@pytest.yield_fixture
def author_with_interests_plain(author_plain, tags_plain):
    author_plain['interests'] = tags_plain
    yield author_plain


@pytest.yield_fixture
def comment_schema():
    yield CommentSchema


@pytest.yield_fixture
def page_schema():
    yield PageSchema


@pytest.yield_fixture
def full_jsonapi():
    author = next(author_with_interests_jsonapi(next(author_jsonapi()), next(tags_jsonapi())))
    page_jsonapi = {'data': {'type': 'pages',
                             'id': str(fake.random_int()),
                             'attributes': {'title': ' '.join(fake.words()),
                                            'text': fake.text()},
                             'relationships': {'author': {'data': {'type': author['data']['type'],
                                                                   'id': author['data']['id']}},
                                               'comments': {'data': []}}}}
    included = [author['data']]
    included.extend(author['included'])
    def add_comment():
        author = next(author_with_interests_jsonapi(next(author_jsonapi()), next(tags_jsonapi())))
        comment = {'data': {'type': 'comments',
                            'id': str(fake.random_int()),
                            'attributes': {'title': ' '.join(fake.words()),
                                           'text': fake.text()},
                            'relationships': {'author': {'data': {'type': author['data']['type'],
                                                                  'id': author['data']['id']}},
                                              'page': {'data': {'type': page_jsonapi['data']['type'],
                                                                'id': page_jsonapi['data']['id']}}}}}
        included.append(author['data'])
        included.extend(author['included'])
        included.append(comment['data'])
        page_jsonapi['data']['relationships']['comments']['data'].append({'type': comment['data']['type'],
                                                                          'id': comment['data']['id']})
    [add_comment() for _ in range(0, 3)]
    page_jsonapi['included'] = included
    return page_jsonapi


@pytest.yield_fixture
def full_plain():
    page = {'id': fake.random_int(),
            'title': ' '.join(fake.words()),
            'text': fake.text(),
            'author': next(author_with_interests_plain(next(author_plain()), next(tags_plain())))}
    comments = [{'id': fake.random_int(),
                 'title': ' '.join(fake.words()),
                 'text': fake.text(),
                 'author': next(author_with_interests_plain(next(author_plain()), next(tags_plain()))),
                 'page': page} for _ in range(0, 3)]
    page['comments'] = comments
    yield page
