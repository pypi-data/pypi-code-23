from browser import document, window
import framework
from browser.html import DIV, PRE, UL, LI
#from mdc import MDC, Build, Components
#from mdc import MDCBuild
from mdcframework import Template

#from base import Base
#from static.brython.scripts import Events
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

        self.button_fab.bind('click', self.interprete)
        self.launch_explorer.bind('click', lambda evt:self.dialog_explorer.mdc.show())

        self.button_open_file.bind('click', self.open_file)
        self.button_open_file_start.bind('click', lambda evt:self.dialog_explorer.mdc.show())


        self.button_cancel_file.bind('click', lambda evt:self.dialog_file.mdc.close())
        self.button_create_file.bind('click', self.create_new_file)

        self.button_new_file.bind('click', lambda evt: self.dialog_file.mdc.show())


        #framework.select('a.mdc-list-item').on('click', self.click_item)



    #----------------------------------------------------------------------
    def click_item(self, event):
        """"""
        framework.select('li.mdc-list-item').css('background-color', 'unset')
        framework.select('li.mdc-list-item').css('color', 'unset')
        framework.select('li.mdc-list-item').removeClass('current-selected')

        event.target.style = {'background-color': '#57c8ec', 'color': 'white',}
        event.target.class_name = ' '.join(event.target.class_name.split() + ["current-selected"])

        li = document.select('.current-selected')[0]

        root = li.getAttribute('root')
        filename = li.getAttribute('filename')

        if not filename:
            self.button_open_file.setAttribute('disabled', True)
        else:
            self.button_open_file.removeAttribute('disabled')


    #----------------------------------------------------------------------
    def interprete(self, event):
        """"""
        self.code_editor.interprete()


    #----------------------------------------------------------------------
    def open_file(self, event):
        """"""
        li = document.select('.current-selected')[0]

        root = li.getAttribute('root')
        filename = li.getAttribute('filename')

        if filename.endswith(".py"):
            self.load_path(root, filename)
            #code = Piton.read(root, filename)
            #self.dialog_explorer.mdc.close()
            #self.code_editor.set_code(code)
            #self.code_editor.ide_path = (root, filename)
            #self.current_file = filename

            #self.mdc_toolbar.mdc.set_title(html="IDE - <small>[{}]</small>".format(filename))
            #self.piton_container.style = {'display':'block'}
            #self.button_open_file_start_parent.style = {"display": 'none',}

        #window.update_all()


    #----------------------------------------------------------------------
    def load_path(self, root, filename):
        """"""
        code = Piton.read(root, filename)
        self.dialog_explorer.mdc.close()
        self.code_editor.set_code(code)
        self.code_editor.ide_path = (root, filename)
        self.current_file = filename

        self.mdc_toolbar.mdc.set_title(html="IDE - <small>[{}]</small>".format(filename))
        self.piton_container.style = {'display':'block'}
        self.button_open_file_start_parent.style = {"display": 'none',}

        window.update_all()



    #----------------------------------------------------------------------
    def create_new_file(self, event):
        """"""
        li = document.select('.current-selected')[0]
        root = li.getAttribute('root')
        filename = self.new_file_input.select('input')[0].value

        filename = filename.strip()

        if not filename.endswith(".py"):
            filename += '.py'

        Piton.new_file(root, filename)
        self.load_path(root, filename)

        self.dialog_file.mdc.close()

        self.dialog_explorer.select('.mdc-dialog__body')[0].clear()
        self.dialog_explorer.select('.mdc-dialog__body')[0] <= self.files()




