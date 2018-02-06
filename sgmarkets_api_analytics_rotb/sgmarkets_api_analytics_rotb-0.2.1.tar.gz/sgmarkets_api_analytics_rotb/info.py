
import os
from IPython.display import display, Markdown


def info():
    """
    """
    _dir = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(_dir, 'markdown', 'info.md')
    with open(path, 'r') as f:
        md = f.read()
        display(Markdown(md))
