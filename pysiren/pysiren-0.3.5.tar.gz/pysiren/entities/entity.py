from typing import Dict, List

from ..error import *
from ..renderer import SirenBase
from .link import Link
from .action import Action
from .rel import RelValue


class Entity(SirenBase):
    def __init__(self,
                 classes: List[str],
                 title: str=None,
                 properties: Dict[str, object]=None,
                 entities: List["Entity"]=None,
                 links: List[Link]=None,
                 actions: List[Action] = None):
        self._class = classes
        self._title = title

        self._properties = None
        self._entities = None
        self._links = None
        self._actions = None

        self.set_properties(properties)
        self.set_entities(entities)
        self._links = links
        self._actions = actions

    def get_class(self):
        return self._class

    def get_properties(self):
        return self._properties

    def set_properties(self, properties):
        if properties is not None and type(properties) != dict:
            raise SirenEntityError("Properties are of type {}, dictionary expected!", type(properties))

        self._properties = properties

    def add_property(self, name, value):
        self._properties[name] = value

    def remove_property(self, name):
        del self._properties[name]

    def set_entities(self, entities):
        self._entities = entities

    def add_entity(self, entity: 'Entity'):
        if self._entities is None:
            self.set_entities([entity])
        else:
            self._entities.append(entity)

    def set_links(self, links: List[Link]):
        if links is not None and type(links) != list:
            raise SirenEntityError("Links are of type {}, list expected!", type(list))

        self._links = links

    def set_actions(self, actions: List[Action]):
        if actions is not None and type(actions) != list:
            raise SirenEntityError("Actions are of type {}, list expected!", type(actions))

        self._actions = actions

    def add_link(self, link: Link):
        if self._links is None:
            self.set_links([link])
        else:
            self._links.append(link)

    def add_action(self, action: Action):
        if self._actions is None:
            self.set_actions([action])
        else:
            self._actions.append(action)

    def get_links(self):
        return self._links

    def get_actions(self):
        return self._actions


class SubEntity(Entity):
    pass


class EmbeddedLinkSubEntity(SubEntity):
    pass


class EmbeddedRepresentationSubEntity(SubEntity):
    def __init__(self,
                 classes: List[str],
                 rel: RelValue,
                 title: str = None,
                 properties: Dict[str, object] = None,
                 entities: List[SubEntity] = None,
                 links: List[Link] = None,
                 actions:List[Action] = None):
        Entity.__init__(self, classes, title, properties, entities, links, actions)
        self._rel = rel