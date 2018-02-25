"""An importer that will import Doozer packages using Henson imports."""

from importlib.machinery import PathFinder
import sys

__all__ = ('install', 'install_fallback')


class FallbackFinder(PathFinder):
    """Fall back to Henson packages through Doozer imports.

    When importing a Doozer package, if no matching package is found,
    the Henson version will be imported instead.
    """

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        """Try to find the spec as a Henson import."""
        # If path is not None, we're performing a relative import and
        # can let Python's regular import machinery run its course.
        if not (path is None and fullname.startswith('doozer')):
            return None

        henson_name = fullname.replace('doozer', 'henson', 1)

        return super().find_spec(henson_name, path, target)


class Finder(PathFinder):
    """Import Doozer packages through Henson imports.

    When importing a Henson package, the Doozer version will be given
    preference and, will be imported instead of the Henson version. If
    only the Henson version of the package is installed, though, this
    meta path finder will do nothing.
    """

    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        """Try to find the spec as a Doozer import."""
        # If path is not None, we're performing a relative import and
        # can let Python's regular import machinery run its course.
        if not (path is None and fullname.startswith('henson')):
            return None

        doozer_name = fullname.replace('henson', 'doozer', 1)

        return super().find_spec(doozer_name, path, target)


def install():
    """Install a finder to import Doozer packages when possible."""
    sys.meta_path.insert(0, Finder)


def install_fallback():
    """Install a finder to fall back to Henson packages.

    Henson packages will import from Henson rather than Doozer. To
    ensure that both Doozer and Henson are imported, this will install
    both finders.
    """
    install()

    # This operation is done second because it's constant time whereas
    # install uses a linear time operation.
    sys.meta_path.append(FallbackFinder)
