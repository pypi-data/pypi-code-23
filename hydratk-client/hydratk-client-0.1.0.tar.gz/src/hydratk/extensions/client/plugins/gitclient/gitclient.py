# -*- coding: utf-8 -*-
"""Git client plugin

.. module:: client.plugins.gitclient
   :platform: Windows, Unix
   :synopsis: Git client
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

from hydratk.extensions.client.core import plugin
from hydratk.extensions.client.core.tkimport import tk, ttk, tkfd
from hydratk.extensions.client.core.utils import fix_path

try:
    from git import Repo
except ImportError:
    pass
    
from shutil import rmtree
import os

class Plugin(plugin.Plugin):
    """Class Plugin
    """

    # gui elements
    _win = None
    _pane = None
    _frame_left = None
    _frame_right = None

    _tree = None
    _menu = None
    _vbar = None

    _url = None
    _user = None
    _passw = None
    _name = None
    _email = None

    _msg = None
    _author = None
    _files = None
    _files_bar = None

    def _init_plugin(self):
        """Method initializes plugin

        Args:
           none

        Returns:
           void

        """

        self._plugin_id = 'gitclient'
        self._plugin_name = 'GitClient'
        self._plugin_version = '0.1.0'
        self._plugin_author = 'Petr Rašek <bowman@hydratk.org>, HydraTK team <team@hydratk.org>'
        self._plugin_year = '2017 - 2018'

    def _setup(self):
        """Method executes plugin setup

        Args:
           none

        Returns:
           void

        """

        try:
            import git
            self._set_menu('gitclient', 'htk_gitclient_menu', 'plugin')
            self._set_menu_item('gitclient', 'htk_gitclient_menu_clone', self._win_clone)
            self._set_menu_item('gitclient', 'htk_gitclient_menu_repomanager', self._win_repomanager)

        except ImportError:
            self.logger.error('Plugin {0} could not be loaded, git executable is not installed.'.format(self._plugin_name))

    def _win_clone(self):
        """Method displays clone window

        Args:
           none

        Returns:
           void

        """

        win = tk.Toplevel(self.root)
        win.title(self.trn.msg('htk_gitclient_clone_title'))
        win.transient(self.root)
        win.resizable(False, False)
        win.geometry('+%d+%d' % (self.root.winfo_screenwidth() / 3, self.root.winfo_screenheight() / 3))
        win.tk.call('wm', 'iconphoto', win._w, self.root.images['logo'])

        tk.Label(win, text=self.trn.msg('htk_gitclient_clone_url')).grid(row=0, column=0, sticky='e')
        url = tk.Entry(win, width=70)
        url.grid(row=0, column=1, padx=3, pady=10, sticky='e')
        url.focus_set()

        tk.Label(win, text=self.trn.msg('htk_gitclient_clone_user')).grid(row=1, column=0, sticky='e')
        user = tk.Entry(win, width=20)
        user.grid(row=1, column=1, padx=3, pady=3, sticky='w')

        tk.Label(win, text=self.trn.msg('htk_gitclient_clone_password')).grid(row=2, column=0, sticky='e')
        passw = tk.Entry(win, width=20)
        passw.grid(row=2, column=1, padx=3, pady=3, sticky='w')

        tk.Label(win, text=self.trn.msg('htk_gitclient_clone_dirpath')).grid(row=3, column=0, sticky='e')
        dirpath = tk.Entry(win, width=70)
        dirpath.grid(row=3, column=1, padx=3, pady=3, sticky='w')
        tk.Button(win, text='...', command=lambda: self._set_dirpath(dirpath)).grid(row=3, column=2, sticky='w')

        error = tk.Label(win, text='', foreground='#FF0000')
        error.grid(row=4, column=1, sticky='w')
        btn = tk.Button(win, text=self.trn.msg('htk_gitclient_clone_button'),
                        command=lambda: self._clone_repo(url.get(), dirpath.get(), user.get(), passw.get(), error, win))
        btn.grid(row=4, column=2, padx=3, pady=3, sticky='e')

        win.bind('<Escape>', lambda f: win.destroy())

    def _win_repomanager(self):
        """Method displays repository manager window

        Args:
           none

        Returns:
           void

        """

        self._win = tk.Toplevel(self.root)
        self._win.title(self.trn.msg('htk_gitclient_repomanager_title'))
        self._win.transient(self.root)
        self._win.resizable(False, False)
        self._win.geometry('+%d+%d' % (self.root.winfo_screenwidth() / 5, self.root.winfo_screenheight() / 10))
        self._win.tk.call('wm', 'iconphoto', self._win._w, self.root.images['logo'])

        self._pane = tk.PanedWindow(self._win, orient=tk.HORIZONTAL)
        self._pane.pack(expand=True, fill=tk.BOTH)

        # left frame
        self._frame_left = tk.Frame(self._pane)
        self._set_tree()
        self._pane.add(self._frame_left)

        # right frame
        self._frame_right = tk.Frame(self._pane)
        self._set_config()
        self._set_commit()
        self._pane.add(self._frame_right)

        self._win.bind('<Escape>', lambda f: self._win.destroy())

    def _set_tree(self):
        """Method sets tree gui

        Args:
           none

        Returns:
           void

        """

        self._vbar = ttk.Scrollbar(self._frame_left, orient=tk.VERTICAL)
        self._tree = ttk.Treeview(self._frame_left, columns=(), show='tree', displaycolumns=(), height=10, selectmode='browse',
                                  yscrollcommand=self._vbar.set)
        self._vbar.config(command=self._tree.yview)
        self._vbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        for name, cfg in self.explorer._projects.items():
            if ('git' in cfg):
                self._tree.insert('', 'end', text=name)

        # context menu
        self._menu = tk.Menu(self._tree, tearoff=False)
        self._menu.add_command(label=self.trn.msg('htk_gitclient_repomanager_push'), command=self._push)
        self._menu.add_command(label=self.trn.msg('htk_gitclient_repomanager_pull'), command=self._pull)

        # events
        self._tree.bind('<ButtonRelease-1>', self._fill_repo_detail)
        self._tree.bind('<Any-KeyRelease>', self._fill_repo_detail)
        self._tree.bind('<Button-3>', self._context_menu)

    def _context_menu(self, event=None):
        """Method sets context menu

        Args:
            event (obj): event

        Returns:
            void

        """

        self._menu.tk_popup(event.x_root, event.y_root)

    def _set_config(self):
        """Method sets configuration gui

        Args:
           none

        Returns:
           void

        """

        row = 0
        font = ('Arial', 10, 'bold')
        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_config_title'), font=font).grid(row=row, column=0, sticky='w')
        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_config_url')).grid(row=row + 1, column=0, sticky='e')
        self._url = tk.Entry(self._frame_right, width=70)
        self._url.grid(row=row + 1, column=1, padx=3, pady=3, sticky='w')

        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_config_user')).grid(row=row + 2, column=0, sticky='e')
        self._user = tk.Entry(self._frame_right, width=20)
        self._user.grid(row=row + 2, column=1, padx=3, pady=3, sticky='w')

        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_config_password')).grid(row=row + 3, column=0, sticky='e')
        self._passw = tk.Entry(self._frame_right, width=20)
        self._passw.grid(row=row + 3, column=1, padx=3, pady=3, sticky='w')

        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_config_name')).grid(row=row + 4, column=0, sticky='e')
        self._name = tk.Entry(self._frame_right, width=40)
        self._name.grid(row=row + 4, column=1, padx=3, pady=3, sticky='w')

        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_config_email')).grid(row=row + 5, column=0, sticky='e')
        self._email = tk.Entry(self._frame_right, width=40)
        self._email.grid(row=row + 5, column=1, padx=3, pady=3, sticky='w')

        error = tk.Label(self._frame_right, text='', foreground='#FF0000')
        error.grid(row=row + 6, column=1, sticky='w')
        btn = tk.Button(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_config_save'),
                        command=lambda: self._save_config(self._url.get(), self._user.get(), self._passw.get(), self._name.get(), self._email.get(), error))
        btn.grid(row=row + 6, column=2, padx=3, pady=3, sticky='e')

    def _set_commit(self):
        """Method sets commit gui

        Args:
           none

        Returns:
           void

        """

        row = 7
        font = ('Arial', 10, 'bold')
        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_commit_title'), font=font).grid(row=row, column=0, sticky='w')

        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_commit_message')).grid(row=row + 1, column=0, sticky='e')
        self._msg = tk.Text(self._frame_right, background='#FFFFFF', height=7, width=50)
        self._msg.grid(row=row + 1, column=1, rowspan=2, sticky='w')
        row += 1

        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_commit_author')).grid(row=row + 3, column=0, sticky='e')
        self._author = tk.Entry(self._frame_right, width=40)
        self._author.grid(row=row + 3, column=1, padx=3, pady=3, sticky='w')

        push = tk.BooleanVar(value=True)
        tk.Checkbutton(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_commit_push'), variable=push).grid(row=row + 3, column=2, sticky='e')

        error = tk.Label(self._frame_right, text='', foreground='#FF0000')
        error.grid(row=row + 4, column=1, sticky='w')
        btn = tk.Button(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_commit_commit'),
                        command=lambda: self._commit(self._msg.get('1.0', 'end-1c'), self._author.get(), [], push.get(), error))
        btn.grid(row=row + 4, column=2, padx=3, pady=3, sticky='e')

        tk.Label(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_commit_files'), font=font).grid(row=row + 5, column=0, sticky='w')

        select_all = tk.BooleanVar(value=False)
        tk.Checkbutton(self._frame_right, text=self.trn.msg('htk_gitclient_repomanager_commit_select_all'), variable=select_all, 
                       command=lambda: self._select_all_files(select_all.get())).grid(row=row + 6, column=1, sticky='w')

        self._files_bar = ttk.Scrollbar(self._frame_right, orient=tk.VERTICAL)
        self._files = ttk.Treeview(self._frame_right, columns=('operation', 'file'), show='tree', displaycolumns=('operation', 'file'), height=10, selectmode='browse',
                                   yscrollcommand=self._files_bar.set)
        self._files_bar.configure(command=self._files.yview)
        self._files.grid(row=row + 7, column=1, sticky=tk.NSEW)
        self._files_bar.grid(row=row + 7, column=2, sticky='nsw')

        self._files.column('#0', stretch=False, width=40)
        self._files.column('operation', stretch=False, width=50)
        self._files.column('file', stretch=True, width=200)

        self._files.bind('<ButtonRelease-1>', self._select_file)
        self._files.bind('<Any-KeyRelease>', self._select_file)

    def _set_dirpath(self, entry):
        """Method sets dirpath

        Args:
           entry (obj): entry reference

        Returns:
           void

        """

        entry.delete(0, tk.END)
        entry.insert(tk.END, tkfd.askdirectory())

    def _clone_repo(self, url, dirpath, user='', passw='', error=None, win=None):
        """Method clones repository

        Args:
           url (str): repository url
           dirpath (str): directory path
           user (str): username
           pass (str): password
           error (obj): error label reference
           win (obj): window reference

        Returns:
           void

        """

        if (error is not None):
            error.config(text='')
            proj_name = dirpath.split('/')[-1]
            if (len(url) == 0):
                error.config(text=self.trn.msg('htk_gitclient_mandatory_field', self.trn.msg('htk_gitclient_clone_url')))
                return
            elif (len(dirpath) == 0):
                error.config(text=self.trn.msg('htk_gitclient_mandatory_field', self.trn.msg('htk_gitclient_clone_dirpath')))
                return
            elif (proj_name in self.explorer._projects):
                error.config(text=self.trn.msg('htk_gitclient_clone_project_exist', proj_name))
                return

        repo = None
        try:
            if (win is not None):
                win.destroy()

            url_auth = self._prepare_url(url, user, passw)
            self.logger.info(self.trn.msg('htk_gitclient_clone_start', url))
            repo = Repo.clone_from(url_auth, dirpath)
            self.logger.info(self.trn.msg('htk_gitclient_clone_finish'))
            self._create_project(url, dirpath, user, passw)
        except Exception as ex:
            self.logger.error(ex)
            if (os.path.exists(dirpath)):
                rmtree(dirpath)
        finally:
            if (repo is not None):
                repo.close()

    def _create_project(self, url, dirpath, user, passw):
        """Method creates project from repository

        Args:
           url (str): repository url
           dirpath (str): directory path
           user (str): username
           pass (str): password

        Returns:
           void

        """

        dirpath = fix_path(dirpath)
        proj_name = dirpath.split('/')[-1]
        self.explorer._projects[proj_name] = {'path': dirpath, 'pythonpath': [dirpath + '/lib/yodalib', dirpath + '/helpers/yodahelpers'],
                                              'git': {'url': url, 'username': user, 'password': passw, 'name': '', 'email': ''}}
        node = self.explorer._tree.insert('', 'end', text=proj_name, values=(dirpath, 'directory'))
        self.explorer._populate_tree(node)
        self.logger.info(self.trn.msg('htk_core_project_created', proj_name))
        self.config.data['Projects'] = self.explorer._projects
        self.explorer.autocompleter.update_pythonpath()
        self.config.save()

    def _fill_repo_detail(self, event=None):
        """Method fills repository detail

        Args:
            event (obj): event

        Returns:
            void

        """

        item = self._tree.selection()
        if (len(item) == 0):
            return

        project = self._tree.item(item)['text']
        cfg = self.config.data['Projects'][project]
        repo_path = cfg['path']
        cfg = cfg['git']

        self._url.delete(0, tk.END)
        self._url.insert(tk.END, cfg['url'])
        self._user.delete(0, tk.END)
        self._user.insert(tk.END, cfg['username'])
        self._passw.delete(0, tk.END)
        self._passw.insert(tk.END, cfg['password'])
        self._name.delete(0, tk.END)
        self._name.insert(tk.END, cfg['name'])
        self._email.delete(0, tk.END)
        self._email.insert(tk.END, cfg['email'])

        self._author.delete(0, tk.END)
        author = '{0} <{1}>'.format(cfg['name'], cfg['email']) if (cfg['email'] != '') else ''
        self._author.insert(tk.END, author)
        self._msg.delete('1.0', 'end')

        self._fill_changed_files(repo_path)

    def _save_config(self, url, user='', passw='', name='', email='', error=None):
        """Method saves configuration

        Args:
           url (str): repository url
           user (str): username
           passw (str): password
           name (str): author name
           email (str): author email
           error (obj): error label reference

        Returns:
           void

        """

        item = self._tree.selection()
        if (len(item) == 0):
            return

        if (error is not None):
            error.config(text='')
            if (len(url) == 0):
                error.config(text=self.trn.msg('htk_gitclient_mandatory_field', self.trn.msg('htk_gitclient_repomanager_config_url')))
                return

        project = self._tree.item(item)['text']
        repo_path = self.config.data['Projects'][project]['path']
        cfg = self.config.data['Projects'][project]['git']

        repo = None
        try:
            if ([cfg['url'], cfg['username'], cfg['password'], cfg['name'], cfg['email']] != [url, user, passw, name, email]):
                repo = Repo(repo_path)
                repo.git.remote('set-url', 'origin', self._prepare_url(url, user, passw))
                repo.git.config('user.name', name)
                repo.git.config('user.email', email)

                cfg['url'] = url
                cfg['username'] = user
                cfg['password'] = passw
                cfg['name'] = name
                cfg['email'] = email
                self.config.save()
                self.logger.debug(self.trn.msg('htk_gitclient_repomanager_config_saved', project))

        except Exception as ex:
            self.logger.error(ex)
        finally:
            if (repo is not None):
                repo.close() 

    def _commit(self, msg, author, files, push=False, error=None):
        """Method performs commit to local repository

        Args:
           msg (str): commit message
           author (str): author
           files (list): files to commit
           push (bool): push commit to remote repository
           error (obj): error label reference

        Returns:
           void

        """

        item = self._tree.selection()
        if (len(item) == 0):
            return

        if (error is not None):
            error.config(text='')
            if (len(msg) == 0):
                error.config(text=self.trn.msg('htk_gitclient_mandatory_field', self.trn.msg('htk_gitclient_repomanager_commit_message')))
                return
            elif (len(author) == 0):
                error.config(text=self.trn.msg('htk_gitclient_mandatory_field', self.trn.msg('htk_gitclient_repomanager_commit_author')))
                return

        cnt, files = 0, []
        for i in self._files.get_children():
            item = self._files.item(i)
            if (item['text'] != ''):
                cnt += 1
                files.append(item['values'][1])

        if (error is not None and cnt == 0):
            error.config(text=self.trn.msg('htk_gitclient_repomanager_commit_no_files_selected'))
            return

        repo = None
        try:
            project = self._tree.item(self._tree.selection())['text']
            repo_path = self.config.data['Projects'][project]['path']
            repo = Repo(repo_path)
            repo.git.add('--all', files)
            repo.git.commit(message=msg, author=author)
            self.logger.info(self.trn.msg('htk_gitclient_repomanager_commit_finish', project))

            if (push):
                self._push()

        except Exception as ex:
            self.logger.error(ex)
        finally:
            if (repo is not None):
                repo.close()

    def _push(self, event=None):
        """Method performs push to remote repository

        Args:
           event (obj): event

        Returns:
           void

        """

        item = self._tree.selection()
        if (len(item) == 0):
            return

        repo = None
        try:
            project = self._tree.item(item)['text']
            repo_path = self.config.data['Projects'][project]['path']
            self.logger.info(self.trn.msg('htk_gitclient_repomanager_push_start', project))

            repo = Repo(repo_path)
            repo.git.push('origin')
            self.logger.info(self.trn.msg('htk_gitclient_repomanager_push_finish'))

        except Exception as ex:
            self.logger.error(ex)
        finally:
            if (repo is not None):
                repo.close()

    def _pull(self, event=None):
        """Method performs pull from remote repository

        Args:
           event (obj): event

        Returns:
           void

        """

        item = self._tree.selection()
        if (len(item) == 0):
            return

        repo = None
        try:
            project = self._tree.item(item)['text']
            repo_path = self.config.data['Projects'][project]['path']
            self.logger.info(self.trn.msg('htk_gitclient_repomanager_pull_start', project))

            repo = Repo(repo_path)
            repo.git.pull('origin')
            self.explorer.refresh(path=repo_path)
            self.logger.info(self.trn.msg('htk_gitclient_repomanager_pull_finish'))

        except Exception as ex:
            self.logger.error(ex)
        finally:
            if (repo is not None):
                repo.close()

    def _fill_changed_files(self, repo_path):
        """Method fills changed

        Args:
           repo_path (str): repository path

        Returns:
           void

        """

        self._files.delete(*self._files.get_children())
        changes = self._get_changed_files(repo_path)
        
        for operation, files in changes.items():
            for f in files:
                self._files.insert('', 'end', text='', values=(operation, f))

    def _get_changed_files(self, repo_path):
        """Method gets changed files available for commit

        Args:
           repo_path (str): repository path

        Returns:
           dict

        """

        repo, files = None, []
        try:
            repo = Repo(repo_path)
            status = repo.git.status('--porcelain')

            added, modified, deleted = [], [], []
            for rec in status.splitlines():
                operation, fname = rec[:2], rec[3:]
                if ('?' in operation):
                    added.append(fname)
                elif ('M' in operation):
                    modified.append(fname)
                elif ('D' in operation):
                    deleted.append(fname)

            files = {
                     'add'    : added,
                     'modify' : modified,
                     'delete' : deleted
                    }

        except Exception as ex:
            self.logger.error(ex)
        finally:
            if (repo is not None):
                repo.close()

        return files

    def _select_file(self, event=None):
        """Method selects or deselects file for commit

        Args:
           event (obj): event

        Returns:
           void

        """

        sel = self._files.selection()
        if (len(sel) == 0):
            return

        item = self._files.item(sel)
        self._files.item(sel, text='X' if item['text'] == '' else '')
        
    def _select_all_files(self, value):
        """Method selects or deselects all files for commit

        Args:
           value (bool): requested value

        Returns:
           void

        """

        value = 'X' if (value) else ''
        for i in self._files.get_children():
            self._files.item(i, text=value)

    def _prepare_url(self, url, user=None, passw=None):
        """Method prepares url with authentication

        Args:
           url (str): repository URL
           user (str): username
           passw (str): password

        Returns:
           str

        """

        if (len(user) > 0 and '://' in url):
            url = url.replace('://', '://{0}:{1}@'.format(user, passw))

        return url
