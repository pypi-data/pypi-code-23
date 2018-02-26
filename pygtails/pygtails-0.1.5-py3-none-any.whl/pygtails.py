"""A simple wrapper around pygame.

Game        implements engine functionality. Subclass to build games.
GameObject  A simple class to provide a more intuitive approach to gamedev.
"""

#TODO: Create a MonoBehaviour-esque class to provide more flexibility (and also
#      so I'm not redefining and redocumenting the same ten methods twice.

import pygame
import sys

from pygame.time import Clock
from pygame.event import Event

class Game(object):
    
    """A class that handles pygame events, input, and mouse-collision.
        
    *resolution* is a 2-tuple of integers that specify the width and height
    of the screen.

    *title* is a string used as the title of the window.
        
    *flags* is an integer flag representing the different controls over the
    display mode that are active. For a full list of the different flags,
    see :ref:`Pygame Display Mode Flags`. For more information on how flags
    work, see :doc:`the Flags tutorial <flag-tut>`.

    Public Methods:

        | main, quit, on_focus, on_key_down, on_key_up, on_mouse_move,
        | on_mouse_up, on_mouse_down, on_resize, update, add_object,
        | destroy_object, key_is_pressed

    Instance variables:

        | screen

    """

    def __init__(self, resolution, title, flags=0, depth=0):
        pygame.init() 
        self._screen = pygame.display.set_mode(resolution, flags, depth)
        pygame.display.set_caption(title)

        self._cur_id = 0
        self._objects = {}
        self._contains_mouse = {}
        self._clicked = {}

        self._keys_pressed = pygame.key.get_pressed()

        self._handle = {pygame.QUIT:            self.quit,
                        pygame.ACTIVEEVENT:     self.on_focus,
                        pygame.KEYDOWN:         self.on_key_down,
                        pygame.KEYUP:           self.on_key_up,
                        pygame.MOUSEMOTION:     self.on_mouse_move,
                        pygame.MOUSEBUTTONUP:   self.on_mouse_up,
                        pygame.JOYAXISMOTION:   self.ignore,
                        pygame.JOYBALLMOTION:   self.ignore,
                        pygame.JOYHATMOTION:    self.ignore,
                        pygame.JOYBUTTONDOWN:   self.ignore,
                        pygame.MOUSEBUTTONDOWN: self.on_mouse_down,
                        pygame.VIDEORESIZE:     self.on_resize,
                        pygame.VIDEOEXPOSE:     self.ignore,
                        pygame.USEREVENT:       self.ignore}

    def main(self):
        """The main loop. Call this to run the game."""
        while True:
            for event in pygame.event.get():
                self._handle[event.type](event)

            self._keys_pressed = pygame.key.get_pressed()
            buttons = pygame.mouse.get_pressed()
            pos = pygame.mouse.get_pos()
            rel = pygame.mouse.get_rel()

            event = Event(pygame.MOUSEMOTION, buttons=buttons,
                          pos=pos, rel=rel)
            for obj in self._contains_mouse.values():
                obj.on_mouse_stay(event)

            self.update()
            for obj in self._objects.values():
                obj.update()

    def quit(self, event):
        """The method called when the exit button is pressed.

        *event* is a pygame ``QUIT`` event. It has no event attributes.
        
        This method is predefined as::
        
            pygame.quit()
            sys.exit()
        
        Redefine it if you need more control.
        """
        pygame.quit()
        sys.exit()

    def on_focus(self, event):
        """This method is called whenever the window loses or gains focus.

        *event* is a pygame ``ACTIVEEVENT`` event. It contains the event
        attributes ``gain`` and ``state``.

        *event.gain* is an integer. It has a value of 1 when the window comes
        into focus or when the mouse enters the window. It has a value of 0
        when the window goes out of focus or when the mouse leaves the window.

        *event.state* is an integer. It has a value of 1 when the mouse exits or
        leaves the window. It has a value of 2 when the window gains or loses
        focus.

        This method is not predefined.
        """
        pass

    def on_key_down(self, event):
        """This method is called whenever a key is pressed.
        
        *event* is a pygame ``KEYDOWN`` event. It contains the event
        attributes ``unicode``, ``key``, and ``mod``.

        *event.unicode* is the unicode representation of the key being pressed.

        *event.key* is a pygame keycode representing the key being pressed.
        For a full list key constants, see :ref:`Pygame Keycodes`.

        *event.mod* is a pygame key mod flag representing the "modulating"
        keys (shift, ctrl, alt, etc.) being pressed when the current key was
        pressed. For a list of these flags, see :ref:`Pygame Key Mod Flags`.

        This method is not predefined.
        """
        pass

    def on_key_up(self, event):
        """This method is called whenever a key is released.

        *event* is a pygame ``KEYUP`` event. It contains the event attributes
        ``key`` and ``mod``.

        *event.key* is a pygame keycode representing the key being released.
        For a full list key constants, see :ref:`Pygame Keycodes`.

        *event.mod* is a pygame key mod flag representing the "modulating" keys
        (shift, ctrl, alt, etc.) pressed when the current key was released.
        For a full list of these flags, see :ref:`Pygame Key Mod Flags`.

        This method is not predefined.
        """
        pass

    def on_mouse_move(self, event):
        """This method is called whenever the mouse is moved.

        *event* is a pygame ``MOUSEMOTION`` event. It contains the event
        attributes ``pos``, ``rel``, and ``buttons``.
          
        *event.pos* is a 2-tuple of integers representing the x and y
        coordinates of the mouse.

        *event.rel* is a 2-tuple of integers representing the change in x and y
        coordinates since the last time this function was called.

        *event.buttons* is a 3-tuple of integers representing the amount of
        mouse buttons being pressed. Index 0 represents the left mouse button,
        1 represents the middle mouse button, 2 represents the right mouse
        button. If the mouse button is down, the value is 1, 0 if it's up.

        This method is predefined to implement the on_mouse_[enter, exit, drag]
        functions.
        
        If you aren't satisfied with the implementation, feel free
        to redefine it. If you want to keep the implementation but also add
        additional functionality call super().on_mouse_move(event) when you're
        redefining the function.
        """
        #TODO: Add support for sleeping vs awake objects
        for ID, obj in self._objects.items():
            mouse_is_colliding = event.pos in obj
            if not obj._contains_mouse and mouse_is_colliding:
                self._contains_mouse[ID] = obj
                obj._contains_mouse = True
                obj.on_mouse_enter(event)
            elif obj._contains_mouse and not mouse_is_colliding:
                del self._contains_mouse[ID]
                obj._contains_mouse = False
                obj.on_mouse_exit(event)

        for obj in self._clicked.values():
            obj.on_mouse_drag(event)

    def on_mouse_up(self, event):
        """This method is called whenever a mouse button is released.

        *event* is a pygame ``MOUSEBUTTONUP`` event. It contains the event
        attributes ``pos`` and ``button``.

        *event.pos* is a 2-tuple of integers representing the x and y
        coordinates of the mouse when it was released.

        *event.button* is an integer representing the button being released. 1
        represents the left mouse button, 2 represents the middle mouse button,
        and 3 represents the right mouse button.

        This method is predefined to implement the GameObject.on_mouse_up
        method and to update internal data about whether or not an object is
        clicked.

        To redefine this method while keeping the implementation call
        super().on_mouse_up(event) at the top of your function.
        """
        if event.button == 1:
            for obj in self._clicked.values():
                obj.on_mouse_up(event)
            self._clicked.clear()

    def on_mouse_down(self, event):
        """This method is called whenever a mouse button is pressed.

        *event* is a pygame ``MOUSEBUTTONDOWN`` event. It contains the event
        attributes ``pos`` and ``button``.

        *event.pos* is a 2-tuple of integers representing the x and y
        coordinates of the mouse when it was released.

        *event.button* is an integer representing the button being pressed. 1
        represents the left mouse button, 2 represents the middle mouse button,
        and 3 represents the right mouse button.

        This method is predefined to implement the GameObject.on_mouse_down
        method and to update internal data bout whether or not an object is
        clicked.

        To redefine this method while keeping the implementation, call
        super().on_mouse_up(event) at the top of your function.
        """
        if event.button == 1:
            for obj in self._contains_mouse.values():
                obj.on_mouse_down(event)
            self._clicked.update(self._contains_mouse)

    def on_resize(self, event):
        """This method is called whenever the window is resized.
        
        *event* is a pygame ``VIDEORESIZE`` event. it contains the event 
        attributes ``size``, ``w``, and ``h``.

        *event.size* is a 2-tuple of integers representing the width and height
        of the screen.

        *event.w* is an integer representing the width of the screen.

        *event.h* is an integer representing the height of the screen.

        This method is not predefined.
        """
        pass

    def update(self):
        """This method is called every frame.

        This method is not predefined.
        """
        pass

    def add_object(self, other):
        """Add a GameObject ``other`` to the Game and return its id."""
        # TODO: provide full documentation for the functions and attributes
        #       to implement if not GameObject

        obj_id = self._cur_id
        self._objects[obj_id] = other
        self._cur_id += 1
        return obj_id

    def destroy_object(self, _id):
        """Destroys the object with the given id from the game.

        Note: Does not "undraw" the object. This must be done manually (for now)
        """
        del self._objects[_id]
        for name in ("contains_mouse", "clicked"):
            D = getattr(self, "_"+name)
            if _id in D: del D[_id]

    def key_is_pressed(self, key):
        """Return True if a key is pressed, False if not.

        *key* is pygame keycode.
        For a full list of keycodes, see :ref:`Pygame Keycodes`.
        """
        return self._keys_pressed[key]

    @property
    def screen(self):
        """The pygame Surface used to draw and blit images to the screen."""
        return self._screen

