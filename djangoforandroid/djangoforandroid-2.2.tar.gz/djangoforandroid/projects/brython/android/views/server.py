#from browser import document, window
import framework
from mdcframework import Template


##from djangoforandroid import Django
##Piton = Django(framework.url("piton_brython"))


from pythoncore import PythonCore
Piton = PythonCore()



########################################################################
class Events:
    """"""

    #----------------------------------------------------------------------
    def connect(self):
        """"""



########################################################################
class Server(Events):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """Constructor"""
        self.main = parent

        self.main.mdc_drawer.mdc.close()
        self.main.container.clear()

        self.container = self.build()
        self.connect()


    #----------------------------------------------------------------------
    def show(self):
        """"""


        return self.container





    #----------------------------------------------------------------------
    def build(self):
        """"""

        container = Template.DIV()
        #container = Template.DIV(style={'background-color': 'white'})


        self.mdc_toolbar = Template.Toolbar(title="Server", class_="mdc-toolbar--fixed")
        self.mdc_toolbar.select('.mdc-toolbar__menu-icon')[0].bind('click', self.main.mdc_drawer.mdc.open)
        container <= self.mdc_toolbar
        ip = Piton.local_ip()





        html = """Open <span style='font-family: mono; font-weight: bold;'>http://{{LOCAL_IP}}:{{PORT}}</span> with any device on local network
            <br><br>
            Happy codding.
            """
        container <= Template.P(html)

        Template.attach()
        return container