########################################################################
class Ide(Events):
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
        self.dialog_explorer.select('.mdc-dialog__body')[0].clear()
        self.dialog_explorer.select('.mdc-dialog__body')[0] <= self.files()

        if self.current_file is None:
            self.dialog_explorer.mdc.show()

        return self.container





    #----------------------------------------------------------------------
    def build(self):
        """"""

        container = Template.DIV()

        self.current_file = None



        self.mdc_toolbar = Template.Toolbar(title="IDE", class_="mdc-toolbar--fixed")
        self.mdc_toolbar.select('.mdc-toolbar__menu-icon')[0].bind('click', self.main.mdc_drawer.mdc.open)
        container <= self.mdc_toolbar


        self.dialog_explorer = Template.Dialog(title="Files", body_class="mdc-dialog__body--scrollable")
        self.dialog_explorer.select('.mdc-dialog__body')[0] <= self.files()
        self.dialog_explorer.select('.mdc-dialog__body')[0].style = {'max-height': "50vh"}

        self.dialog_explorer.select(".mdc-dialog__footer")[0].html = ''


        self.button_new_file = Template.Button("New File...", class_="mdc-dialog__footer__button mdc-theme--secondary")
        self.dialog_explorer.select(".mdc-dialog__footer")[0] <= self.button_new_file

        self.button_open_file = Template.Button("Open", class_="mdc-dialog__footer__button")
        self.button_open_file.setAttribute('disabled', True)
        self.dialog_explorer.select(".mdc-dialog__footer")[0] <= self.button_open_file


        container <= self.dialog_explorer


        self.dialog_file = Template.Dialog(title="Create new file")

        self.new_file_input = Template.TextField(style={'width': '100%', })

        self.dialog_file.select('.mdc-dialog__body')[0] <= self.new_file_input

        self.dialog_file.select(".mdc-dialog__footer")[0].html = ''

        self.button_cancel_file = Template.Button("Cancel", class_="mdc-dialog__footer__button")
        self.dialog_file.select(".mdc-dialog__footer")[0] <= self.button_cancel_file

        self.button_create_file = Template.Button("Create", class_="mdc-dialog__footer__button")
        self.dialog_file.select(".mdc-dialog__footer")[0] <= self.button_create_file

        container <= self.dialog_file



        self.launch_explorer = Template.Icon(icon="folder_open", class_="mdc-toolbar__icon")
        #self.main.mdc_toolbar.select('.mdc-toolbar__section--align-end')[0] <= self.launch_explorer
        #self.mdc_toolbar('.mdc-menu-anchor') <= self.menu()

        self.mdc_toolbar.select('.mdc-toolbar__section--align-end')[0] <= self.launch_explorer
        #self.mdc_toolbar.select('.mdc-menu-anchor')[0] <= self.menu

        #self.main.set_toolbar_menu(self.launch_explorer)

        self.button_fab = Template.ButtonFab('bug_report', class_="piton-float_button")
        container <= self.button_fab

        self.piton_container = Template.DIV(Class="piton-container")
        self.piton_container.style = {'position': "absolute"}
        container <= self.piton_container

        #self.piton_core = self.main.('ide')

        self.code_editor = CodeEditor(self.main.piton_core, "", None, 'ide')


        line_number = Template.DIV(Class="piton_numberline", id=self.code_editor.id)
        line_number <= Template.PRE()

        numberline_editor = Template.DIV(Class="numberline")


        numberline_editor <= line_number
        numberline_editor <= self.code_editor.codeblock

        self.piton_container <= numberline_editor


        self.piton_container.style = {'display':'none'}


        self.button_open_file_start_parent = DIV(style={"width": "100vw", 'text-align': 'center',})
        self.button_open_file_start = Template.Button("Open file...", class_="mdc-button--raised")
        self.button_open_file_start.style = {'top': '30vh',}

        self.button_open_file_start_parent <= self.button_open_file_start
        container <= self.button_open_file_start_parent


        self.code_editor.codeblock.class_name += " on-focus"

        Template.attach()


        return container



    #----------------------------------------------------------------------
    def files(self):
        """"""

        tree = Piton.path()
        margin = 30
        items = []

        ul = UL(Class="mdc-list")

        for index, dirname, files, root in tree:

            folder = Template.ListItem(text=dirname, icon='subdirectory_arrow_right folder', href="#", attr={'root': root, 'filename':''})
            folder.style = {'padding-left': "{}px".format(margin*index), "height": '38px',}
            folder.select('.material-icons')[0].style = {'margin-right': '30px', 'color': '#d2d2d2', 'letter-spacing': "-5px"}
            #ul <= folder
            items.append(folder)

            for filename in files:
                file = Template.ListItem(text=filename, icon='subdirectory_arrow_right insert_drive_file', href="#", attr={'root': root, 'filename':filename})
                file.style = {'padding-left': "{}px".format(margin*(index+1)), "height": '38px',}
                file.select('.material-icons')[0].style = {'margin-right': '30px', 'color': '#d2d2d2', 'letter-spacing': "-5px"}

                #ul <= file
                items.append(file)

        #[ul.__le__(item) for item in items]
        for item in items:
            ul <= item
            item.bind('click', self.click_item)

        return ul




##----------------------------------------------------------------------
#def main():
    #""""""
    #Ide()






##main()