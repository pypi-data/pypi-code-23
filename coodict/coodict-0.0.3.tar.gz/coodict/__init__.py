"""CooDict - a (Scottish) copy-on-write dictionary class."""

from collections import UserDict


class CooDict(UserDict):  # pylint: disable=too-many-ancestors
    """Copy-on-write dictionary class."""

    class Deleted():
        """Class used as a marker for deleted keys."""
        pass

    # pylint:disable=super-init-not-called
    def __init__(self, base=None, data=None):
        """Set up base and data (overlay) dicts."""
        self.base = base or {}
        # alias data to overlay for clarity in code/docs
        self.data = self.overlay = data or {}

    def __delitem__(self, key):
        """Update value to Deleted class to mark deletion"""
        self[key] = self.Deleted()

    def __getitem__(self, key):
        """Return item from overlay, or fall back to base."""
        if key in self.overlay:
            if isinstance(self.overlay[key], self.Deleted):
                raise KeyError
            return self.overlay[key]
        else:
            return self.base[key]

    def __repr__(self):
        """repr of merge dicts."""
        return repr(self.merge())

    __str__ = str(__repr__)

    def merge(self):
        """Return a dict containing a merge of overlay and base.
        Overlay overwrites base, and deleted items are discarded."""
        return {k: v for k, v in {**self.base, **self.overlay}.items() if not isinstance(v, self.Deleted)}

    def __len__(self):
        return len(self.merge())

    def copy(self):
        """Return a copy of the CowDict (as a CowDict instance)."""
        return CooDict(base=self.base.copy(), data=self.overlay.copy())

    def clear(self):
        """Clear the overlay dict."""
        self.overlay = {}

    def keys(self):
        """Return keys of merged dicts."""
        return self.merge().keys()

    def values(self):
        """Return values of merged dicts."""
        return self.merge().values()
