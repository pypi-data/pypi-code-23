import sys
import inspect
from pathlib import Path


def module_parent(level=1, caller_file=None):
    """
    activate relative import in __name__ == '__main__'

    example:
    __package__ = module_parent()
    importlib.import_module(__package__)

    """
    if not caller_file:
        stack = inspect.stack()
        caller_file = stack[1].filename

    file = Path(caller_file).resolve()
    parent, top = file.parent, file.parents[level]

    sys.path.append(str(top))
    try:
        sys.path.remove(str(parent))
    except ValueError:
        pass

    return '.'.join(parent.parts[len(top.parts):])
