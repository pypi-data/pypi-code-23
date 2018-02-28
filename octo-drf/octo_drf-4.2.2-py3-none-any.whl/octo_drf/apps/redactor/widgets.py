"""
Now we use https://gitlab.com/octoberweb/trumbowyg-redactor
Main repo with django app https://bitbucket.org/fogstream/django-fs-trumbowyg/
"""
from trumbowyg.widgets import TrumbowygWidget


class OctoRedactorWidget(TrumbowygWidget):
    """
    Base widget class for inheritance
    """
    pass

