#import framework
from browser import window, html, timer
import framework

#from djangoforandroid import Django
#Piton = Django(framework.url("piton_brython"))



from pythoncore import PythonCore
Piton = PythonCore()



########################################################################
class CodeEditor:

    #----------------------------------------------------------------------
    def __init__(self, piton_core, code="", id=None, type='cell'):
        """"""

        self.piton_core = piton_core
        self.type = type

        if id is None:
            if self.type == 'cell':
                self.id = Piton.save_cell()
            elif self.type == 'ide':
                self.id = 'piton_ide'
        else:
            self.id = id

        self.codeblock = html.DIV(Class="codeblock-block mdc-elevation--z2", id="codeblock-block-{}".format(self.id), sort=self.id)
        self.codeblock.setAttribute('editor_id', self.id)

        codeblock_container = html.DIV(Class="codeblock-parent")
        editor_container = html.DIV(Class="mdl-card editor-container editor-container-{}".format(self.id))
        self.codeblock <= codeblock_container
        codeblock_container <= editor_container

        container = html.DIV(Class="container")
        backdrop = html.DIV(Class="backdrop")
        pre = html.PRE(html.CODE(Class="highlights python"), id="pre__code-{}".format(self.id))
        editor_container <= container
        backdrop <= pre
        container <= backdrop

        #Code editor
        #code = "\nx = numpy.linspace(0, 10, 1000)\ny = numpy.sinc(x)\nplot(x,y)"
        self.editor = html.TEXTAREA(code, Class="code-in piton-codeeditor", id="code-{}".format(self.id))
        self.editor.setAttribute('editor_id', self.id)
        self.editor.setAttribute('piton_type', "block")
        container <= self.editor

        self.image_out = html.DIV(Class="image-out")
        editor_container <= self.image_out
        #image-out-placeholder

        #Output
        code_out = html.DIV(Class="code-out")
        code_out <= html.PRE(Class="piton-stdout piton-stdout-{}".format(self.id), style={"display": 'none',})
        editor_container <= code_out


        self.editor.bind('focus', self.set_focus)


        #if self.piton_core.type == 'cell':
        self.save_timer = timer.set_interval(self.save, 1000)


    #----------------------------------------------------------------------
    def set_code(self, code):
        """"""
        self.editor.text = code
        #print('.code-in.piton-codeeditor#code-{}'.format(self.id))
        window.update_textarea('.code-in.piton-codeeditor#code-{}'.format(self.id))


    #----------------------------------------------------------------------
    def set_focus(self, event=None):
        """"""
        framework.select('.codeblock-block.on-focus').removeClass('on-focus')
        framework.select('.codeblock-block#codeblock-block-{}'.format(self.id)).addClass('on-focus')


    #----------------------------------------------------------------------
    def interprete(self):
        """"""
        code = self.editor.value

        self.piton_core.interprete(code, self.id)


    #----------------------------------------------------------------------
    def save(self):
        """"""
        if self.type == 'cell':
            if "on-focus" in self.codeblock.class_name.split():
                code = self.editor.value
                Piton.save_cell(self.id, code)

        elif self.type == 'ide':
            if hasattr(self, 'ide_path'):
                code = self.editor.value
                path = self.ide_path
                Piton.save_ide(path, code)


    #----------------------------------------------------------------------
    def remove(self):
        """"""
        timer.clear_interval(self.save_timer)
        Piton.remove_cell(self.id)
        self.codeblock.remove()
        framework.select('.codeblock-block').last().addClass('on-focus')

