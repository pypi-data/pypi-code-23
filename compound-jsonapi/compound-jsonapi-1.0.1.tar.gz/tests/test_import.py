import pytest
from marshmallow import ValidationError

def test_load_basic_schema(author_schema, author_jsonapi):
    """Tests that loading a basic schema with no relationships works"""
    author = author_schema().load(author_jsonapi)
    assert author.id == int(author_jsonapi['data']['id'])
    assert author.name == author_jsonapi['data']['attributes']['name']


def test_load_basic_missing_field(author_schema, author_jsonapi):
    """Tests that loading missing data leads to an error"""
    del author_jsonapi['data']['attributes']['name']
    with pytest.raises(ValidationError) as error:
        author = author_schema().load(author_jsonapi)
        assert error.errors == {'name': ['Missing data for required field.']}


def test_load_multiple(tag_schema, tags_jsonapi):
    """Tests that loading multiple objects in one go works."""
    tags = tag_schema().load(tags_jsonapi, many=True)
    assert len(tags) == 3
    for tag in tags:
        assert hasattr(tag, 'tag')


def test_load_multiple_set_on_schema(tag_schema, tags_jsonapi):
    """Tests that loading multiple objects in one go works when configured on the schema."""
    tags  = tag_schema(many=True).load(tags_jsonapi)
    assert len(tags) == 3
    for tag in tags:
        assert hasattr(tag, 'tag')


def test_load_single_parent_child_relationship(author_schema, tag_schema, author_with_interests_jsonapi):
    '''Tests that loading a basic schema with a one-to-many relationships works'''
    author = author_schema(include_schemas=(tag_schema,)).load(author_with_interests_jsonapi)
    assert author.id == int(author_with_interests_jsonapi['data']['id'])
    assert author.name == author_with_interests_jsonapi['data']['attributes']['name']
    assert len(author.interests) == 3
    assert author.interests[0].tag == author_with_interests_jsonapi['included'][0]['attributes']['tag']
    assert author.interests[1].tag == author_with_interests_jsonapi['included'][1]['attributes']['tag']
    assert author.interests[2].tag == author_with_interests_jsonapi['included'][2]['attributes']['tag']


def test_load_none_relationship(author_schema, tag_schema, author_jsonapi):
    """Tests that loading a relationship that is set to None does not load anything."""
    author_jsonapi['interests'] = None
    author = author_schema(include_schemas=(tag_schema,)).load(author_jsonapi)
    assert author.id == int(author_jsonapi['data']['id'])
    assert author.name == author_jsonapi['data']['attributes']['name']
    assert not hasattr(author, 'interests')


def test_ignore_other_data(author_schema, author_jsonapi):
    """Tests that loading data ignores any additional relationships not specified."""
    author = author_schema().load(author_jsonapi)
    assert author.id == int(author_jsonapi['data']['id'])
    assert author.name == author_jsonapi['data']['attributes']['name']
    assert not hasattr(author, 'interests')


def test_circular_relationship(page_schema, comment_schema, author_schema, tag_schema, full_jsonapi):
    """Tests that loading a circular graph structure works."""
    page = page_schema(include_schemas=(comment_schema, author_schema, tag_schema)).\
        load(full_jsonapi)
    assert page['title'] == full_jsonapi['data']['attributes']['title']
    assert not isinstance(page['author'], tuple)
    assert len(page['comments']) == 3
    assert not isinstance(page['comments'][0], tuple)
    assert not isinstance(page['comments'][1], tuple)
    assert not isinstance(page['comments'][2], tuple)


def test_load_empty_list(author_schema, tag_schema, author_jsonapi):
    """Tests that loading an empty list relationship works."""
    author_jsonapi['data']['relationships'] = {'interests': {'data': []}}
    author = author_schema(include_schemas=(tag_schema,)).load(author_jsonapi)
    assert author.interests == []
