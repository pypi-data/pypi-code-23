#from browser import document, window
import framework
from mdcframework import Template



#from pythoncore import PythonCore
#Piton = PythonCore()



#########################################################################
#class MDCTemplates:
    #""""""

    ##----------------------------------------------------------------------
    #def __init__(self):
        #"""Constructor"""

        #url = framework.url('mdc_button')







########################################################################
class Events:
    """"""

    #----------------------------------------------------------------------
    def connect(self):
        """"""



########################################################################
class Help(Events):
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


        self.mdc_toolbar = Template.Toolbar(title="Help", class_="mdc-toolbar--fixed")
        self.mdc_toolbar.select('.mdc-toolbar__menu-icon')[0].bind('click', self.main.mdc_drawer.mdc.open)
        container <= self.mdc_toolbar




        Template.attach()
        return container


