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
        """"""
        self.button_next.bind('click', self.load_next_example)
        self.button_prev.bind('click', self.load_prev_example)
        self.button_run.bind('click', self.load_code)


    #----------------------------------------------------------------------
    def load_next_example(self, evt):
        """"""
        i = self.examples_sort.index(self.current_example)
        i += 1
        if i >= len(self.examples_sort):
            i = 0

        print(self.examples_sort[i])
        self.show_dialog(example=self.examples_sort[i])


    #----------------------------------------------------------------------
    def load_prev_example(self, evt):
        """"""
        i = self.examples_sort.index(self.current_example)
        i -= 1
        if i < 0:
            i = len(self.examples_sort) - 1

        print(self.examples_sort[i])
        self.show_dialog(example=self.examples_sort[i])


    #----------------------------------------------------------------------
    def load_code(self, evt):
        """"""
        code = self.examples[self.current_example]['code']
        #Piton.save_cell(pk=None, code=code)
        self.main.views['Home'].new_cell(code=code)
        self.main.set_view('Home')



########################################################################
class Examples(Events):
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

        #container = Template.DIV()
        container = Template.DIV(style={'background-color': 'white'})

        self.mdc_toolbar = Template.Toolbar(title="Examples", class_="mdc-toolbar--fixed")
        self.mdc_toolbar.select('.mdc-toolbar__menu-icon')[0].bind('click', self.main.mdc_drawer.mdc.open)
        container <= self.mdc_toolbar
        self.examples = Piton.get_examples()

        self.examples_sort = []
        for k in self.examples:

            example = self.examples[k]

            self.examples_sort.append(example['name'])

            img = framework.static('images/thumbnails/{}'.format(example['thumbnail']))
            ul = Template.UL(Class="mdc-list mdc-list--two-line thumbnail_image", style={"border-bottom": "1px solid #cccccc", 'background-image': 'url({})'.format(img),})
            ul.setAttribute('example', example['name'])
            item = Template.ListItemSecondary(example['name'], example['description'])
            ul <= item
            ul.bind('click', self.show_dialog)
            container <= ul




        image = Template.DIV()

        self.dialog_example = Template.Dialog(title="Select file...")
        self.dialog_example.select(".mdc-dialog__footer")[0].html = ''
        self.dialog_example.select(".mdc-dialog__footer")[0].style = {'justify-content': 'space-around'}


        self.button_prev = Template.ButtonIcon('', "keyboard_arrow_left", class_="mdc-dialog__footer__button")
        self.dialog_example.select(".mdc-dialog__footer")[0] <= self.button_prev

        self.button_run = Template.ButtonIcon('', "play_arrow", class_="mdc-dialog__footer__button")
        self.dialog_example.select(".mdc-dialog__footer")[0] <= self.button_run

        self.button_next = Template.ButtonIcon('', "keyboard_arrow_right", class_="mdc-dialog__footer__button")
        self.dialog_example.select(".mdc-dialog__footer")[0] <= self.button_next


        container <= self.dialog_example



        Template.attach()
        return container




    #----------------------------------------------------------------------
    def show_dialog(self, evt=None, example=None):
        """"""

        if not evt is None:
            e = evt.target
            while not "thumbnail_image" in e.class_name:
                e = e.parent

            example = e.getAttribute('example')

        if self.examples[example]['thumbnail']:

            img = framework.static('images/thumbnails/{}'.format(self.examples[example]['thumbnail']))
            style = {
                'background-image': "url({})".format(img),
                     'min-height': "40vh",
                     'background-position': 'center',
                     'background-repeat': 'no-repeat',
                     'background-size': '90%',
                     }

        else:
            style = {
                'background-image': 'none',
                'min-height': "unset",
                #'background-position': 'center',
                #'background-repeat': 'no-repeat',
                     }


        self.dialog_example.select('.mdc-dialog__body')[0].style = style

        self.dialog_example.select('.mdc-dialog__header__title')[0].text = self.examples[example]['name']
        self.dialog_example.select('.mdc-dialog__body')[0].text = self.examples[example]['description']


        self.current_example = example
        self.dialog_example.mdc.show()