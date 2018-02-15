import os.path

__all__ = [
    "__name__", "__summary__", "__url__", "__version__",
    "__author__", "__email__", "__license__"
]


try:
    base_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    base_dir = None


__title__   = "makebib"
__summary__ = "A simple script to generate a local bib file from a central database."
__url__     = 'https://gitlab.com/Verner/makebib'
__version__ = "0.2.2"
__author__  = "Jonathan L. Verner"
__email__   = "jonathan@temno.eu"
__license__ = "MIT"
