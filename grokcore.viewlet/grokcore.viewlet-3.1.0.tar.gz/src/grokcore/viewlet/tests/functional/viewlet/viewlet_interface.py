"""

Verify that associating viewlets with an interface instead of with a
viewlet manager class works as expected.

Set up the model object to view::

  >>> root = getRootFolder()
  >>> root['cave'] = Cave()

Viewing the cave object should result in the viewlet being displayed,
as it is associated with the interface::

  >>> from zope.testbrowser.wsgi import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open("http://localhost/cave")
  >>> print(browser.contents)
  Me Fred


"""

import grokcore.viewlet as grok
from zope.interface import Interface, implementer

class ICavemenViewletManager(Interface):
    pass

@implementer(ICavemenViewletManager)
class CavemenViewletManager(grok.ViewletManager):
    grok.name('manage.cavemen')

class FredViewlet(grok.Viewlet):
    grok.viewletmanager(ICavemenViewletManager)

    def render(self):
        return u"Me Fred"

class Cave(grok.Context):
    pass

class Index(grok.View):
    pass
