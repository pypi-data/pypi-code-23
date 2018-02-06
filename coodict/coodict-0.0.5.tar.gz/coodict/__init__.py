"""CooDict - a (Scottish) copy-on-write dictionary class."""

from collections import UserDict
from itertools import chain


class CooDict(UserDict):  # pylint: disable=too-many-ancestors
    """Copy-on-write dictionary class."""

    # pylint:disable=super-init-not-called
    def __init__(self, base=None, overlay=None):
        """Set up base and data (overlay) dicts."""
        self.base = base or {}
        # alias data to overlay for clarity in code/docs
        self.data = self.overlay = overlay or {}
        self.deleted = set()

    def __delitem__(self, key):
        """Update value to Deleted class to mark deletion"""
        # Throw away keys only in overlay
        if key in self.overlay:
            self.overlay.pop(key)
        elif key in self.base and key not in self.deleted:
            self.deleted.add(key)
        else:
            raise KeyError

    def __getitem__(self, key):
        """Return item from overlay, or fall back to base."""
        if key in self.deleted:
            raise KeyError
        if key in self.overlay:
            return self.overlay[key]
        return self.base[key]

    def __setitem__(self, key, value):
        """Clear deleted keys before setting."""
        try:
            self.deleted.remove(key)
        except KeyError:
            pass
        super().__setitem__(key, value)

    def __iter__(self):
        """CooDict iterator."""
        for key in self.base.keys() | self.overlay.keys():
            if key not in self.deleted:
                yield key

    def __len__(self):
        """len of CooDict."""
        return len(self.base.keys() | self.overlay.keys() - self.deleted)

    def __repr__(self):
        """Representation of CooDict."""
        return repr({k: self[k] for k in self.__iter__()})

    def __str__(self):
        """String representation of CooDict."""
        return str(self.__repr__())

    def copy(self):
        """Return a copy of the CooDict (as a CooDict instance)."""
        return CooDict(base=self.base.copy(), overlay=self.overlay.copy())

    def clear(self):
        """Clear the overlay dict."""
        self.overlay = {}
        self.deleted.clear()
