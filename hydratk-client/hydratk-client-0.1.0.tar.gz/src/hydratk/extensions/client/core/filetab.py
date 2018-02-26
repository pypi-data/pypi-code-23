# -*- coding: utf-8 -*-
"""FileTab

.. module:: client.core.filetab
   :platform: Windows
   :synopsis: FileTab, Unix
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from hydratk.extensions.client.core.tkimport import tk, ttk, c_os
from hydratk.extensions.client.core.colorizer import Colorizer
from hydratk.extensions.client.core.formatter import Formatter
from hydratk.extensions.client.core.autocompleter import AutoCompleter

class FileTab(tk.Frame):
    """Class FileTab
    """

    # references
    _nb = None
    _editor = None
    _colorizer = None
    _formatter = None
    _autocompleter = None

    # tab parameters
    _name = None
    _path = None
    _last_find_str = ''
    _disable_format = False

    # gui elements
    _text = None
    _ln_bar = None
    _info_bar = None
    _vbar = None
    _hbar = None
    _menu = None

    def __init__(self, nb, name, path=None, content=None):
        """Class constructor

        Called when object is initialized

        Args:
           nb (obj): notebook reference
           name (str): file name
           path (str): file path
           content (str): file content

        """

        self._nb = nb
        self._editor = self.nb.editor
        self._colorizer = Colorizer.get_instance()
        self._formatter = Formatter.get_instance()
        self._autocompleter = AutoCompleter.get_instance()

        tk.Frame.__init__(self)
        self._name = name
        self._path = path
        self._set_gui(content)

    @property
    def nb(self):
        """ nb property getter """

        return self._nb

    @property
    def editor(self):
        """ editor property getter """

        return self._editor

    @property
    def colorizer(self):
        """ colorizer property getter """

        return self._colorizer

    @property
    def formatter(self):
        """ formatter property getter """

        return self._formatter

    @property
    def autocompleter(self):
        """ autocompleter property getter """

        return self._autocompleter

    @property
    def text(self):
        """ text property getter """

        return self._text

    @property
    def name(self):
        """ name property getter """

        return self._name

    @property
    def path(self):
        """ path property getter """

        return self._path

    def _set_gui(self, content=None):
        """Method sets graphical interface

        Args:
            content (str): file content

        Returns:
            void

        """

        self.rowconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        self._vbar = ttk.Scrollbar(self, orient=tk.VERTICAL)
        self._hbar = ttk.Scrollbar(self, orient=tk.HORIZONTAL)

        # line number bar
        self._ln_bar = tk.Text(self, background='#FFFFFF', width=5, padx=3, takefocus=0, state=tk.DISABLED, yscrollcommand=self._vbar.set)
        self._ln_bar.grid(in_=self, row=0, column=0, sticky=tk.NSEW)

        # text area
        self._text = tk.Text(self, wrap=tk.NONE, background='#FFFFFF', xscrollcommand=self._hbar.set, yscrollcommand=self._vbar.set)
        self.set_font(self.editor.font['family'], self.editor.font['size'], self.editor.font['style'])
        self._text.grid(in_=self, row=0, column=1, sticky=tk.NSEW)

        # scrollbars
        self._vbar.configure(command=self._text.yview)
        self._vbar.grid(in_=self, row=0, column=2, sticky=tk.NS)
        self._hbar.configure(command=self._text.xview)
        self._hbar.grid(in_=self, row=1, column=1, sticky=tk.EW)

        # info bar
        info_text = '1 : 1' if (self.editor.var_show_info_bar.get()) else ''
        self._info_bar = tk.Label(self._text, text=info_text)
        self._info_bar.pack(side=tk.RIGHT, anchor=tk.SE)

        self._text.focus_set()

        # initial text content
        if (content != None):
            self._text.insert(tk.END, content)
            self._text.edit_modified(False)
            self._text.mark_set(tk.INSERT, 1.0)
            self.update_line_numbers()
            self.update_info_bar()
            self.colorize()

        # events
        self._text.configure(undo=True)
        self._text.bind('<Control-v>', self.editor.paste)
        self._text.bind('<Control-F4>', self.nb.close_tab)
        self._text.bind('<Any-KeyPress>', self._on_key_press)
        self._text.bind('<Any-KeyRelease>', self._on_key_release)
        self._text.bind('<ButtonRelease-1>', self._on_mouse_click)
        self._vbar.configure(command=self._on_vsb)

        if (c_os == 'Windows'):
            self._ln_bar.bind('<MouseWheel>', self._on_mouse_wheel)
            self._text.bind('<MouseWheel>', self._on_mouse_wheel)
            self._text.bind('<Control-MouseWheel>', self._change_font_size)
        else:
            self._ln_bar.bind('<Button-4>', self._on_mouse_wheel)
            self._ln_bar.bind('<Button-5>', self._on_mouse_wheel)
            self._text.bind('<Button-4>', self._on_mouse_wheel)
            self._text.bind('<Button-5>', self._on_mouse_wheel)
            self._text.bind('<Control-Button-4>', self._change_font_size)
            self._text.bind('<Control-Button-5>', self._change_font_size)

        self._text.bind('<F3>', self.find)
        self._text.bind('<Control-z>', self.editor.undo)
        self._text.bind('<Control-y>', self.editor.redo)
        self._text.bind('<Control-space>', self._show_autocomplete)

        self._set_menu()

    def _set_menu(self):
        """Method sets menu

        Args:
            none

        Returns:
            void

        """

        self._menu = tk.Menu(self._text, tearoff=False)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_undo'), accelerator='Ctrl+Z', command=self.editor.undo)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_redo'), accelerator='Ctrl+Y', command=self.editor.redo)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_cut'), accelerator='Ctrl+X', command=self.editor.cut)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_copy'), accelerator='Ctrl+C', command=self.editor.copy)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_paste'), accelerator='Ctrl+V', command=self.editor.paste)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_delete'), accelerator='Delete', command=self.editor.delete)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_select_all'), accelerator='Ctrl+A', command=self.editor.select_all)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_goto'), accelerator='Ctrl+G', command=self.editor.win_goto)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_find'), accelerator='Ctrl+F', command=self.editor.win_find)
        self._menu.add_command(label=self.editor.trn.msg('htk_gui_editor_menu_replace'), accelerator='Ctrl+R', command=self.editor.win_replace)

        self._text.bind('<Button-3>', self._context_menu)

    def _context_menu(self, event=None):
        """Method sets context menu

        Args:
            event (obj): event

        Returns:
            void

        """

        self._menu.tk_popup(event.x_root, event.y_root)

    def set_font(self, family, size, style):
        """Method sets font

        Args:
            family (str): font family
            size (int): font size
            style (str): font style

        Returns:
            void

        """

        self._text.configure(font=(family, size, style))
        self._ln_bar.configure(font=(family, size, style))

    def _get_line_numbers(self):
        """Method calculates line numbers for current tab

        Args:
            none

        Returns:
            str

        """

        output = ''
        row, col = self._text.index('end').split('.')
        i = 0
        for i in range(1, int(row) - 1):
            output += str(i) + '\n'

        return output + str(i + 1)

    def update_line_numbers(self, event=None):
        """Method updates line numbers bar after event

        Args:
            event (obj): event

        Returns:
            void

        """

        if (self.editor.var_show_line_number.get()):
            line_numbers = self._get_line_numbers()
            self._ln_bar.config(state=tk.NORMAL)
            self._ln_bar.delete('1.0', 'end')
            self._ln_bar.insert('1.0', line_numbers)
            self._ln_bar.yview_moveto(self._text.yview()[0])
            self._ln_bar.config(state=tk.DISABLED)
        else:
            self._ln_bar.config(state=tk.NORMAL)
            self._ln_bar.delete('1.0', 'end')
            self._ln_bar.config(state=tk.DISABLED)

    def update_info_bar(self, event=None, index=None):
        """Method updates info bar after event

        Args:
            event (obj): event
            index (str): index

        Returns:
            void

        """

        if (self.editor.var_show_info_bar.get()):
            row, col = self._text.index(tk.INSERT).split('.') if (index == None) else index.split('.')
            row, col = str(int(row)), str(int(col) + 1)
            self._info_bar.config(text='{0} : {1}'.format(row, col))
        else:
            self._info_bar.config(text='')

    def highlight_line(self, event=None, row=None):
        """Method highlights current line

        Args:
            event (obj): event
            row (str): row

        Returns:
            void

        """

        if (event != None):
            row, col = self._text.index(tk.INSERT).split('.')

        self._text.tag_remove('highlight', 1.0, 'end')
        self._text.tag_add('highlight', row + '.0', row + '.150')
        self._text.tag_configure('highlight', background='#AFEEEE')
        self._text.see(row + '.0')

    def _on_key_press(self, event=None):
        """Method handles key press

        Args:
            event (obj): event

        Returns:
            void

        """

        self.update_line_numbers(event)
        self.update_info_bar(event)
        self.highlight_line(event)

    def _on_key_release(self, event=None):
        """Method handles key release

        Args:
            event (obj): event

        Returns:
            void

        """

        self.update_line_numbers(event)
        self.update_info_bar(event)
        self.highlight_line(event)

        # recolorize
        if (event.keysym not in ['Up', 'Down']):
            row = self._text.index(tk.INSERT).split('.')[0]
            self.colorize('{0}.0'.format(int(row)), '{0}.0'.format(int(row) + 1))

        # remove highlight
        self._text.tag_remove('match', 1.0, tk.END)

        # format text
        self._format_text(event)

        # refresh yoda tree
        if (event.keysym == 'BackSpace'):
            self.editor.refresh_yoda_tree(self)

    def _on_mouse_click(self, event=None):
        """Method handles mouse click event

        Args:
            event (obj): event

        Returns:
            void

        """

        self.update_info_bar(event)
        self.highlight_line(event)
        self.text.tag_remove('match', 1.0, tk.END)

    def _on_vsb(self, *args):
        """Method handles scrollbar event

        Args:
            args (list): arguments

        Returns:
            void

        """

        self._ln_bar.yview(*args)
        self._text.yview(*args)

    def _on_mouse_wheel(self, event=None):
        """Method handles mouse wheel event

        Args:
            event (obj): event

        Returns:
            void

        """

        if (c_os == 'Windows'):
            self._ln_bar.yview_scroll(-1 * (event.delta / 120), 'units')
            self._text.yview_scroll(-1 * (event.delta / 120), 'units')
        else:
            unit = 0
            if (event.num == 4):
                unit = -1
            elif (event.num == 5):
                unit = 1
            self._ln_bar.yview_scroll(unit, 'units')
            self._text.yview_scroll(unit, 'units')

        return 'break'

    def _change_font_size(self, event=None):
        """Method changes font size

        Args:
            event (obj): event

        Returns:
            void

        """

        if (c_os == 'Windows'):
            if (event.delta > 0):
                self.editor.increase_font()
            else:
                self.editor.decrease_font()
        else:
            if (event.num == 4):
                self.editor.increase_font()
            else:
                self.editor.decrease_font()

    def goto(self, line):
        """Method goes to given line

        Args:
            line (int): line number

        Returns:
            void

        """

        self._text.mark_set(tk.INSERT, '%s.1' % line)
        self.highlight_line(line)
        self.update_info_bar()
        self.update_line_numbers()

    def find(self, event=None, find_str=None, find_all=False, ignore_case=False, regexp=False):
        """Method finds given string and highlights it

        Args:
            event (obj): event
            find_str (str): string to find
            find_all (bool): find all occurrences, otherwise only next one
            ignore_case (bool): ignore case
            regexp (bool): regular expression

        Returns:
            void

        """

        if (event != None):
            if (len(self._last_find_str) > 0):
                find_str = self._last_find_str
            else:
                return

        self._text.tag_remove('match', 1.0, tk.END)
        first_match = True

        if (find_all):
            idx1 = 1.0
        else:
            row, col = self._text.index(tk.INSERT).split('.')
            idx1 = '{0}.{1}'.format(row, int(col) + 1)

        if (regexp):
            find_str = r'{0}'.format(find_str)

        while True:
            idx1 = self._text.search(find_str, idx1, stopindex=tk.END, nocase=ignore_case, regexp=regexp)
            if (not idx1):
                if (event != None):
                    idx1 = self._text.search(find_str, 1.0, stopindex=tk.END, nocase=ignore_case)
                    if (not idx1):
                        break
                else:
                    break
            idx2 = '{0}+{1}c'.format(idx1, len(find_str))
            self._text.tag_add('match', idx1, idx2)

            if (first_match):
                self._last_find_str = find_str
                self._text.mark_set(tk.INSERT, idx1)
                self._text.see(tk.INSERT)
                first_match = False
                if (not find_all):
                    break

            idx1 = idx2
        self._text.tag_config('match', foreground='#FF0000', background='#FFFF00')

    def replace(self, find_str, replace_str, replace_all, ignore_case, regexp):
        """Method finds given string and replaces it

        Args:
            find_str (str): string to find
            replace_str (str): string to replace
            replace_all (bool): replace all occurrences, otherwise only next one
            ignore_case (bool): ignore case
            regexp (bool): regular expression

        Returns:
            void

        """

        self._text.tag_remove('match', 1.0, tk.END)
        first_match = True

        if (replace_all):
            idx1 = 1.0
        else:
            row, col = self._text.index(tk.INSERT).split('.')
            idx1 = '{0}.{1}'.format(row, int(col) + 1)

        if (regexp):
            find_str = r'{0}'.format(find_str)

        while True:
            idx1 = self._text.search(find_str, idx1, stopindex=tk.END, nocase=ignore_case, regexp=regexp)
            if (not idx1):
                break

            idx2 = '{0}+{1}c'.format(idx1, len(find_str))
            self._text.delete(idx1, idx2)
            self._text.insert(idx1, replace_str)
            idx2 = '{0}+{1}c'.format(idx1, len(replace_str))
            self._text.tag_add('match', idx1, idx2)

            if (first_match):
                self._last_find_str = replace_str
                self._text.mark_set(tk.INSERT, idx1)
                self._text.see(tk.INSERT)
                first_match = False
                if (not replace_all):
                    break

            idx1 = idx2
        self._text.tag_config('match', foreground='red', background='yellow')

    def colorize(self, start='1.0', stop='end'):
        """Method colorizes text

        Args:
            start (str): start index
            stop (str): stop index

        Returns:
            void

        """

        yoda_found = self.colorizer.colorize(self._text, start, stop)
        if (yoda_found):
            self.editor.refresh_yoda_tree(self)

    def _format_text(self, event=None):
        """Method formats text

        Args:
            event (obj): event

        Returns:
            void

        """

        if (not self._disable_format):
            self.formatter.format_text(event, self._text)
        else:
            self._disable_format = False

    def _show_autocomplete(self, event=None):
        """Method shows code autocomplete

        Args:
            event (obj): event

        Returns:
            void

        """      
        
        self.autocompleter.show_completion(self)

    def disable_format(self):
        """Method disables automatic format

        Args:
            none

        Returns:
            void

        """

        self._disable_format = True