class GameObject(object):

    """A simple class to (hopefully) make pygame more intuitive.

    *game* is the pygame.Game that this GameObject will be added to.

    Intializing a GameObject modifies internal data in the Game it's
    instantiated by.

    Public Methods:

        | update, on_mouse_enter, on_mouse_exit, on_mouse_stay, on_mouse_down,
        | on_mouse_up, on_mouse_drag, move

    Instance Variables:

        | game, ID

    """

    def __init__(self, game):
        self._game = game
        self._contains_mouse = False

        self._id = game.add_object(self)

    def update(self):
        """This method is called every frame.

        This method is not predefined.
        """
        pass

    def on_mouse_enter(self, event):
        """This method is called whenever the mouse enters this object.

        *event* is a pygame ``MOUSEMOTION`` event. It contains the event
        attributes ``pos``, ``rel``, and ``buttons``.
          
        *event.pos* is a 2-tuple of integers representing the x and y
        coordinates of the mouse.

        *event.rel* is a 2-tuple of integers representing the change in x and y
        coordinates since the last time this function was called.

        *event.buttons* is a 3-tuple of integers representing the amount of
        mouse buttons being pressed. Index 0 represents the left mouse button,
        1 represents the middle mouse button, 2 represents the right mouse
        button. If the mouse button is down, the value is 1, 0 if it's up.

        This method is not predefined.
        """
        pass

    def on_mouse_exit(self, event):
        """This method is called whenever the mouse exits this object.

        *event* is a pygame ``MOUSEMOTION`` event. It contains the event
        attributes ``pos``, ``rel``, and ``buttons``.
          
        *event.pos* is a 2-tuple of integers representing the x and y
        coordinates of the mouse.

        *event.rel* is a 2-tuple of integers representing the change in x and y
        coordinates since the last time this function was called.

        *event.buttons* is a 3-tuple of integers representing the amount of
        mouse buttons being pressed. Index 0 represents the left mouse button,
        1 represents the middle mouse button, 2 represents the right mouse
        button. If the mouse button is down, the value is 1, 0 if it's up.

        This method is not predefined.
        """
        pass

    def on_mouse_stay(self, event):
        """This method is called each frame the mouse is within this object.

        *event* is a pygame ``MOUSEMOTION`` event. It contains the event
        attributes ``pos``, ``rel``, and ``buttons``.
          
        *event.pos* is a 2-tuple of integers representing the x and y
        coordinates of the mouse.

        *event.rel* is a 2-tuple of integers representing the change in x and y
        coordinates since the last time this function was called.

        *event.buttons* is a 3-tuple of integers representing the amount of
        mouse buttons being pressed. Index 0 represents the left mouse button,
        1 represents the middle mouse button, 2 represents the right mouse
        button. If the mouse button is down, the value is 1, 0 if it's up.

        This method is not predefined.
        """
        pass

    def on_mouse_drag(self, event):
        """This method is called each frame this object is dragged by the mouse.

        *event* is a pygame ``MOUSEMOTION`` event. It contains the event
        attributes ``pos``, ``rel``, and ``buttons``.
          
        *event.pos* is a 2-tuple of integers representing the x and y
        coordinates of the mouse.

        *event.rel* is a 2-tuple of integers representing the change in x and y
        coordinates since the last time this function was called.

        *event.buttons* is a 3-tuple of integers representing the amount of
        mouse buttons being pressed. Index 0 represents the left mouse button,
        1 represents the middle mouse button, 2 represents the right mouse
        button. If the mouse button is down, the value is 1, 0 if it's up.

        This method is not predefined.
        """
        pass

    def on_mouse_down(self, event):
        """This method is called when the mouse is pressed inside this object.

        *event* is a pygame ``MOUSEBUTTONDOWN`` event. It contains the event
        attributes ``pos`` and ``button``.

        *event.pos* is a 2-tuple of integers representing the x and y
        coordinates of the mouse when it was released.

        *event.button* is an integer representing the button being pressed. 1
        represents the left mouse button, 2 represents the middle mouse button,
        and 3 represents the right mouse button.

        This method is not predefined.
        """
        pass

    def on_mouse_up(self, event):
        """This method is called on mouse up if this object is clicked.

        *event* is a pygame ``MOUSEBUTTONUP`` event. It contains the event
        attributes ``pos`` and ``button``.

        *event.pos* is a 2-tuple of integers representing the x and y
        coordinates of the mouse when it was released.

        *event.button* is an integer representing the button being released. 1
        represents the left mouse button, 2 represents the middle mouse button,
        and 3 represents the right mouse button.

        This method is not predefined.
        """
        pass

    def ignore(self, event):
        pass

    @property
    def game(self):
        """The pygtails.Game object that this object is a part of."""
        return self._game

    @property
    def ID(self):
        """An integer that represents this object's id."""
        return self._id

