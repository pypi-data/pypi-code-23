from pyno.html_tags_autocomplete import HTMLTagList
from pyno.tree_model import HTML, html, TreeNode, TreeSub
from pyno.browser_preview import browser_preview


# Set default settings for void elements
void_elements = 'br hr img input link meta area base col command embed keygen param source track wbr'.split(' ')
for tag in void_elements:
    TreeNode.defaults[tag] = {'_void_element': True}


from pyno.costum_tags import CDATA, Include


# todo consider adding some magic to add default parameters from construct as parameters on the object during initialization. (*It's funky but nice in practice*)

from werkzeug.serving import run_simple
from werkzeug.wrappers import Request, Response


def serve_example(content, host='localhost', port=8080):
    @Request.application
    def application(request):
        return Response(str(content), mimetype='text/HTML')
    run_simple(host, port, application, use_reloader=True)

__version__ = "0.0.5-dev"
