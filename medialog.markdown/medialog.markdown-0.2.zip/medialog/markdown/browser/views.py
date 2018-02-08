from Products.Five.browser import BrowserView
#from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone import api


class RenderFromMarkdown(BrowserView):
    """ mardown to html.
    """
 
    # template = ViewPageTemplateFile('render_markdownt.pt')

    def __call__(self, *args, **kw):
        return self.render_markdown()
         
    def render_markdown(self, markdown=""):
        """Return the preview as a stringified HTML document."""
        value = self.request.markdown
        portal_transforms = api.portal.get_tool(name='portal_transforms')
        data = portal_transforms.convertTo('text/html', value, mimetype='text/x-web-markdown')
        html = data.getData()
        return html