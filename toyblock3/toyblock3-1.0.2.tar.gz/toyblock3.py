#  Copyright (C) 2018 Oscar 'dotoscat' Triano

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.

#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import deque

class PoolableMixin:
    """Provide mechanisms to be used by a :class:`Pool`.

    Don't use this class directly.
    """
    __slots__ = ("__pool", "_used")
    def __init__(self, pool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pool = pool
        self._used = False
    def free(self):
        """Free this entity."""
        if not self._used:
            return
        self.__pool.free(self)

class Pool:
    """
    Create a pool of :class:`class_` n_entities.

    Any class passed by parameter it will be mixed with :class:`PoolableMixin`

    Get an object from this pool just creating an instance. This instance
    has the *free* method.

    Parameters:
        class (type): Any class.
        n_entities (int): Number of entities for this pool
        *args: args for creating the instances.
        **kwargs: kwargs for creating the instances.

    Raises:
        NotImplementedError: if the class has not implemented :meth:`reset`.

    Example:
    
        .. code-block:: python
        
            class Body:
                def __init__(self):
                    self.x = 0
                    self.y = 0
                    
                def reset(self):
                    self.x = 0
                    self.y = 0
        
            body_pool = Pool(Body, 10)

            one = body_pool()
            two = body_pool()
            one.free()
            two.free()
        
    """
    def __init__(self, class_, n_entities, *args, **kwargs):
        reset_method = getattr(class_, "reset", None)
        if not (callable(reset_method) and reset_method.__code__.co_argcount):
            raise NotImplementedError("Implement the reset method for {}".format(class_.__name__))
        poolable_class = type(class_.__name__, (PoolableMixin, class_), {})
        self.entities = deque([poolable_class(self, *args, **kwargs) for i in range(n_entities)])

    def free(self, entity):
        entity.reset()
        entity._used = False
        self.entities.append(entity)
        
    def __call__(self, *args, **kwargs):
        """Return an instance from its pool. None if there is not an avaliable entity."""
        if not self.entities:
            return None
        entity = self.entities.pop()
        entity._used = True
        return entity

class System:
    """This is an abstract class which your systems will derive from this."""
    def __init__(self):
        self._entities = deque()
        self._locked = False
        self._add_entity_list = deque()
        self._remove_entity_list = deque()
        
    @property
    def entities(self):
        """Return the current entities that are in this System."""
        return self._entities
    
    def add_entity(self, entity):
        """Add an entity to this system."""
        if self._locked:
            self._add_entity_list.append(entity)
        else:
            self._entities.append(entity)
    
    def remove_entity(self, entity):
        """Remove an entity from entity.
        
        If your entity has implemented the :meth:`free` then call it instead.
        """
        if self._locked:
            self._remove_entity_list.append(entity)
        else:
            self._entities.remove(entity)
    
    def __call__(self):
        """Call the system to compute the entities.
        
        Example:
        
            .. code-block:: python
            
                class PhysicsSystem(toyblock3.System, dt):
                    def __init__(self):
                        super().__init__()
                        self.dt = dt

                    def _update(self, entity):
                        entity.body.update(self.dt)
                        
                physics = PhysicsSystem(STEP)
                physics.add_entity(player)
                
                while not game_over:
                    physics()
        
        """
        if self._locked:
            return
        entities = self._entities
        update = self._update
        self._locked = True
        for entity in entities:
            update(entity)
        self._locked = False
        while self._remove_entity_list:
            self._entities.remove(self._remove_entity_list.pop())
        while self._add_entity_list:
            self._entities.append(self._add_entity_list.pop())

    def _update(self, entity):
        raise NotImplementedError("Define an _update method for this system.")

class ManagedEntityMixin:
    """This mixin is used internally by :class:`Manager`.
    
    Don't use this class directly.
    """
    def reset(self):
        super().reset()
        for system in self.SYSTEMS:
            system.remove_entity(self)

class Manager:
    """A convenient class to manage entities from pools and systems.
    
    Normally you will retrieve an entity from a pool and add it to some systems, then
    when you are done with that entity call its :meth:`free` from inside any system
    which it belongs and finally remove that entity from the systems...

    The manager provides mechanisms that will do all from above for you, cleanly. This
    will create a pool for you and will mix in :class:`ManagedEntityMixin` with the class_.

    The class must have defined *SYSTEMS*, which is a list with instances of a :class:`System`.

    You can retrive an instance from the :class:`Manager` in the same way as :class:`Pool`.

    Parameters:
        class_ (type): The class to use.
        n_entities (int): Number of entities for the pool.
        *args: Args for the Pool.
        **kwargs: Kwargs for the Pool.

    Raises:
        AttributeError: if the class_ has not `SYSTEMS`
        NotImplementedError: if the class has not implemented :meth:`reset`.

    Example:

        .. code-block:: python

            physics_system = PhysicsSystem(-10.)
            sprites_system = SpritesSystem()

            class Player:
                SYSTEMS = (physics_system, sprites_system)
                def __init__(self):
                    self.x = 0
                    self.y = 0
                    self.status = "happy"
                def reset(self):
                    self.x = 0
                    self.y = 0
                    self.status = "happy"

            player_manager = toyblock3.Manager(Player, 4)
            player = player_manager()
            while playing:
                physics_system()
                sprites_system()
    """
    def __init__(self, class_, n_entities, *args, **kwargs):
        systems = getattr(class_, "SYSTEMS", None)
        if not isinstance(systems, (tuple, list)):
            raise AttributeError("Implement SYSTEMS attribute as a list or tuple for {}".format(class_.__name__)) 
        managed_class = type(class_.__name__, (ManagedEntityMixin, class_), {})
        self.pool = Pool(managed_class, n_entities, *args, **kwargs)
        self.systems = systems
        
    def __call__(self, *args, **kwargs):
        entity = self.pool()
        if not entity:
            return entity
        for system in self.systems:
            system.add_entity(entity)
        return entity
