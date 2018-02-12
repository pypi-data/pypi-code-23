from pysiren import *
from nose.tools import *


def test_siren_entity_creation():
    entity = Entity('name')

    assert(entity is not None)
    assert(entity.get_class() == 'name')


def test_siren_entity_properties():
    entity = Entity('name')

    assert(entity.get_properties() is None)

    entity.set_properties(None)
    assert(entity.get_properties() is None)

    properties = {'a': 1, 'b': 'c', 'd': [1, 2, 3]}
    entity.set_properties(properties)
    assert(entity.get_properties() == properties)


@raises(SirenEntityError)
def test_siren_entity_properties_error():
    entity = Entity('name')
    entity.set_properties('explode!')


def test_actions():
    entity = Entity('name')

    expected_actions = [
        Action("test-action", "example.com/action"),
        Action("test-action2", "example.com/action2")
    ]
    for a in expected_actions:
        entity.add_action(a)

    assert entity.get_actions() == expected_actions

    entity.set_actions(None)
    assert entity.get_actions() is None

    entity.set_actions(expected_actions)
    assert entity.get_actions() == expected_actions


def test_links():
    entity = Entity('name')

    expected_links = [
        Link(['self'], 'example.com/self'),
        Link(['up'], 'example.com')
    ]
    for a in expected_links:
        entity.add_link(a)

    assert entity.get_links() == expected_links

    entity.set_links(None)
    assert entity.get_links() is None

    entity.set_links(expected_links)
    assert entity.get_links() == expected_links