class Circle(GameObject):

    """A GameObject with a circular "hitmask".

    *game* is the Game this object is a part of.

    *corner* is a 2-tuple of integers representing the x and y coordinates of
    the upper-left corner of the bounding square of circle.

    *radius* is a numeric value representing the radius of the circle.

    Initializing a Circle will modify internal data in the Game it's
    instantiated with.

    Public Methods:

        | update, on_mouse_enter, on_mouse_exit, on_mouse_stay, on_mouse_down,
        | on_mouse_up, on_mouse_drag, move

    Instance Variables:

        | game, ID, center, corner, radius

    """

    def __init__(self, game, corner, radius):
        super().__init__(game)
        x, y = corner
        self._corner = corner
        self._center = x+radius, y+radius
        self._radius = radius

    @property
    def corner(self):
        """A 2-tuple of integers representing the center of the circle.

        Setting this will change the ``corner`` and ``center`` attributes.
        """
        return self._corner
    @corner.setter
    def corner(self, other):
        x, y = other
        self._corner = other
        self._center = x+self.radius, y+self.radius

    @property
    def radius(self):
        """An integer representing the radius of the circle.
        
        Setting this will change the ``radius`` and ``center`` attributes.
        """
        return self._radius
    @radius.setter
    def radius(self, other):
        self._center = (self._x+radius, self._y+radius)
        self._radius = radius

    @property
    def center(self):
        """A 2-tuple of integers representing the center of the circle.

        Setting this will change the ``center`` and ``corner`` attributes.
        """
        return self._center
    @center.setter
    def center(self, other):
        x, y = other
        corner = x-self.radius, y-self.radius
        self._corner = corner

        self._center = other

    def __contains__(self, other):
        otherx, othery = other
        x, y = self.center
        return self.radius**2 >= (x-otherx)**2 + (y-othery)**2

