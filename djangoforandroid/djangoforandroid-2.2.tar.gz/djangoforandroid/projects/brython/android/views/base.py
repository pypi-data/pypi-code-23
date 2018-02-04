from browser import document
import framework
#from mdc import MDCBuild
from mdcframework import Template, Build

from pythoncore import PythonCore

Piton = PythonCore()

from apps import PitonCore

from home import Home
from ide import Ide
from config import Config
from examples import Examples
from server import Server
from new import New
from help import Help



########################################################################
class Base:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        #print("OK")

        framework.select("title").html("Scientific Piton")

        self.views = {}

        Build.styles([
            "css/styles.css",
            "piton_codeeditor/piton_codeeditor.css",
            "piton_codeeditor/syntax_highlight.css",
            #"codepress/codepress.css",
            ])

        Build.scripts([
            "piton_codeeditor/highlight.pack.js",
            #"piton_codeeditor/mousetrap.min.js",
            #"piton_codeeditor/mousetrap-global-bind.min.js",
            #"piton_codeeditor/shortcuts.js",
            "piton_codeeditor/autosize.js",
            "piton_codeeditor/piton_codeeditor.js",
           ])

        self.piton_core = PitonCore()

        self.build()
        super().__init__()



    #----------------------------------------------------------------------
    def build(self):
        """"""

        html = """Open <span style='font-family: mono; font-weight: bold;'>http://{}</span> with any device on local network
            <br><br>
            Happy codding.
            """.format(Piton.local_ip())

        self.dialog_server = Template.Dialog(title="Running as server", cancel='Close')
        self.dialog_server.select('.mdc-dialog__body')[0].html = html
        self.dialog_server.select('.mdc-dialog__footer__button--accept')[0].remove()

        document <= self.dialog_server

        self.mdc_drawer = Template.TemporaryDrawer()
        self.mdc_drawer.select('.mdc-list')[0] <= self.sidebar()



        #self.dialog_server.select('.mdc-dialog__body')[0].style = {'max-height': "50vh"}

        #self.mdc_toolbar = Template.Toolbar(title="Scientific Piton", class_="")
        #self.mdc_toolbar.select('.mdc-toolbar__menu-icon')[0].bind('click', self.mdc_drawer.mdc.open)
        self.container = Template.DIV(Class="main-containder", style={"padding-top": "55px", })

        self.toolbar_elements = {}

        #document <= self.mdc_toolbar
        document <= self.mdc_drawer
        document <= self.container

        #Template.attach()


    #----------------------------------------------------------------------
    def run_server(self, evt=None):
        """"""
        self.mdc_drawer.mdc.close()
        self.dialog_server.mdc.show()



    #----------------------------------------------------------------------
    def sidebar(self):
        """"""

        style = {'color': "#757575",}

        sidebar = []

        #return [

            #Template.ListItem(text="Cells", icon='code', href=framework.url('home'), style=style),
            #Template.ListItem(text="IDE", icon='insert_drive_file', href=framework.url('ide'), style=style),
            #Template.ListItem(text="Examples", icon='content_paste', href=framework.url('home'), style=style),
            ##MDCBuild.ListItem(text="Trash", icon='delete_sweep', href=framework.url('home'), style=style),
            #Template.ListItem(text="Settings", icon='tune', href=framework.url('home'), style=style),
            #Template.ListItem(text="Help", icon='help_outline', href=framework.url('home'), style=style),

            #]


        home = Template.ListItem(text="Cells", icon='code', href='#', style=style)
        home.bind('click', lambda evt:self.set_view('Home'))
        sidebar.append(home)

        ide = Template.ListItem(text="Files", icon='insert_drive_file', href='#', style=style)
        ide.bind('click', lambda evt:self.set_view('Ide'))
        sidebar.append(ide)

        examples = Template.ListItem(text="Examples", icon='content_paste', href='#', style=style)
        examples.bind('click', lambda evt:self.set_view('Examples'))
        sidebar.append(examples)

        config = Template.ListItem(text="Options", icon='tune', href='#', style=style)
        config.bind('click', lambda evt:self.set_view('Config'))
        sidebar.append(config)

        help = Template.ListItem(text="Help", icon='help_outline', href='#', style=style)
        help.bind('click', lambda evt:self.set_view('Help'))
        sidebar.append(help)


        #server = Template.ListItem(text="Run as server...", icon='phonelink', href='#', style=style)
        #server.style = {'margin-top': "100%"}
        #server.bind('click', self.run_server)
        #sidebar.append(server)

        new = Template.ListItem(text="NEW", icon='', href='#', style=style)
        new.bind('click', lambda evt:self.set_view('New'))
        sidebar.append(new)



        return sidebar


    #----------------------------------------------------------------------
    def set_view(self, name):
        """"""
        if name in self.views:
            self.container.clear()
            self.container <= self.views[name].show()

        else:
            view = eval(name)
            view = view(self)
            self.container.clear()
            self.container <= view.show()
            self.views[name] = view

        self.mdc_drawer.mdc.close()
        Template.attach()





main = Base()
main.set_view('Home')

print("WTF")

try:
    document.select('.splash_loading')[0].remove()
except:
    pass


