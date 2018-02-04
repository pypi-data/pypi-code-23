from browser import window, document
#import framework


#from mdcframework import Template

from mdcframework import Template
#from mdcframework import templates


from apps import CodeEditor

#from djangoforandroid import Django
#Piton = Django(framework.url("piton_brython"))

from pythoncore import PythonCore
Piton = PythonCore()


########################################################################
class Events:
    """"""

    #----------------------------------------------------------------------
    def connect(self):
        """"""

        self.button_fab.bind('click', self.interprete)
        self.menu_icon.bind("click", lambda :self.menu.mdc.toggle())
        self.menu_new_cell.bind("click", self.new_cell)
        self.menu_remove_cell.bind("click", self.remove_cell)
        self.menu_run_all_cell.bind('click', self.run_all_cells)
        self.menu_run_as_server.bind('click', self.main.run_server)


    #----------------------------------------------------------------------
    def new_cell(self, event=None, code="", id=None):
        """"""
        ce = CodeEditor(self.main.piton_core, code, id, 'cell')
        self.cells[str(ce.id)] = ce
        self.piton_container <= ce.codeblock

        try:
            window.update_all()
        except:
            pass

    #----------------------------------------------------------------------
    def remove_cell(self, event=None):
        """"""
        codeblock = document.select('.codeblock-block.on-focus')[0]
        code_editor = self.cells[codeblock.getAttribute("editor_id")]
        code_editor.remove()

    #----------------------------------------------------------------------
    def interprete(self, event):
        """"""
        codeblock = document.select('.codeblock-block.on-focus')[0]
        code_editor = self.cells[codeblock.getAttribute("editor_id")]

        code_editor.interprete()


    #----------------------------------------------------------------------
    def run_all_cells(self, event):
        """"""
        for codeblock in document.select('.codeblock-block'):
            code_editor = self.cells[codeblock.getAttribute("editor_id")]
            code_editor.interprete()





########################################################################
class Home(Events):
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
        #if document.select('.codeblock-block'):
            #document.select('.codeblock-block')[0].class_name += " on-focus"

        return self.container



    #----------------------------------------------------------------------
    def build(self):
        """"""
        container = Template.DIV()

        self.cells = {}


        self.mdc_toolbar = Template.Toolbar(title="Scientific Piton", class_="mdc-toolbar--fixed")
        self.mdc_toolbar.select('.mdc-toolbar__menu-icon')[0].bind('click', self.main.mdc_drawer.mdc.open)
        container <= self.mdc_toolbar

        self.button_fab = Template.ButtonFab('bug_report', class_="piton-float_button")
        container <= self.button_fab

        self.menu = Template.SimpleMenu()

        self.menu_new_cell = Template.MenuItem("New cell", class_='piton-new_cell')
        self.menu.mdc.add_item(self.menu_new_cell)

        self.menu_run_all_cell = Template.MenuItem("Run all cells", class_='piton-run_all_cell')
        self.menu.mdc.add_item(self.menu_run_all_cell)

        self.menu.mdc.add_item(Template.MenuItemDivider())

        self.menu_run_as_server = Template.MenuItem("Run as server...", class_='piton-run_as_server')
        self.menu.mdc.add_item(self.menu_run_as_server)

        self.menu_remove_cell = Template.MenuItem("Remove cell", class_='piton-remove_cell')
        self.menu.mdc.add_item(self.menu_remove_cell)

        self.menu_icon = Template.Icon(icon="more_vert", class_="mdc-toolbar__icon toggle")

        self.mdc_toolbar.select('.mdc-toolbar__section--align-end')[0] <= self.menu_icon
        self.mdc_toolbar.select('.mdc-menu-anchor')[0] <= self.menu

        self.piton_container = Template.DIV(Class="piton-container")
        self.piton_container.style = {'position': "absolute",
                                      'overflow': 'scroll',
                                      'height': '100%'}

        container <= self.piton_container


        for cell in Piton.cells():
            self.new_cell(self.main.piton_core, cell['fields']['code'], cell['pk'])

        #if document.select('.codeblock-block'):
            #document.select('.codeblock-block')[0].class_name += " on-focus"

        try:
            window.update_all()
        except:
            pass

        Template.attach()


        return container






    ##----------------------------------------------------------------------
    #def set_toolbar_menu(self, icon, menu=None):
        #""""""

        ##if label in self.toolbar_elements:
            ###icon.remove()
            ###menu.remove()
            ##icon, menu = self.toolbar_elements[label]
            ##icon.style = {'display': 'block',}
            ##if menu:
                ##icon.bind("click", lambda :menu.mdc.toggle())

        ##else:
        #self.mdc_toolbar.select('.mdc-toolbar__section--align-end')[0].clear()
        #self.mdc_toolbar.select('.mdc-menu-anchor')[0].clear()

        #self.mdc_toolbar.select('.mdc-toolbar__section--align-end')[0] <= icon
        #self.mdc_toolbar.select('.mdc-menu-anchor')[0] <= menu

            ##icon.bind("click", lambda :menu.mdc.toggle())

            ##self.toolbar_elements[label] = icon, menu