class Rectangle(GameObject):
    """A GameObject with a rectangular "hitmask".

    *game* is the Game this object is a part of.

    *corner* is a 2-tuple of integers representing the x and y coordinates of
    the upper-left corner of the rectangle.

    *width* is an integer representing the width of the rectangle.

    *height* is an integer representing the height of the rectangle.

    Initializing a Rectangle will modify internal data in the Game it's
    instantiated with.

    Public Methods:

        | update, on_mouse_enter, on_mouse_exit, on_mouse_stay, on_mouse_down,
        | on_mouse_up, on_mouse_drag, move

    Instance Variables:

        | game, ID, corner, width, height
    
    """

    def __init__(self, game, corner, width, height):
        super().__init__(game)
        self._corner = corner
        x, y = corner
        self._width = width
        self._height = height
        self._corners = ((x,y), (x+width,y), (x+width,y+height), (x,y+height))

    @property
    def corner(self):
        """The upper left corner of the rectangle.

        A 2-tuple of integers that represent the x and y coordinates of
        the upper-left corner of the rectangle.

        This attribute is mutable.
        """
        return self._corner
    @corner.setter
    def corner(self, other):
        x, y = other
        self._corner = other

    @property
    def width(self):
        """An integer that represents the width of the rectangle.

        This attribute is mutable.
        """
        return self._width
    @width.setter
    def width(self, other):
        self._width = other

    @property
    def height(self):
        """An integer that represents the height of the rectangle.

        This attribute is mutable.
        """
        return self._height
    @height.setter
    def height(self, other):
        self._height = other

    @property
    def corners(self):
        """A tuple of all of the corners of the rectangle.
        
        A 2-dimensional tuple, where the inner tuples are 2-tuples of integers
        representing the x and y coordinates of the different corners of the
        rectangle.

        The order that the points appear are top-left, top-right, bottom-right,
        bottom-left.

        This attribute is immutable.
        """
        return self._corners

    def __contains__(self, other):
        otherx, othery = other
        x, y = self.corner
        contains = (x <= otherx <= x+self.width and
                    y <= othery <= y+self.height)

        return contains
