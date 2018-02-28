# -*- coding: utf-8 -*-

"""
This class allows to set some common handlers and methods for
easy view declaration"""

import wx
import wx.aui
from beatle import model, tran, localpath
from beatle.lib import wxx
from beatle.app.ui import dlg
from beatle.activity.models.ui import dlg as mdlg
from beatle.ctx import localcontext as context
from beatle.lib.handlers import Identifiers
from beatle.app.ui.tools import edit

class BaseView(object):
    """Declares a base view class"""

    _saveWorkspace = Identifiers.register("ID_SAVE_WORKSPACE")
    _closeWorkspace = Identifiers.register("ID_CLOSE_WORKSPACE")
    _closeProject = Identifiers.register("ID_CLOSE_PROJECT")
    _saveProject = Identifiers.register("ID_SAVE_PROJECT")
    _editProperties = Identifiers.register("ID_EDIT_PROPERTIES")
    _editDelete = Identifiers.register("ID_DELETE")
    _newProject = Identifiers.register("ID_NEW_PROJECT")
    _openProject = Identifiers.register("ID_OPEN_PROJECT")
    _importProject = Identifiers.register("ID_IMPORT_PROJECT")
    _editCopy = Identifiers.register("ID_COPY")
    _editCut = Identifiers.register("ID_CUT")
    _editPaste = Identifiers.register("ID_PASTE")

    # class variables defines installed handlers
    workspace_handler = True
    project_handler = True
    clipboard_handler = True
    build_handler = False
    run_handler = False
    debug_handler = False

    # command ids: tree
    _leftKeyId = wx.Window.NewControlId()

    #command ids: build
    _buildProjectId = wx.Window.NewControlId()

    #command ids: run
    _runProjectId = wx.Window.NewControlId()
    _runFileId = wx.Window.NewControlId()
    _stopRunId = wx.Window.NewControlId()
    _addPathToConsoleId = wx.Window.NewControlId()

    #command ids: debug
    _toggleBreakpointId = wx.Window.NewControlId()
    _debugProjectId = wx.Window.NewControlId()
    _debugFileId = wx.Window.NewControlId()
    _debugContinueId = wx.Window.NewControlId()
    _debugStepOverId = wx.Window.NewControlId()
    _debugStepIntoId = wx.Window.NewControlId()
    _debugStepOutId = wx.Window.NewControlId()
    _debugStopId = wx.Window.NewControlId()

    #update_context : these properties will be used for update menus
    @property
    def can_edit_properties(self):
        """Are the properties of the selected element editable?"""
        if self.selected and not self.selected.read_only:
            return True
        return False

    def __init__(self, *args, **kwargs):
        """Initialize base view"""
        self._evtHandler = wx.PyEvtHandler()
        self._handler_installed = False
        self._registered_menus = {}
        self._registered_toolbars = []
        self._perspective_base = None
        self.selected = None
        super(BaseView, self).__init__(*args, **kwargs)

    def _create_menus(self):
        """Create the base view menus"""
        if self.project_handler:
            self._menuProject = wx.Menu()
            if self.build_handler:
                self._submenuBuild = wx.Menu()
                self._buildProject = wx.MenuItem(self._submenuBuild, self._buildProjectId, u"Project",
                    u"build project", wx.ITEM_NORMAL)
                self._buildProject.SetBitmap(wx.Bitmap(localpath("app/res/build.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuBuild.AppendItem(self._buildProject)
                self._menuProject.AppendSubMenu(self._submenuBuild, u"Build")
            if self.run_handler:
                self._submenuRun = wx.Menu()
                # run project
                self._runProject = wx.MenuItem(self._submenuRun, self._runProjectId, u"Project",
                    u"run project", wx.ITEM_NORMAL)
                self._runProject.SetBitmap(wx.Bitmap(localpath("app/res/run.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuRun.AppendItem(self._runProject)
                # run file
                self._runFile = wx.MenuItem(self._submenuRun, self._runFileId, u"File",
                    u"run current file", wx.ITEM_NORMAL)
                self._runFile.SetBitmap(wx.Bitmap(localpath("app/res/run_file.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuRun.AppendItem(self._runFile)
                # stop run
                self._stopRun = wx.MenuItem(self._submenuRun, self._stopRunId, u"Stop",
                    u"stop project", wx.ITEM_NORMAL)
                self._stopRun.SetBitmap(wx.Bitmap(localpath("app/res/stop.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuRun.AppendItem(self._stopRun)

                self._menuProject.AppendSubMenu(self._submenuRun, u"Run")

            if self.debug_handler:
                self._submenuDebug = wx.Menu()
                # breakpoint
                self._toggleBreakpoint = wx.MenuItem(self._submenuDebug, self._toggleBreakpointId, u"Breakpoint\tF9",
                    u"toggle breakpoint", wx.ITEM_CHECK)
                #self._toggleBreakpoint.SetBitmap(wx.Bitmap(u"res/breakpoint.xpm", wx.BITMAP_TYPE_ANY))
                self._submenuDebug.AppendItem(self._toggleBreakpoint)

                self._submenuDebug.AppendSeparator()
                # debug project
                self._debugProject = wx.MenuItem(self._submenuDebug, self._debugProjectId, u"Project",
                    u"debug project", wx.ITEM_NORMAL)
                self._debugProject.SetBitmap(wx.Bitmap(localpath("app/res/debug.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuDebug.AppendItem(self._debugProject)
                # debug file
                self._debugFile = wx.MenuItem(self._submenuDebug, self._debugFileId, u"File",
                    u"debug file", wx.ITEM_NORMAL)
                self._debugFile.SetBitmap(wx.Bitmap(localpath("app/res/debug_file.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuDebug.AppendItem(self._debugFile)
                # debug continue
                self._debugContinue = wx.MenuItem(self._submenuDebug, self._debugContinueId,
                    u"Continue\tF5", u"continue", wx.ITEM_NORMAL)
                self._debugContinue.SetBitmap(wx.Bitmap(localpath("app/res/continue.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuDebug.AppendItem(self._debugContinue)
                # debug step over
                self._debugStepOver = wx.MenuItem(self._submenuDebug, self._debugStepOverId,
                    u"Step over\tF6", u"step over", wx.ITEM_NORMAL)
                self._debugStepOver.SetBitmap(wx.Bitmap(localpath("app/res/step_over.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuDebug.AppendItem(self._debugStepOver)
                # debug step into
                self._debugStepInto = wx.MenuItem(self._submenuDebug, self._debugStepIntoId,
                    u"Step into\tF7", u"step into", wx.ITEM_NORMAL)
                self._debugStepInto.SetBitmap(wx.Bitmap(localpath("app/res/step_into.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuDebug.AppendItem(self._debugStepInto)
                # debug step out
                self._debugStepOut = wx.MenuItem(self._submenuDebug, self._debugStepOutId,
                    u"Step out\tF8", u"step out", wx.ITEM_NORMAL)
                self._debugStepOut.SetBitmap(wx.Bitmap(localpath("app/res/step_out.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuDebug.AppendItem(self._debugStepOut)
                # debug stop
                self._debugStop = wx.MenuItem(self._submenuDebug, self._debugStopId, u"Stop",
                    u"stop debug", wx.ITEM_NORMAL)
                self._debugStop.SetBitmap(wx.Bitmap(localpath("app/res/stop.xpm"), wx.BITMAP_TYPE_ANY))
                self._submenuDebug.AppendItem(self._debugStop)

                self._menuProject.AppendSubMenu(self._submenuDebug, u"Debug")

            self._addPathToConsole = wx.MenuItem(self._menuProject, self._addPathToConsoleId, u"Add path to console",
                    u"add the project path to console", wx.ITEM_NORMAL)
            self._menuProject.AppendItem(self._addPathToConsole)

            self.RegisterMenu('Project', self._menuProject)

    def RegisterMenu(self, name, menu):
        """Appends a dynamic menu to the view, This menu will be
        shown only when the view becomes active"""
        self._registered_menus[name] = menu

    def RegisterToolbar(self, toolbar):
        """Appends a dynamic toolbar to the view, This toolbar will be
        shown only when the view becomes active"""
        self._registered_toolbars.append(toolbar)

    def BindSpecial(self, evtID, handler, source=None, id=-1, id2=-1):
        """Do a special binding for pluggable event handler and also internal event handler"""
        self._evtHandler.Bind(evtID, handler, source=source, id=id, id2=id2)
        self.Bind(evtID, handler, source=source, id=id, id2=id2)

    def _delete_toolbars(self):
        """Destroy associated toolbard"""
        while len(self._registered_toolbars):
            self._registered_toolbars.pop().Destroy()

    def _create_toolbars(self):
        """Create the associated toolbars"""
        # common elements
        if self.run_handler:
            self._barRun = wx.aui.AuiToolBar(self.frame, wx.ID_ANY, wx.DefaultPosition,
                wx.DefaultSize, wx.aui.AUI_TB_GRIPPER | wx.aui.AUI_TB_HORZ_LAYOUT)

            els = [self._runFile, self._runProject, self._stopRun]
            bar = self._barRun
            bar.SetMinSize(wx.Size(24, 24))
            for el in els:
                bar.AddTool(el.GetId(), el.GetLabel(), el.GetBitmap())
            bar.Realize()
            name = "run_toolbar_{0}".format(self.__class__)
            self.frame.m_mgr.AddPane(bar, wx.aui.AuiPaneInfo().Name(name).Top().Hide().
                Caption(u"run").PinButton(True).Gripper().Dock().Resizable().
                DockFixed(False).Row(1).Position(0).Layer(10).ToolbarPane())
            self.RegisterToolbar(bar)

        if self.debug_handler:
            self._barDebug = wx.aui.AuiToolBar(self.frame, wx.ID_ANY, wx.DefaultPosition,
                wx.DefaultSize, wx.aui.AUI_TB_GRIPPER | wx.aui.AUI_TB_HORZ_LAYOUT)

            els = [self._debugFile, self._debugProject, self._debugContinue,
                self._debugStepInto, self._debugStepOver, self._debugStepOut,
                self._debugStop]
            bar = self._barDebug
            bar.SetMinSize(wx.Size(24, 24))
            for el in els:
                bar.AddTool(el.GetId(), el.GetLabel(), el.GetBitmap())
            bar.AddSeparator()
            bar.AddTool(self._toggleBreakpointId,
                "breakpoint",
                wx.Bitmap(localpath("app/res/breakpoint.xpm"), wx.BITMAP_TYPE_ANY),
                "toggle breakpoint", wx.ITEM_CHECK
                )
            bar.Realize()
            name = "debug_toolbar_{0}".format(self.__class__)
            self.frame.m_mgr.AddPane(bar, wx.aui.AuiPaneInfo().Name(name).Top().Hide().
                Caption(u"debug").PinButton(True).Gripper().Dock().Resizable().
                DockFixed(False).Row(1).Position(1).Layer(10).ToolbarPane())
            self.RegisterToolbar(bar)

    def _bind_events(self):
        """Connect common handlers"""
        if self.workspace_handler:
            self.BindSpecial(wx.EVT_MENU, self.OnSaveWorkspace, id=self._saveWorkspace)
            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateSaveWorkspace, id=self._saveWorkspace)
            self.BindSpecial(wx.EVT_MENU, self.OnCloseWorkspace, id=self._closeWorkspace)
            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateCloseWorkspace, id=self._closeWorkspace)
            self.BindSpecial(wx.EVT_MENU, self.OnCloseProject, id=self._closeProject)
            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateCloseProject, id=self._closeProject)

        if self.build_handler:
            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateBuildProject, id=self._buildProjectId)
            self.BindSpecial(wx.EVT_MENU, self.OnBuildProject, id=self._buildProjectId)

        if self.project_handler:
            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateSaveProject, id=self._saveProject)
            self.BindSpecial(wx.EVT_MENU, self.OnSaveProject, id=self._saveProject)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateAddPathToConsole, id=self._addPathToConsoleId)
            self.BindSpecial(wx.EVT_MENU, self.OnAddPathToConsole, id=self._addPathToConsoleId)

        if self.run_handler:
            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateRunProject, id=self._runProjectId)
            self.BindSpecial(wx.EVT_MENU, self.OnRunProject, id=self._runProjectId)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateRunFile, id=self._runFileId)
            self.BindSpecial(wx.EVT_MENU, self.OnRunFile, id=self._runFileId)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateStopRun, id=self._stopRunId)
            self.BindSpecial(wx.EVT_MENU, self.OnStopRun, id=self._stopRunId)

        if self.debug_handler:
            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateToggleBreakpoint, id=self._toggleBreakpointId)
            self.BindSpecial(wx.EVT_MENU, self.OnToggleBreakpoint, id=self._toggleBreakpointId)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateDebugProject, id=self._debugProjectId)
            self.BindSpecial(wx.EVT_MENU, self.OnDebugProject, id=self._debugProjectId)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateDebugFile, id=self._debugFileId)
            self.BindSpecial(wx.EVT_MENU, self.OnDebugFile, id=self._debugFileId)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateDebugContinue, id=self._debugContinueId)
            self.BindSpecial(wx.EVT_MENU, self.OnDebugContinue, id=self._debugContinueId)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateDebugStepOver, id=self._debugStepOverId)
            self.BindSpecial(wx.EVT_MENU, self.OnDebugStepOver, id=self._debugStepOverId)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateDebugStepInto, id=self._debugStepIntoId)
            self.BindSpecial(wx.EVT_MENU, self.OnDebugStepInto, id=self._debugStepIntoId)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateDebugStepOut, id=self._debugStepOutId)
            self.BindSpecial(wx.EVT_MENU, self.OnDebugStepOut, id=self._debugStepOutId)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateDebugStop, id=self._debugStopId)
            self.BindSpecial(wx.EVT_MENU, self.OnDebugStop, id=self._debugStopId)

        self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateEditProperties, id=self._editProperties)
        self.BindSpecial(wx.EVT_MENU, self.OnEditProperties, id=self._editProperties)

        self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateDelete, id=self._editDelete)
        self.BindSpecial(wx.EVT_MENU, self.OnDelete, id=self._editDelete)

        self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateNewProject, id=self._newProject)
        self.BindSpecial(wx.EVT_MENU, self.OnNewProject, id=self._newProject)

        self.BindSpecial(wx.EVT_MENU, self.OnOpenProject, id=self._openProject)
        self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateOpenProject, id=self._openProject)

        self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateImportProject, id=self._importProject)
        self.BindSpecial(wx.EVT_MENU, self.OnImportProject, id=self._importProject)

        self.BindSpecial(wx.EVT_MENU, self.OnShowViewToolbars, id=context.frame.m_view_showToolbars.GetId())

        # if the view has transactional behavior, activate edit handlers
        if self.clipboard_handler:
            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateEditCopy, id=self._editCopy)
            self.BindSpecial(wx.EVT_MENU, self.OnEditCopy, id=self._editCopy)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateEditCut, id=self._editCut)
            self.BindSpecial(wx.EVT_MENU, self.OnEditCut, id=self._editCut)

            self.BindSpecial(wx.EVT_UPDATE_UI, self.OnUpdateEditPaste, id=self._editPaste)
            self.BindSpecial(wx.EVT_MENU, self.OnEditPaste, id=self._editPaste)

        self.BindSpecial(wx.EVT_MENU, self.frame.OnMRUFile, None, wx.ID_FILE1, wx.ID_FILE9)

        # bind special navigation facility
        self.Bind(wx.EVT_MENU, self.TreeLeftKey, id=BaseView._leftKeyId)

    #default handlers
    def OnUpdateRunProject(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateRunFile(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateStopRun(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateToggleBreakpoint(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateDebugProject(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateDebugFile(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateDebugContinue(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateDebugStepOver(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateDebugStepInto(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateDebugStepOut(self, event):
        """default event handler"""
        event.Enable(False)

    def OnUpdateDebugStop(self, event):
        """default event handler"""
        event.Enable(False)

    def OnRunProject(self, event):
        """default event handler"""
        pass

    def OnRunFile(self, event):
        """default event handler"""
        pass

    def OnStopRun(self, event):
        """default event handler"""
        pass

    def OnDebugProject(self, event):
        """default event handler"""
        pass

    def OnToggleBreakpoint(self, event):
        """default event handler"""
        pass

    def OnDebugFile(self, event):
        """default event handler"""
        pass

    def OnDebugContinue(self, event):
        """default event handler"""
        pass

    def OnDebugStepOver(self, event):
        """default event handler"""
        pass

    def OnDebugStepInto(self, event):
        """default event handler"""
        pass

    def OnDebugStepOut(self, event):
        """default event handler"""
        pass

    def OnDebugStop(self, event):
        """default event handler"""
        pass

    def OnUpdateEditProperties(self, event):
        """Handle update edit properties"""
        event.Enable(self.can_edit_properties)

    def OnEditProperties(self, event):
        """Handle edit properties method"""
        edit(context.frame, self.selected)

    def OnUpdateSaveWorkspace(self, event):
        """Handle update save project"""
        event.Enable(bool(self.selected and self.selected.workspace))

    def OnSaveWorkspace(self, event):
        """Handle save project"""
        wrk = self.selected and self.selected.workspace
        if wrk is None:
            return
        context.app.SaveWorkspace(wrk)

    def OnUpdateCloseWorkspace(self, event):
        """Handle update close workspace"""
        event.Enable(bool(self.selected and self.selected.workspace))

    @tran.TransactionalMethod('close workspace')
    def OnCloseWorkspace(self, event):
        """Handle save project"""
        wrk = self.selected and self.selected.workspace
        if wrk is None:
            return
        tran.TransactionStack.DoUnload(wrk)
        return True

    def OnUpdateCloseProject(self, event):
        """Handle update close workspace"""
        event.Enable(bool(self.selected and self.selected.project))

    @tran.TransactionalMethod('close project')
    def OnCloseProject(self, event):
        """Handle save project"""
        prj = self.selected and self.selected.project
        if prj is None:
            return
        tran.TransactionStack.DoUnload(prj)
        return True

    def OnUpdateBuildProject(self, event):
        """Update build project"""
        s = self.selected
        event.Enable(bool(s and s.project and s.project.buildable))

    def OnBuildProject(self, event):
        """Update build project"""
        pass

    def OnUpdateSaveProject(self, event):
        """Update save project method"""
        event.Enable(bool(self.selected and self.selected.project))

    def OnSaveProject(self, event):
        """Handle save project"""
        obj = self.selected
        project = obj.project
        if project is None:
            return
        context.app.SaveProject(project)

    def OnUpdateAddPathToConsole(self, event):
        """Update save project method"""
        event.Enable(False)

    def OnAddPathToConsole(self, event):
        """Update save project method"""
        pass

    def OnUpdateNewProject(self, event):
        """Update add project"""
        obj = self.selected
        if obj is None:
            return
        event.Enable(bool(obj and obj.inner_project_container))

    @tran.TransactionalMethod('new project {0}')
    @wxx.CreationDialog(mdlg.ProjectDialog, model.Project)
    def OnNewProject(self, event):
        """Handle new project command"""
        return (context.frame,
            self.selected and self.selected.inner_project_container)

    def OnUpdateOpenProject(self, event):
        """Handle update edit properties"""
        event.Enable(bool(self.selected and self.selected.inner_project_container))

    @tran.TransactionalMethod('open project')
    def OnOpenProject(self, event):
        """Handle open project method"""
        path = wx.EmptyString
        v = self.selected
        if v:
            workspace = v.workspace
            if workspace:
                path = workspace._dir
        else:
            workspace = None
        dialog = wx.FileDialog(self, "Select project file", path,
            wx.EmptyString, "Project files (*.pcc)|*.pcc", wx.FD_OPEN)
        if dialog.ShowModal() != wx.ID_OK:
            return None
        fname = dialog.GetPath()
        project = context.app.LoadProject(fname, workspace)
        if project:
            tran.TransactionStack.DoLoad(project)
            if not workspace:
                mru = context.mru
                mru.AddFileToHistory(fname)
            project.SetModified(False)
            # check classes
            for cls in project.classes:
                if cls.errorCheckDerivatives():
                    project.SetModified(True)
        return project


    def OnUpdateImportProject(self, event):
        """Update import procjec"""
        obj = self.selected
        event.Enable(bool(obj and obj.workspace))

    @tran.TransactionalMethod('import project')
    def OnImportProject(self, event):
        """Handle import project event"""
        dialog = dlg.ImportProjectDialog(context.frame, self.selected.workspace)
        if dialog.ShowModal() == wx.ID_OK:
            # create modeless dialog
            progress = dlg.WaitDialog(context.frame)
            progress.InitDialog()
            progress.Show(True)
            progress.Centre()
            progress.Refresh()
            progress.Update()
            v = dialog.DoImport(progress)
            progress.Close()
            return v
        return False

    def install_handler(self):
        """Installs the event handler"""
        if self._handler_installed:
            return False  # already installed
        context.frame.PushEventHandler(self._evtHandler)
        self._handler_installed = True
        return True  # ok, installed

    def remove_handler(self):
        """Remove the event handler"""
        if not self._handler_installed:
            return False  # already removed
        # pop event handlers until found this
        other_event_handlers = []
        evth = context.frame.PopEventHandler()
        try:
            while evth != self._evtHandler:
                other_event_handlers.append(evth)
                evth = context.frame.PopEventHandler()
            if evth == self._evtHandler:
                self._handler_installed = False
            result = True
        except:
            print "Fatal error : missing event handler"
            self._handler_installed = False
            result = False
        # reinstall the event handlers chain
        while len(other_event_handlers):
            context.frame.PushEventHandler(other_event_handlers.pop())
        return result

    def NotifyShow(self):
        """Called where the git view is show"""
        if not self.install_handler():
            return  # avoid extra calls
        for menu in self._registered_menus:
            self.frame.AddMainMenu(menu, self._registered_menus[menu])
        if self._perspective_base is None:
            # if there is not a base perspective, we create one
            for toolbar in self._registered_toolbars:
                context.frame.m_mgr.GetPane(toolbar).Show()
                toolbar.Realize()
            self._perspective_base = context.frame.m_mgr.SavePerspective()
        cls = type(self)
        if cls.perspective:
            context.frame.m_mgr.LoadPerspective(cls.perspective)
            context.frame.m_mgr.Update()
        context.frame.LoadViewsPerspective()
        context.frame.m_mgr.Update()
        wx.YieldIfNeeded()
        self.SetFocus()

    def NotifyHide(self):
        """Called where the git view is hidden"""
        if not self.remove_handler():
            return  # avoid extra calls
        # store current perspective for later use
        cls = type(self)
        cls.perspective = context.frame.m_mgr.SavePerspective()
        context.frame.SaveViewsPerspective()
        for menu in self._registered_menus:
            self.frame.RemoveMainMenu(menu, self._registered_menus[menu])
        changes = False
        for toolbar in self._registered_toolbars:
            context.frame.m_mgr.GetPane(toolbar).Hide()
            toolbar.Realize()
            changes = True
        if changes:
            context.frame.m_mgr.Update()
            wx.YieldIfNeeded()

    def OnShowViewToolbars(self, event):
        """Show all the view toolbars"""
        context.frame.m_mgr.LoadPerspective(self._perspective_base)


