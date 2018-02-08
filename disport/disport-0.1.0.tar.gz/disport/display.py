# -*- coding: utf-8 -*-

import sys

class Resolution:
    """Stores width and height of a certain resolution.

    Provides the following methods:
        1) get_x()
        2) get_y()

    Provides the following operators:
        1) str(resolution)
        2) resolution1 < resolution2
        3) resolution1 > resolution2
        4) resolution1 == resolution2
        5) resolution1 != resolution2
        5) resolution1 <= resolution2
        5) resolution1 >= resolution2
    """
    def __init__(self, resolution):
        """Assume that the resolution is provided as a string
        in the format WxH.
        """
        # Split at 'x' and store dimensions as integers.
        try:
            x, y = resolution.strip().split("x")
            self._x = int(x)
            self._y = int(y)
        
        # If not possible, set to 0.
        except ValueError:
            self._x = 0
            self._y = 0

    def get_x(self):
        """Return width."""
        return self._x

    def get_y(self):
        """Return height."""
        return self._y

    def __str__(self):
        """Return resolution in the format WxH,
        so xrandr can process it.
        """
        return "x".join((str(self._x), str(self._y)))

    def __lt__(self, other):
        """Check if own dimenions are smaller
        than the dimenions of another resolution.
        If it’s not clear by the widths, compare the heights.
        """
        if isinstance(other, Resolution):
            if self._x < other.get_x():
                return True
            elif self._x == other.get_x():
                return self._y < other.get_y()
            else:
                return False
        else:
            return NotImplemented

    def __gt__(self, other):
        """Check if own dimenions are bigger
        than the dimenions of another resolution.
        If it’s not clear by the widths, compare the heights.
        """
        if isinstance(other, Resolution):
            if self._x > other.get_x():
                return True
            elif self._x == other.get_x():
                return self._y > other.get_y()
            else:
                return False
        else:
            return NotImplemented

    def __eq__(self, other):
        """Check if own dimensions are equal to another resolution."""
        if isinstance(other, Resolution):
            return self._x == other.get_x() and self._y == other.get_y()
        else:
            return NotImplemented

    def __nq__(self, other):
        """Check if own dimenions are unequal to another resolution."""
        if isinstance(other, Resolution):
            return not(self == other)
        else:
            return NotImplemented

    def __le__(self, other):
        """Check if own dimenions are smaller
        than or equal to the dimenions of another resolution.
        """
        if isinstance(other, Resolution):
            return self < other or self == other
        else:
            return NotImplemented

    def __ge__(self, other):
        """Check if own dimenions are smaller
        than or equal to the dimenions of another resolution.
        """
        if isinstance(other, Resolution):
            return self > other or self == other
        else:
            return NotImplemented


class Display:
    """Stores name and resolutions of a display.

    Provides the following methods:

        1) get_resolutions()

    Provides the following operators:

        1) str(display)
        2) resolution in display
        3) display1 & display2
        4) display1 == display2
        5) display1 != display2
    """
    def __init__(self, name, resolutions):
        """Store name and resolutions."""
        # Apply name
        try:
            self._name = str(name)
        except ValueError:
            print("Could not apply name to display.")
            sys.exit(1)

        # Apply all legitimate resolutions.
        self._resolutions = (res for res in resolutions if res.get_x() > 0)

    def get_resolutions(self):
        """Returns list of available resolutions."""
        return self._resolutions

    def __str__(self):
        """Returns the name of the display as a string."""
        return self._name

    def __contains__(self, resolution):
        """Returns True if resolution is available to display."""
        if isinstance(resolution, Resolution):
            return resolution in self._resolutions
        else:
            return NotImplemented

    def __and__(self, other):
        """Returns list of resolutions shared
        between display1 and display2.
        """
        if isinstance(other, Display):
            return (res for res in self._resolutions if res in other)
        else:
            return NotImplemented

    def __eq__(self, other):
        """Returns True if the names of
        display1 and display2 are identical.
        """
        if isinstance(other, Display) or isinstance(other, str):
            return self._name == str(other)
        else:
            return NotImplemented

    def __nq__(self, other):
        """Returns True if the names of
        display1 and display2 are different.
        """
        if isinstance(other, Display) or isinstance(other, str):
            return not(self == other)
        else:
            return NotImplemented
