def test_basic_export(author_schema, author_plain):
    """Test basic dumping of a single object."""
    author = author_schema().dump(author_plain)
    assert 'data' in author
    assert 'type' in author['data']
    assert author['data']['type'] == 'authors'
    assert 'id' in author['data']
    assert author['data']['id'] == str(author_plain['id'])
    assert 'attributes' in author['data']
    assert 'name' in author['data']['attributes']
    assert author['data']['attributes']['name'] == author_plain['name']

def test_basic_export_many(tag_schema, tags_plain):
    """Test basic dumping of many objects with the same schema."""
    tags = tag_schema(many=True).dump(tags_plain)
    assert 'data' in tags
    assert len(tags['data']) == 3
    for tag in tags['data']:
        assert 'type' in tag
        assert tag['type'] == 'tags'
        assert 'id' in tag
        assert 'attributes' in tag
        assert 'tag' in tag['attributes']


def test_export_no_attributes():
    """Test dumping of a schema without attributes."""
    from marshmallow import fields
    from compound_jsonapi import Schema

    class NoAttributeSchema(Schema):
        id = fields.Int()

        class Meta():
            type_ = 'no_attributes'

    schema = NoAttributeSchema()
    data  = schema.dump({'id': 1})
    assert 'data' in data
    assert 'type' in data['data']
    assert data['data']['type'] == 'no_attributes'
    assert 'id' in data['data']
    assert data['data']['id'] == '1'
    assert 'attributes' not in data['data']
    assert 'relationships' not in data['data']


def test_one_to_many_relationship(author_schema, tag_schema, author_with_interests_plain):
    """Test dumping a single level one-to-many relationship."""
    author = author_schema(include_schemas=(tag_schema,)).dump(author_with_interests_plain)
    assert 'data' in author
    assert 'type' in author['data']
    assert author['data']['type'] == 'authors'
    assert 'id' in author['data']
    assert author['data']['id'] == str(author_with_interests_plain['id'])
    assert 'attributes' in author['data']
    assert 'name' in author['data']['attributes']
    assert author['data']['attributes']['name'] == author_with_interests_plain['name']
    assert 'interests' not in author['data']['attributes']
    assert 'relationships' in author['data']
    assert 'interests' in author['data']['relationships']
    assert 'data' in author['data']['relationships']['interests']
    for interest in author['data']['relationships']['interests']['data']:
        assert 'type' in interest
        assert 'id' in interest
        assert len(interest) == 2
    assert 'included' in author
    for included in author['included']:
        assert 'type' in included
        assert included['type'] == 'tags'
        assert 'id' in included
        assert 'attributes' in included
        assert 'tag' in included['attributes']


def test_many_to_many_relationship(page_schema, comment_schema, author_schema, tag_schema, full_plain):
    """Test dumping a many to many relationship."""
    page = page_schema(include_schemas=(comment_schema, author_schema, tag_schema)).dump(full_plain)
    assert 'data' in page
    assert 'type' in page['data']
    assert page['data']['type'] == 'pages'
    assert 'id' in page['data']
    assert page['data']['id'] == str(full_plain['id'])
    assert 'attributes' in page['data']
    assert 'relationships' in page['data']
    assert 'comments' in page['data']['relationships']
    assert 'data' in page['data']['relationships']['comments']
    assert len(page['data']['relationships']['comments']['data']) == 3
    assert 'included' in page
    assert len(page['included']) == 19


def test_export_explicit_relationships(page_schema, author_schema, tag_schema, full_plain):
    """Test exporting only a sub-set of relationships."""
    page = page_schema(include_schemas=(author_schema, tag_schema)).dump(full_plain)
    assert 'data' in page
    assert 'type' in page['data']
    assert page['data']['type'] == 'pages'
    assert 'id' in page['data']
    assert page['data']['id'] == str(full_plain['id'])
    assert 'relationships' in page['data']
    assert len(page['data']['relationships']) == 2
    assert 'author' in page['data']['relationships']
    assert 'data' in page['data']['relationships']['author']
    assert 'type' in page['data']['relationships']['author']['data']
    assert 'id' in page['data']['relationships']['author']['data']
    assert 'comments' in page['data']['relationships']
    assert 'data' in page['data']['relationships']['comments']
    assert page['data']['relationships']['comments']['data'] == []
    assert 'included' in page
    assert len(page['included']) == 4


def test_export_obj(author_schema, author_obj):
    """Test basic dumping of a single object."""
    author = author_schema().dump(author_obj)
    assert 'data' in author
    assert 'type' in author['data']
    assert author['data']['type'] == 'authors'
    assert 'id' in author['data']
    assert author['data']['id'] == str(author_obj.id)
    assert 'attributes' in author['data']
    assert 'name' in author['data']['attributes']
    assert author['data']['attributes']['name'] == author_obj.name


def test_export_obj_none_relationship(author_schema, tag_schema, author_obj):
    """Test basic dumping of a single object with a None relationship."""
    author_obj.interests = None
    author = author_schema(include_schemas=(tag_schema, )).dump(author_obj)
    assert 'data' in author
    assert 'type' in author['data']
    assert author['data']['type'] == 'authors'
    assert 'id' in author['data']
    assert author['data']['id'] == str(author_obj.id)
    assert 'attributes' in author['data']
    assert 'name' in author['data']['attributes']
    assert author['data']['attributes']['name'] == author_obj.name
    assert 'relationships' in author['data']
    assert 'interests' in author['data']['relationships']
    assert 'data' in author['data']['relationships']['interests']
    assert author['data']['relationships']['interests']['data'] == []


def test_export_obj_empty_relationship(author_schema, tag_schema, author_obj):
    """Test basic dumping of a single object with an empty list relationship."""
    author_obj.interests = []
    author = author_schema(include_schemas=(tag_schema, )).dump(author_obj)
    assert 'data' in author
    assert 'type' in author['data']
    assert author['data']['type'] == 'authors'
    assert 'id' in author['data']
    assert author['data']['id'] == str(author_obj.id)
    assert 'attributes' in author['data']
    assert 'name' in author['data']['attributes']
    assert author['data']['attributes']['name'] == author_obj.name
    assert 'relationships' in author['data']
    assert 'interests' in author['data']['relationships']
    assert 'data' in author['data']['relationships']['interests']
    assert author['data']['relationships']['interests']['data'] == []
