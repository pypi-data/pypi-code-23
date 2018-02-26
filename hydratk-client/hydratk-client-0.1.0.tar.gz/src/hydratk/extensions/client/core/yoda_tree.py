# -*- coding: utf-8 -*-
"""Yoda tree

.. module:: client.core.yoda_tree
   :platform: Windows, Unix
   :synopsis: Yoda tree
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from yaml import safe_load
from yaml.scanner import ScannerError
from yaml.parser import ParserError

from hydratk.extensions.client.core.tkimport import tk, ttk
import hydratk.extensions.client.core.template as tmpl

class YodaTree(tk.LabelFrame):
    """Class YodaTree
    """

    _instance = None
    _instance_created = False

    # references
    _root = None
    _trn = None
    _config = None
    _editor = None
    _logger = None

    # gui elements
    _tree = None
    _vsb = None
    _hsb = None
    _menu = None

    # tests
    _tests = {}
    _current_test = None
    _hidden_tags = []
    _indent = None

    def __init__(self, root):
        """Class constructor

        Called when object is initialized

        Args:
           root (obj): root frame

        Raises:
           error: ValueError

        """

        if (self._instance_created == False):
            raise ValueError('For creating class instance please use the get_instance method instead!')
        if (self._instance is not None):
            raise ValueError('A Class instance already exists, use get_instance method instead!')

        self._root = root
        self._trn = self.root.trn
        self._config = self.root.cfg

        tk.LabelFrame.__init__(self, self.root.pane_left, text=self.trn.msg('htk_gui_yoda_tree_label'))
        self._set_gui()
        self._parse_config()

    @staticmethod
    def get_instance(root=None):
        """Method gets YodaTree singleton instance

        Args:
            root (obj): root frame

        Returns:
            obj

        """

        if (YodaTree._instance is None):
            YodaTree._instance_created = True
            YodaTree._instance = YodaTree(root)

        return YodaTree._instance

    @property
    def root(self):
        """ root property getter """

        return self._root

    @property
    def trn(self):
        """ trn property getter """

        return self._trn

    @property
    def config(self):
        """ config property getter """

        return self._config

    @property
    def editor(self):
        """ editor property getter """

        if (self._editor is None):
            self._editor = self.root.editor

        return self._editor

    @property
    def logger(self):
        """ logger property getter """

        if (self._logger is None):
            self._logger = self.root.logger

        return self._logger

    def _parse_config(self):
        """Method parses configuration

        Args:
            none

        Returns:
            void

        """

        tags = []
        for key in self.config.data['Core']['yodatree']['hidden_tags'].split(','):
            tags.append(key.upper())
        self._hidden_tags = tags

        self._indent = self._config.data['Core']['editor']['format']['indent_yoda']

    def _set_gui(self):
        """Method sets graphical interface

        Args:
            none

        Returns:
            void

        """

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        # treeview
        self._tree = ttk.Treeview(self, columns=('content'), show='tree', displaycolumns=('content'), height=20, selectmode='browse',
                                  xscrollcommand=lambda f, l: self._autoscroll(self._hsb, f, l),
                                  yscrollcommand=lambda f, l: self._autoscroll(self._vsb, f, l))
        self._tree.grid(in_=self, row=0, column=0, sticky=tk.NSEW)

        # scrollbars
        self._vsb = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._tree.yview)
        self._vsb.grid(in_=self, row=0, column=1, sticky=tk.NS)
        self._hsb = ttk.Scrollbar(self, orient=tk.HORIZONTAL, command=self._tree.xview)
        self._hsb.grid(in_=self, row=1, column=0, sticky=tk.EW)

        self._tree['yscroll'] = self._vsb.set
        self._tree['xscroll'] = self._hsb.set
        self._tree.heading('#0', text='Element', anchor='w')
        self._tree.column('#0', stretch=False, width=170)
        self._tree.column('content', stretch=True, minwidth=200, width=100)

        # events
        self._tree.bind('<ButtonRelease-1>', self._highlight_item)
        self._tree.bind('<Any-KeyRelease>', self._highlight_item)
        self._tree.bind('<Button-3>', self._context_menu)

    def _context_menu(self, event=None):
        """Method sets context menu

        Args:
            event (obj): event

        Returns:
            void

        """

        item = self._tree.selection()
        if (len(item) == 0):
            return

        self._set_menu(item)
        self._menu.tk_popup(event.x_root, event.y_root)

    def _autoscroll(self, sbar, idx1, idx2):
        """Method for automatic treeview scroll

        Args:
            sbar (obj): scrollbar
            idx1 (int): start index
            idx2 (int): stop index

        Returns:
            void

        """

        idx1, idx2 = float(idx1), float(idx2)
        if (idx1 <= 0 and idx2 >= 1):
            sbar.grid_remove()
        else:
            sbar.grid()
        sbar.set(idx1, idx2)

    def add_test(self, path, content=None):
        """Method adds new test

        Test and draft file is displayed in tree form

        Args:
            path (str): file path
            content (str): file content

        Returns:
            void

        """
        
        if (path == None):
            self.clear_tree()
            return

        if (path in self._tests):
            content = self._tests[path]['content']
        elif ('.jedi' in path or '.padawan' in path):
            try:
                content = safe_load(content)
                self._tests[path] = {'content': content}
            except (ScannerError, ParserError):
                self.logger.debug(self.trn.msg('htk_core_invalid_yaml', path))
                self._tests[path] = {'content': {}}
        else:
            content = {}
            self._tests[path] = {'content': {}}

        self._populate_tree('', content)
        self._current_test = path

    def get_test(self, path):
        """Method gets test

        Args:
            path (str): file path

        Returns:
            dict

        """

        test = None
        if (path in self._tests):
            test = self._tests[path]

        return test

    def delete_test(self, path):
        """Method deletes test

        Args:
            path (str): file path

        Returns:
            void

        """

        if (path in self._tests):
            del self._tests[path]

    def refresh(self, path, content):
        """Method refreshes tree

        Args:
            path (str): file path
            content (str): file content

        Returns:
            void

        """

        if (path != None and ('.jedi' in path or '.padawan' in path)):
            try:
                content = safe_load(content)
                self._tests[path] = {'content': content}
                self._populate_tree('', content)
            except (ScannerError, ParserError):
                self.logger.debug(self.trn.msg('htk_core_invalid_yaml', path))
                self._tests[path] = {'content': {}}
                self.clear_tree()

    def _populate_tree(self, parent, content):
        """Method populates tree

        Args:
            parent (obj): parent tree node
            content (dict): parsed file

        Returns:
            void

        """

        if (parent == ''):
            self.clear_tree()

        try:
            keys = sorted(content.keys(), key=lambda k: int(k.split('-')[-1]) if ('TEST-' in k.upper()) else 0)
        except (ValueError, AttributeError):
            return

        for key in keys:
            display = self._display_item(key)
            if (display[0]):
                value = content[key]
                node_value = '"{0}"'.format(value) if (display[1]) else ''
                node = self._tree.insert(parent, 'end', text=key, values=(node_value), open=True)
                if (type(value) is dict):
                    self._populate_tree(node, value)

    def clear_tree(self):
        """Method clears tree

        Args:
            none

        Returns:
            void

        """

        self._tree.delete(*self._tree.get_children())

    def _display_item(self, key):
        """Method checks if item can be displayed

        Args:
            key (str): node key

        Returns:
            tuple: display item (bool), display value (bool)

        """

        key = key.upper()
        if ('TEST-' in key):
            key = '-'.join(key.split('-')[:-1])

        # not displayed tags
        item, value = True, True
        for k in self._hidden_tags:
            if (key == k.upper()):        
                item = False
                break

        # tags with not displayed value
        if (item):
            if (key in ['TEST-SCENARIO', 'TEST-CASE', 'TEST-CONDITION', 'TEST', 'VALIDATE',
                        'PRE-REQ', 'POST-REQ', 'EVENTS', 'BEFORE_START', 'AFTER_FINISH']):
                value = False

        return item, value

    def _highlight_item(self, event=None):
        """Method highlights item in editor

        Args:
            event (obj): event

        Returns:
            void

        """
        
        item = self._tree.selection()
        if (len(item) == 0):
            return

        # tree path
        items = [self._tree.item(item)['text']]
        parent = self._tree.parent(item)
        item = self._tree.item(parent)
        while (item['text'] != ''):
            items.append(item['text'])
            parent = self._tree.parent(parent)
            item = self._tree.item(parent)
         
        tab = self.editor.nb.get_current_tab()
        idx = '1.0'
        for item in items[::-1]:
            idx = tab.text.search(r'\y({0})\y\s*:'.format(item), idx, stopindex=tk.END, regexp=True)
            if (not idx):
                break

        if (idx):
            tab.highlight_line(row=idx.split('.')[0])
            tab.update_line_numbers()
            tab.update_info_bar(index=idx)
        else:
            self.clear_tree()

    def _set_menu(self, item):
        """Method sets context menu according to item

        Args:
            item (obj): selected tree item

        Returns:
            void

        """
        
        key = self._tree.item(item)['text']
        self._menu = tk.Menu(self._tree, tearoff=False)
        self._tree.bind('<Button-3>', self._context_menu)
        
        if ('TEST-SCENARIO' in key.upper()):
            tree_path = [key]
            self._menu.add_command(label=self.trn.msg('htk_gui_yoda_tree_menu_add_scenario'), command=lambda: self._add_item('scenario', tree_path))
            self._menu.add_command(label=self.trn.msg('htk_gui_yoda_tree_menu_add_case'), command=lambda: self._add_item('case', tree_path))

            keys = []
            for k in self._tests[self._current_test]['content'][key].keys():
                keys.append(k.upper())

            if ('PRE-REQ' not in keys):
                self._menu.add_command(label=self.trn.msg('htk_gui_yoda_tree_menu_add_prereq'), command=lambda: self._add_item('prereq', tree_path))
            if ('POST-REQ' not in keys):
                self._menu.add_command(label=self.trn.msg('htk_gui_yoda_tree_menu_add_postreq'), command=lambda: self._add_item('postreq', tree_path))
            if ('EVENTS' not in keys):
                self._menu.add_command(label=self.trn.msg('htk_gui_yoda_tree_menu_add_events'), command=lambda: self._add_item('events', tree_path))

        elif ('TEST-CASE' in key.upper()):
            parent = self._tree.parent(item)
            tsc = self._tree.item(parent)['text']
            tree_path = [tsc, key]
            self._menu.add_command(label=self.trn.msg('htk_gui_yoda_tree_menu_add_condition'), command=lambda: self._add_item('condition', tree_path))

            keys = []
            for k in self._tests[self._current_test]['content'][tsc][key].keys():
                keys.append(k.upper())

            if ('EVENTS' not in keys):
                self._menu.add_command(label=self.trn.msg('htk_gui_yoda_tree_menu_add_events'), command=lambda: self._add_item('events', tree_path))
            
        elif ('TEST-CONDITION' in key.upper()):
            parent = self._tree.parent(item)
            tca = self._tree.item(parent)['text']
            tsc = self._tree.item(self._tree.parent(parent))['text']
            tree_path = [tsc, tca, key]

            keys = []
            for k in self._tests[self._current_test]['content'][tsc][tca][key].keys():
                keys.append(k.upper())

            if ('EVENTS' not in keys):
                self._menu.add_command(label=self.trn.msg('htk_gui_yoda_tree_menu_add_events'), command=lambda: self._add_item('events', tree_path))

    def _add_item(self, item, tree_path):
        """Method adds new item from template

        Args:
            item (str): type of item, scenario|case|condition|prereq|postreq|events
            tree_path (list): tree path

        Returns:
            void

        """

        tab = self.editor.nb.get_current_tab()
        idx = self._find_item(tab, tree_path)

        if (item == 'scenario'):
            idx, content = self._prepare_add_scenario(tab, tree_path)
        elif (item == 'case'):
            idx, content = self._prepare_add_case(tab, tree_path, idx)
        elif (item == 'condition'):
            idx, content = self._prepare_add_condition(tab, tree_path, idx)
        elif (item == 'prereq'):
            idx, content = self._prepare_add_prereq(tab, tree_path, idx)
        elif (item == 'postreq'):
            idx, content = self._prepare_add_postreq(tab, tree_path, idx)                
        elif (item == 'events'):
            idx, content = self._prepare_add_events(tab, tree_path, idx)

        tab.text.insert(idx, content)
        tab.text.edit_separator()
        idx = self._find_item(tab, tree_path)
        tab.colorize()
        tab.highlight_line(row=idx.split('.')[0])
        tab.update_line_numbers()
        tab.update_info_bar(index=idx)

    def _find_item(self, tab, tree_path, idx='1.0', stopindex=tk.END, nocase=False):
        """Method finds item in tab

        Args:
            tab (obj): file tab
            tree_path (list): tree path
            idx (str): start index
            stopindex (str): stop index
            nocase (bool): ignore case

        Returns:
            str: item index

        """

        for i in tree_path:
            idx = tab.text.search(r'\y({0})\y\s*:'.format(i), idx, stopindex=stopindex, nocase=nocase, regexp=True)

        return idx

    def _prepare_add_scenario(self, tab, tree_path):
        """Method prepares scenario item

        Args:
            tab (obj): file tab
            tree_path (list): tree path

        Returns:
            tuple: index (str), content (str)

        """

        # calculate new scenario id
        cnt = 0
        for k in self._tests[self._current_test]['content']:
            if ('TEST-SCENARIO' in k.upper()):
                cnt += 1
        id = cnt + 1
        tree_path[0] = 'Test-Scenario-%d' % id

        # calculate index, format content
        idx = tk.END
        content = '\n' + tmpl.scenario.format(tsc_id=id, path=tab.name, tca_id=1, tco_id=1)

        return idx, content

    def _prepare_add_case(self, tab, tree_path, idx):
        """Method prepares case item

        Args:
            tab (obj): file tab
            tree_path (list): tree path
            idx (str): start index

        Returns:
            tuple: index (str), content (str)

        """

        # calculate new case id
        cnt = 0
        for k in self._tests[self._current_test]['content'][tree_path[0]]:
            if ('TEST-CASE' in k.upper()):
                cnt += 1
        id = cnt + 1
        tree_path.append('Test-Case-%d' % id)

        # calculate index, format content
        tsc_id = int(tree_path[0].split('-')[-1])
        tsc_next = self._find_item(tab, ['Test-Scenario-{0}'.format(tsc_id + 1)], idx, nocase=True)
        content = tmpl.case.format(tca_id=id, tco_id=1)

        if (not tsc_next):  # end of file
            idx, content = tk.END, '\n' + content
        else:  # before next scenario
            idx, content = tsc_next, content + '\n'

        return idx, content

    def _prepare_add_condition(self, tab, tree_path, idx):
        """Method prepares condition item

        Args:
            tab (obj): file tab
            tree_path (list): tree path
            idx (str): start index

        Returns:
            tuple: index (str), content (str)

        """

        # calculate new condition id
        cnt = 0
        for k in self._tests[self._current_test]['content'][tree_path[0]][tree_path[1]]:
            if ('TEST-CONDITION' in k.upper()):
                cnt += 1
        id = cnt + 1
        tree_path.append('Test-Condition-%d' % id)

        # calculate index, format content
        tsc_id = int(tree_path[0].split('-')[-1])
        tsc_next = self._find_item(tab, ['Test-Scenario-{0}'.format(tsc_id + 1)], idx, nocase=True)
        stopindex = tk.END if (not tsc_next) else tsc_next
        tca_id = int(tree_path[1].split('-')[-1])
        tca_next = self._find_item(tab, ['Test-Case-{0}'.format(tca_id + 1)], idx, stopindex, nocase=True)
        content = tmpl.condition.format(tco_id=id)

        if (not tca_next):
            if (not tsc_next):  # end of file
                idx, content = tk.END, '\n' + content
            else:  # before next scenario
                idx, content = tsc_next, content + '\n'
        else:  # before next case
            idx, content = tca_next, content[self._indent:] + '\n' + (' ' * self._indent)

        return idx, content

    def _prepare_add_prereq(self, tab, tree_path, idx):
        """Method prepares prereq item

        Args:
            tab (obj): file tab
            tree_path (list): tree path
            idx (str): start index

        Returns:
            tuple: index (str), content (str)

        """

        # calculate index, format content
        tree_path.append('Pre-Req')
        tsc_id = int(tree_path[0].split('-')[-1])
        tsc_next = self._find_item(tab, ['Test-Scenario-{0}'.format(tsc_id + 1)], idx, nocase=True)
        stopindex = tk.END if (not tsc_next) else tsc_next
        tca_next = self._find_item(tab, ['Test-Case-1'], idx, stopindex, nocase=True)
        stopindex = stopindex if (not tca_next) else tca_next
        postreq = self._find_item(tab, ['Post-Req'], idx, stopindex, nocase=True)
        events = self._find_item(tab, ['Events'], idx, stopindex, nocase=True)
        content = tmpl.prereq

        if (not events):
            if (not postreq):
                if (not tca_next):
                    if (not tsc_next):  # end of file
                        idx, content = tk.END, '\n' + content[:-1]
                    else:  # before next scenario
                        idx, content = tsc_next, content
                else:  # before next case
                    idx, content = tca_next, content[self._indent:] + (' ' * self._indent)
            else:  # before postreq
                idx, content = postreq, content[self._indent:] + (' ' * self._indent)
        else:  # before events
            idx, content = events, content[self._indent:] + (' ' * self._indent)

        return idx, content

    def _prepare_add_postreq(self, tab, tree_path, idx):
        """Method prepares postreq item

        Args:
            tab (obj): file tab
            tree_path (list): tree path
            idx (str): start index

        Returns:
            tuple: index (str), content (str)

        """

        # calculate index, format content
        tree_path.append('Post-Req')
        tsc_id = int(tree_path[0].split('-')[-1])
        tsc_next = self._find_item(tab, ['Test-Scenario-{0}'.format(tsc_id + 1)], idx, nocase=True)
        stopindex = tk.END if (not tsc_next) else tsc_next
        tca_next = self._find_item(tab, ['Test-Case-1'], idx, stopindex, nocase=True)
        content = tmpl.postreq

        if (not tca_next):
            if (not tsc_next):  # end of file
                idx, content = tk.END, '\n' + content
            else:  # before next scenario
                idx, content = tsc_next, content + '\n'
        else:  # before next case
            idx, content = tca_next, content[self._indent:] + '\n' + (' ' * self._indent)

        return idx, content

    def _prepare_add_events(self, tab, tree_path, idx):
        """Method prepares events item

        Args:
            tab (obj): file tab
            tree_path (list): tree path
            idx (str): start index

        Returns:
            tuple: index (str), content (str)

        """
        
        # calculate index, format content
        tree_path.append('Events')
        tsc_id = int(tree_path[0].split('-')[-1])
        tsc_next = self._find_item(tab, ['Test-Scenario-{0}'.format(tsc_id + 1)], idx, nocase=True)
        stopindex = tk.END if (not tsc_next) else tsc_next
            
        cnt = len(tree_path)
        if (cnt == 2):  # scenario events
            tca_next = self._find_item(tab, ['Test-Case-1'], idx, stopindex, nocase=True)
            stopindex = stopindex if (not tca_next) else tca_next
            postreq = self._find_item(tab, ['Post-Req'], idx, stopindex, nocase=True)
            content = tmpl.events.format(indent=' ' * self._indent)
                
            if (not postreq):
                if (not tca_next):
                    if (not tsc_next):  # end of file
                        idx, content = tk.END, '\n' + content
                    else:  # before next scenario
                        idx, content = tsc_next, content + '\n'
                else:  # before next case
                    idx, content = tca_next, content[self._indent:] + '\n' + (' ' * self._indent)
            else:  # before postreq
                idx, content = postreq, content[self._indent:] + '\n' + (' ' * self._indent)
                    
        elif (cnt == 3):  # case events
            tca_id = int(tree_path[1].split('-')[-1])
            tca_next = self._find_item(tab, ['Test-Case-{0}'.format(tca_id + 1)], idx, stopindex, nocase=True)
            stopindex = stopindex if (not tca_next) else tca_next
            tco_next = self._find_item(tab, ['Test-Condition-1'], idx, stopindex, nocase=True)
            content = tmpl.events.format(indent=' ' * self._indent * 2)
                
            if (not tco_next):
                if (not tca_next):
                    if (not tsc_next):  # end of file
                        idx, content = tk.END, '\n' + content
                    else:  # before next scenario
                        idx, content = tsc_next, content + '\n'
                else:  # before next case
                    idx, content = tca_next, content[self._indent:] + '\n'
            else:  # before next condition
                idx, content = tco_next, content[self._indent * 2:] + '\n' + (' ' * self._indent * 2)
                    
        elif (cnt == 4):  # condition events
            tca_id = int(tree_path[1].split('-')[-1])
            tca_next = self._find_item(tab, ['Test-Case-{0}'.format(tca_id + 1)], idx, stopindex, nocase=True)
            stopindex = stopindex if (not tca_next) else tca_next
            tco_id = int(tree_path[2].split('-')[-1])
            tco_next = self._find_item(tab, ['Test-Condition-{0}'.format(tco_id + 1)], idx, stopindex, nocase=True)
            stopindex = stopindex if (not tco_next) else tco_next
            test = self._find_item(tab, ['Test'], idx, stopindex, nocase=True)
            validate = self._find_item(tab, ['Validate'], idx, stopindex, nocase=True)
            content = tmpl.events.format(indent=' ' * self._indent * 3)

            if (not test):
                if (not validate):
                    if (not tco_next):
                        if (not tca_next):
                            if (not tsc_next):  # end of file
                                idx, content = tk.END, '\n' + content
                            else:  # before next scenario
                                idx, content = tsc_next, content + '\n'
                        else:  # before next case
                            idx, content = tca_next, content[self._indent:] + '\n' + (' ' * self._indent)
                    else:  # before next condition
                        idx, content = tco_next, content[self._indent * 2:] + '\n' + (' ' * self._indent * 2)
                else:  # before validate
                    idx, content = validate, content[self._indent * 3:] + '\n' + (' ' * self._indent * 3)
            else:  # before test
                idx, content = test, content[self._indent * 3:] + '\n' + (' ' * self._indent * 3)        

        return idx, content
