from browser import window, document
import framework


from mdcframework import Template

from apps import CodeEditor

#from djangoforandroid import Django
#Piton = Django(framework.url("piton_brython"))

#from androidcore import AndroidCore
#Piton = AndroidCore()

from pythoncore import PythonCore
Piton = PythonCore()

########################################################################
class Events:
    """"""

    #----------------------------------------------------------------------
    def connect(self):
        """"""

        #self.button_fab.bind('click', self.interprete)
        #self.menu_icon.bind("click", lambda :self.menu.mdc.toggle())
        #self.menu_new_cell.bind("click", self.new_cell)
        #self.menu_remove_cell.bind("click", self.remove_cell)
        #self.menu_run_all_cell.bind('click', self.run_all_cells)


    ##----------------------------------------------------------------------
    #def new_cell(self, event=None, code="", id=None):
        #""""""
        #ce = CodeEditor(self.main.piton_core, code, id, 'cell')
        #self.cells[str(ce.id)] = ce
        #self.piton_container <= ce.codeblock


    ##----------------------------------------------------------------------
    #def remove_cell(self, event=None):
        #""""""
        #codeblock = document.select('.codeblock-block.on-focus')[0]
        #code_editor = self.cells[codeblock.getAttribute("editor_id")]
        #code_editor.remove()

    ##----------------------------------------------------------------------
    #def interprete(self, event):
        #""""""
        #codeblock = document.select('.codeblock-block.on-focus')[0]
        #code_editor = self.cells[codeblock.getAttribute("editor_id")]

        #code_editor.interprete()


    ##----------------------------------------------------------------------
    #def run_all_cells(self, event):
        #""""""
        #for codeblock in document.select('.codeblock-block'):
            #code_editor = self.cells[codeblock.getAttribute("editor_id")]
            #code_editor.interprete()





########################################################################
class Config(Events):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        self.main = parent

        self.main.mdc_drawer.mdc.close()
        self.main.container.clear()

        self.container = self.build()
        self.connect()

        #return container

    #----------------------------------------------------------------------
    def show(self):
        """"""



        return self.container



    #----------------------------------------------------------------------
    def build(self):
        """"""
        container = Template.DIV(style={'background-color': 'white', 'height': '-webkit-fill-available'})

        self.mdc_toolbar = Template.Toolbar(title="Options", class_="mdc-toolbar--fixed")
        self.mdc_toolbar.select('.mdc-toolbar__menu-icon')[0].bind('click', self.main.mdc_drawer.mdc.open)
        container <= self.mdc_toolbar


        ul = Template.UL(Class="mdc-list mdc-list--two-line", style={"border-bottom": "1px solid #cccccc"})
        item = Template.ListItemSecondary("Root path", Piton.get_path())
        ul <= item
        container <= ul

        ul = Template.UL(Class="mdc-list mdc-list--two-line", style={"border-bottom": "1px solid #cccccc"})
        item = Template.ListItemSecondary("Reset", "Remove all cells")
        item <= Template.Button('Reset', class_='mdc-button--raised', style={'margin-right': '0', 'margin-left': 'auto', })
        ul <= item
        container <= ul



        Template.attach()


        return container




