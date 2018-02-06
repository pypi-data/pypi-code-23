"""
Import Sounds
-----------

A widget for import sounds 'into' canvas session from a local file system
"""
import enum
import fnmatch
import itertools
import logging
import os
import sys
import traceback
import warnings
from collections import namedtuple
from types import SimpleNamespace as namespace

import Orange.data
import numpy
from AnyQt.QtCore import Qt, QEvent, QFileInfo, QThread
from AnyQt.QtCore import pyqtSlot as Slot
from AnyQt.QtGui import QStandardItem, QImageReader, QDropEvent
from AnyQt.QtWidgets import (
    QAction, QPushButton, QComboBox, QApplication, QStyle, QFileDialog,
    QFileIconProvider, QStackedWidget, QProgressBar, QWidget, QHBoxLayout,
    QVBoxLayout, QLabel
)
from Orange.canvas.preview.previewbrowser import TextLabel
from Orange.widgets import widget, gui, settings
from Orange.widgets.utils.concurrent import (
    ThreadExecutor, FutureWatcher, methodinvoke
)
from Orange.widgets.utils.filedialogs import RecentPath
from scipy.io.wavfile import read


def prettyfypath(path):
    home = os.path.expanduser("~/")
    if path.startswith(home):  # case sensitivity!
        path = os.path.join("~", os.path.relpath(path, home))
    return path


log = logging.getLogger(__name__)


class standard_icons(object):
    def __init__(self, widget=None):
        self.widget = widget
        if widget is None:
            self.style = QApplication.instance().style()
        else:
            self.style = widget.style()

    @property
    def dir_open_icon(self):
        return self.style.standardIcon(QStyle.SP_DirOpenIcon)

    @property
    def reload_icon(self):
        return self.style.standardIcon(QStyle.SP_BrowserReload)

    @property
    def cancel_icon(self):
        return self.style.standardIcon(QStyle.SP_DialogCancelButton)


class RuntimeEvent(QEvent):
    Init = QEvent.registerEventType()


def RecentPath_asqstandarditem(pathitem):
    icon_provider = QFileIconProvider()
    # basename of a normalized name (strip right path component separators)
    basename = os.path.basename(os.path.normpath(pathitem.abspath))
    item = QStandardItem(
        icon_provider.icon(QFileInfo(pathitem.abspath)),
        basename
    )
    item.setToolTip(pathitem.abspath)
    item.setData(pathitem, Qt.UserRole)
    return item


class State(enum.IntEnum):
    NoState, Processing, Done, Cancelled, Error = range(5)


class OWImportSounds(widget.OWWidget):
    name = "Import Sounds"
    description = "Import sounds from a directory(s)"
    icon = "icons/import_sound.png"
    priority = 1

    outputs = [("Data", Orange.data.Table)]

    #: list of recent paths
    recent_paths = settings.Setting([])  # type: List[RecentPath]
    currentPath = settings.Setting(None)

    want_main_area = False
    resizing_enabled = False

    Modality = Qt.ApplicationModal
    # Modality = Qt.WindowModal

    MaxRecentItems = 20

    def __init__(self):
        super().__init__()
        #: widget's runtime state
        self.__state = State.NoState
        self._soundMeta = []
        self._soundCategories = {}
        self._data = []

        self.__invalidated = False
        self.__pendingTask = None

        vbox = gui.vBox(self.controlArea)
        hbox = gui.hBox(vbox)
        self.recent_cb = QComboBox(
            sizeAdjustPolicy=QComboBox.AdjustToMinimumContentsLengthWithIcon,
            minimumContentsLength=16,
            acceptDrops=True
        )
        self.recent_cb.installEventFilter(self)
        self.recent_cb.activated[int].connect(self.__onRecentActivated)
        icons = standard_icons(self)

        browseaction = QAction(
            "Open/Load Sounds", self,
            iconText="\N{HORIZONTAL ELLIPSIS}",
            icon=icons.dir_open_icon,
            toolTip="Select a directory from which to load the sounds"
        )
        browseaction.triggered.connect(self.__runOpenDialog)
        reloadaction = QAction(
            "Reload", self,
            icon=icons.reload_icon,
            toolTip="Reload current sounds set"
        )
        reloadaction.triggered.connect(self.reload)
        self.__actions = namespace(
            browse=browseaction,
            reload=reloadaction,
        )

        browsebutton = QPushButton(
            browseaction.iconText(),
            icon=browseaction.icon(),
            toolTip=browseaction.toolTip(),
            clicked=browseaction.trigger
        )
        reloadbutton = QPushButton(
            reloadaction.iconText(),
            icon=reloadaction.icon(),
            clicked=reloadaction.trigger,
            default=True,
        )

        hbox.layout().addWidget(self.recent_cb)
        hbox.layout().addWidget(browsebutton)
        hbox.layout().addWidget(reloadbutton)

        self.addActions([browseaction, reloadaction])

        reloadaction.changed.connect(
            lambda: reloadbutton.setEnabled(reloadaction.isEnabled())
        )
        box = gui.vBox(vbox, "Info")
        self.infostack = QStackedWidget()

        self.info_area = QLabel(
            text="No sound set selected",
            wordWrap=True
        )
        self.progress_widget = QProgressBar(
            minimum=0, maximum=0
        )
        self.cancel_button = QPushButton(
            "Cancel", icon=icons.cancel_icon,
        )
        self.cancel_button.clicked.connect(self.cancel)

        w = QWidget()
        vlayout = QVBoxLayout()
        vlayout.setContentsMargins(0, 0, 0, 0)
        hlayout = QHBoxLayout()
        hlayout.setContentsMargins(0, 0, 0, 0)

        hlayout.addWidget(self.progress_widget)
        hlayout.addWidget(self.cancel_button)
        vlayout.addLayout(hlayout)

        self.pathlabel = TextLabel()
        self.pathlabel.setTextElideMode(Qt.ElideMiddle)
        self.pathlabel.setAttribute(Qt.WA_MacSmallSize)

        vlayout.addWidget(self.pathlabel)
        w.setLayout(vlayout)

        self.infostack.addWidget(self.info_area)
        self.infostack.addWidget(w)

        box.layout().addWidget(self.infostack)

        self.__initRecentItemsModel()
        self.__invalidated = True
        self.__executor = ThreadExecutor(self)

        QApplication.postEvent(self, QEvent(RuntimeEvent.Init))

    def __initRecentItemsModel(self):
        if self.currentPath is not None and \
                not os.path.isdir(self.currentPath):
            self.currentPath = None

        recent_paths = []
        for item in self.recent_paths:
            if os.path.isdir(item.abspath):
                recent_paths.append(item)
        recent_paths = recent_paths[:OWImportSounds.MaxRecentItems]
        recent_model = self.recent_cb.model()
        for pathitem in recent_paths:
            item = RecentPath_asqstandarditem(pathitem)
            recent_model.appendRow(item)

        self.recent_paths = recent_paths

        if self.currentPath is not None and os.path.isdir(
                self.currentPath) and self.recent_paths and os.path.samefile(
                self.currentPath, self.recent_paths[0].abspath):
            self.recent_cb.setCurrentIndex(0)
        else:
            self.currentPath = None
            self.recent_cb.setCurrentIndex(-1)
        self.__actions.reload.setEnabled(self.currentPath is not None)

    def customEvent(self, event):
        """Reimplemented."""
        if event.type() == RuntimeEvent.Init:
            if self.__invalidated:
                try:
                    self.start()
                finally:
                    self.__invalidated = False

        super().customEvent(event)

    def __runOpenDialog(self):
        startdir = os.path.expanduser("~/")
        if self.recent_paths:
            startdir = os.path.dirname(self.recent_paths[0].abspath)

        if OWImportSounds.Modality == Qt.WindowModal:
            dlg = QFileDialog(
                self, "Select Top Level Directory", startdir,
                acceptMode=QFileDialog.AcceptOpen,
                modal=True,
            )
            dlg.setFileMode(QFileDialog.Directory)
            dlg.setOption(QFileDialog.ShowDirsOnly)
            dlg.setDirectory(startdir)
            dlg.setAttribute(Qt.WA_DeleteOnClose)

            @dlg.accepted.connect
            def on_accepted():
                dirpath = dlg.selectedFiles()
                if dirpath:
                    self.setCurrentPath(dirpath[0])
                    self.start()
            dlg.open()
        else:
            dirpath = QFileDialog.getExistingDirectory(
                self, "Select Top Level Directory", startdir
            )
            if dirpath:
                self.setCurrentPath(dirpath)
                self.start()

    def __onRecentActivated(self, index):
        item = self.recent_cb.itemData(index)
        if item is None:
            return
        assert isinstance(item, RecentPath)
        self.setCurrentPath(item.abspath)
        self.start()

    def __updateInfo(self):
        if self.__state == State.NoState:
            text = "No sounds set selected"
        elif self.__state == State.Processing:
            text = "Processing"
        elif self.__state == State.Done:
            nvalid = sum(imeta.isvalid for imeta in self._soundMeta)
            ncategories = len(self._soundCategories)
            if ncategories < 2:
                text = "{} sounds".format(nvalid)
            else:
                text = "{} sounds / {} categories".format(nvalid, ncategories)
        elif self.__state == State.Cancelled:
            text = "Cancelled"
        elif self.__state == State.Error:
            text = "Error state"
        else:
            assert False

        self.info_area.setText(text)

        if self.__state == State.Processing:
            self.infostack.setCurrentIndex(1)
        else:
            self.infostack.setCurrentIndex(0)

    def setCurrentPath(self, path):
        """
        Set the current root sound path to path

        If the path does not exists or is not a directory the current path
        is left unchanged

        Parameters
        ----------
        path : str
            New root import path.

        Returns
        -------
        status : bool
            True if the current root import path was successfully
            changed to path.
        """
        if self.currentPath is not None and path is not None and \
                os.path.isdir(self.currentPath) and os.path.isdir(path) and \
                os.path.samefile(self.currentPath, path):
            return True

        success = True
        error = None
        if path is not None:
            if not os.path.exists(path):
                error = "'{}' does not exist".format(path)
                path = None
                success = False
            elif not os.path.isdir(path):
                error = "'{}' is not a directory".format(path)
                path = None
                success = False

        if error is not None:
            self.error(error)
            warnings.warn(error, UserWarning, stacklevel=3)
        else:
            self.error()

        if path is not None:
            newindex = self.addRecentPath(path)
            self.recent_cb.setCurrentIndex(newindex)
            if newindex >= 0:
                self.currentPath = path
            else:
                self.currentPath = None
        else:
            self.currentPath = None
        self.__actions.reload.setEnabled(self.currentPath is not None)

        if self.__state == State.Processing:
            self.cancel()

        return success

    def addRecentPath(self, path):
        """
        Prepend a path entry to the list of recent paths

        If an entry with the same path already exists in the recent path
        list it is moved to the first place

        Parameters
        ----------
        path : str
        """
        existing = None
        for pathitem in self.recent_paths:
            try:
                if os.path.samefile(pathitem.abspath, path):
                    existing = pathitem
                    break
            except FileNotFoundError:
                # file not found if the `pathitem.abspath` no longer exists
                pass

        model = self.recent_cb.model()

        if existing is not None:
            selected_index = self.recent_paths.index(existing)
            assert model.item(selected_index).data(Qt.UserRole) is existing
            self.recent_paths.remove(existing)
            row = model.takeRow(selected_index)
            self.recent_paths.insert(0, existing)
            model.insertRow(0, row)
        else:
            item = RecentPath(path, None, None)
            self.recent_paths.insert(0, item)
            model.insertRow(0, RecentPath_asqstandarditem(item))
        return 0

    def __setRuntimeState(self, state):
        assert state in State
        self.setBlocking(state == State.Processing)
        message = ""
        if state == State.Processing:
            assert self.__state in [State.Done,
                                    State.NoState,
                                    State.Error,
                                    State.Cancelled]
            message = "Processing"
        elif state == State.Done:
            assert self.__state == State.Processing
        elif state == State.Cancelled:
            assert self.__state == State.Processing
            message = "Cancelled"
        elif state == State.Error:
            message = "Error during processing"
        elif state == State.NoState:
            message = ""
        else:
            assert False

        self.__state = state

        if self.__state == State.Processing:
            self.infostack.setCurrentIndex(1)
        else:
            self.infostack.setCurrentIndex(0)

        self.setStatusMessage(message)
        self.__updateInfo()

    def reload(self):
        """
        Restart the sound scan task
        """
        if self.__state == State.Processing:
            self.cancel()

        self._soundMeta = []
        self._soundCategories = {}
        self.start()

    def start(self):
        """
        Start/execute the sound indexing operation
        """
        self.error()

        self.__invalidated = False
        if self.currentPath is None:
            return

        if self.__state == State.Processing:
            assert self.__pendingTask is not None
            log.info("Starting a new task while one is in progress. "
                     "Cancel the existing task (dir:'{}')"
                     .format(self.__pendingTask.startdir))
            self.cancel()

        startdir = self.currentPath

        self.__setRuntimeState(State.Processing)

        report_progress = methodinvoke(
            self, "__onReportProgress", (object,))

        task = ImageScan(startdir, report_progress=report_progress)

        # collect the task state in one convenient place
        self.__pendingTask = taskstate = namespace(
            task=task,
            startdir=startdir,
            future=None,
            watcher=None,
            cancelled=False,
            cancel=None,
        )

        def cancel():
            # Cancel the task and disconnect
            if taskstate.future.cancel():
                pass
            else:
                taskstate.task.cancelled = True
                taskstate.cancelled = True
                try:
                    taskstate.future.result(timeout=3)
                except UserInterruptError:
                    pass
                except TimeoutError:
                    log.info("The task did not stop in in a timely manner")
            taskstate.watcher.finished.disconnect(self.__onRunFinished)

        taskstate.cancel = cancel

        def run_sound_scan_task_interupt():
            try:
                return task.run()
            except UserInterruptError:
                # Suppress interrupt errors, so they are not logged
                return

        taskstate.future = self.__executor.submit(run_sound_scan_task_interupt)
        taskstate.watcher = FutureWatcher(taskstate.future)
        taskstate.watcher.finished.connect(self.__onRunFinished)

    @Slot()
    def __onRunFinished(self):
        assert QThread.currentThread() is self.thread()
        assert self.__state == State.Processing
        assert self.__pendingTask is not None
        assert self.sender() is self.__pendingTask.watcher
        assert self.__pendingTask.future.done()
        task = self.__pendingTask
        self.__pendingTask = None

        try:
            sound_meta = task.future.result()
        except Exception as err:
            sys.excepthook(*sys.exc_info())
            state = State.Error
            sound_meta = []
            self.error(traceback.format_exc())
        else:
            state = State.Done
            self.error()

        categories = {}

        for smeta in sound_meta:
            # derive categories from the path relative to the starting dir
            dirname = os.path.dirname(smeta.path)
            relpath = os.path.relpath(dirname, task.startdir)
            categories[dirname] = relpath

        self._soundMeta = sound_meta
        self._soundCategories = categories

        self.__setRuntimeState(state)
        self.commit()

    def cancel(self):
        """
        Cancel current pending task (if any).
        """
        if self.__state == State.Processing:
            assert self.__pendingTask is not None
            self.__pendingTask.cancel()
            self.__pendingTask = None
            self.__setRuntimeState(State.Cancelled)

    @Slot(object)
    def __onReportProgress(self, arg):
        # report on scan progress from a worker thread
        # arg must be a namespace(count: int, lastpath: str)
        assert QThread.currentThread() is self.thread()
        if self.__state == State.Processing:
            self.pathlabel.setText(prettyfypath(arg.lastpath))

    def commit(self):
        """
        Create and commit a Table from the collected sound meta data.
        """
        if self._soundMeta:
            categories = self._soundCategories
            if len(categories) > 1:
                cat_var = Orange.data.DiscreteVariable(
                    "category", values=list(sorted(categories.values()))
                )
            else:
                cat_var = None

            # Sound name (file basename without the extension)
            soundname_var = Orange.data.StringVariable("sound name")
            # Full fs path
            sound_var = Orange.data.StringVariable("sound")
            sound_var.attributes["type"] = "sound"
            # file size/length
            size_var = Orange.data.ContinuousVariable(
                "size", number_of_decimals=0)
            length_var = Orange.data.ContinuousVariable(
                "length", number_of_decimals=2)
            framerate_var = Orange.data.ContinuousVariable(
                "framerate", number_of_decimals=0
            )
            domain = Orange.data.Domain(
                [], [cat_var] if cat_var is not None else [],
                [soundname_var, sound_var, size_var, length_var, framerate_var]
            )
            cat_data = []
            meta_data = []

            for soundmeta in self._soundMeta:
                if soundmeta.isvalid:
                    if cat_var is not None:
                        category = categories.get(
                            os.path.dirname(soundmeta.path))
                        cat_data.append([cat_var.to_val(category)])
                    else:
                        cat_data.append([])
                    basename = os.path.basename(soundmeta.path)
                    soundname, _ = os.path.splitext(basename)

                    meta_data.append(
                        [soundname, soundmeta.path, soundmeta.size,
                         soundmeta.length, soundmeta.framerate]
                    )

            cat_data = numpy.array(cat_data, dtype=float)
            meta_data = numpy.array(meta_data, dtype=object)

            if len(meta_data):
                table = Orange.data.Table.from_numpy(
                    domain, numpy.empty((len(cat_data), 0), dtype=float),
                    cat_data, meta_data
                )
            else:
                # empty results, no sounds found
                table = None
        else:
            table = None

        self.send("Data", table)

    def onDeleteWidget(self):
        self.cancel()
        print("danes je lep dan")
        self.__executor.shutdown(wait=True)
        self.__invalidated = False

    def eventFilter(self, receiver, event):
        # re-implemented from QWidget
        # intercept and process drag drop events on the recent directory
        # selection combo box
        def dirpath(event):
            # type: (QDropEvent) -> Optional[str]
            """Return the directory from a QDropEvent."""
            data = event.mimeData()
            urls = data.urls()
            if len(urls) == 1:
                url = urls[0]
                path = url.toLocalFile()
                if os.path.isdir(path):
                    return path
            return None

        if receiver is self.recent_cb and \
                event.type() in {QEvent.DragEnter, QEvent.DragMove,
                                 QEvent.Drop}:
            assert isinstance(event, QDropEvent)
            path = dirpath(event)
            if path is not None and event.possibleActions() & Qt.LinkAction:
                event.setDropAction(Qt.LinkAction)
                event.accept()
                if event.type() == QEvent.Drop:
                    self.setCurrentPath(path)
                    self.start()
            else:
                event.ignore()
            return True

        return super().eventFilter(receiver, event)


class UserInterruptError(BaseException):
    """
    A BaseException subclass used for cooperative task/thread cancellation
    """
    pass


DefaultFormats = ("wav", "mp3")


class ImageScan:
    def __init__(self, startdir, formats=DefaultFormats, report_progress=None):
        self.startdir = startdir
        self.formats = formats
        self.report_progress = report_progress
        self.cancelled = False

    def run(self):
        soundmeta = []
        filescanner = scan(self.startdir)
        patterns = ["*.{}".format(fmt.lower()) for fmt in self.formats]

        def fnmatch_any(fname, patterns):
            return any(fnmatch.fnmatch(fname.lower(), pattern)
                       for pattern in patterns)

        batch = []

        for path in filescanner:
            if fnmatch_any(path, patterns):
                smeta = sound_meta_data(path)
                soundmeta.append(smeta)
                batch.append(soundmeta)

            if self.cancelled:
                return
                # raise UserInterruptError

            if len(batch) == 10 and self.report_progress is not None:
                self.report_progress(
                    namespace(count=len(soundmeta),
                              lastpath=soundmeta[-1].path,
                              batch=batch))
                batch = []

        if batch and self.report_progress is not None:
            self.report_progress(
                namespace(count=len(soundmeta),
                          lastpath=soundmeta[-1].path,
                          batch=batch))

        return soundmeta


def batches(iter, batch_size=10):
    """
    Yield items from iter by batches of size `batch_size`.
    """
    while True:
        batch = list(itertools.islice(iter, 0, batch_size))
        if batch:
            yield batch
        else:
            break


def scan(topdir, include_patterns=("*",), exclude_patterns=(".*",)):
    """
    Yield file system paths under `topdir` that match include/exclude patterns

    Parameters
    ----------
    topdir: str
        Top level directory path for the search.
    include_patterns: List[str]
        `fnmatch.fnmatch` include patterns.
    exclude_patterns: List[str]
        `fnmatch.fnmatch` exclude patterns.

    Returns
    -------
    iter: generator
        A generator yielding matching filesystem paths
    """
    if include_patterns is None:
        include_patterns = ["*"]

    for dirpath, dirnames, filenames in os.walk(topdir):
        for dirname in list(dirnames):
            # do not recurse into hidden dirs
            if fnmatch.fnmatch(dirname, ".*"):
                dirnames.remove(dirname)

        def matches_any(fname, patterns):
            return any(fnmatch.fnmatch(fname, pattern)
                       for pattern in patterns)

        filenames = [fname for fname in filenames
                     if matches_any(fname, include_patterns)
                     and not matches_any(fname, exclude_patterns)]

        yield from (os.path.join(dirpath, fname) for fname in filenames)


def scan_sounds(topdir, formats=DefaultFormats):
    include_patterns = ["*.{}".format(fmt) for fmt in formats]
    path_iter = scan(topdir, include_patterns=include_patterns)
    yield from map(sound_meta_data, path_iter)


def supportedImageFormats():
    return [bytes(fmt).decode("ascii")
            for fmt in QImageReader.supportedImageFormats()]


SoundData = namedtuple(
    "SoundData",
    ["path", "format", "size", "length", "framerate"]
)
SoundData.isvalid = property(lambda self: True)

SoundDataError = namedtuple(
    "SoundDataError",
    ["path", "error", "error_str"]
)
SoundDataError.isvalid = property(lambda self: False)


def sound_meta_data(path):
    data = read(path)
    return SoundData(path, "wav", len(data[1]), float(
        len(data[1])) / float(data[0]), data[0])


def main(argv=sys.argv):
    app = QApplication(list(argv))
    argv = app.arguments()
    if len(argv) > 1:
        path = argv[1]
    else:
        path = None
    w = OWImportSounds()
    w.show()
    w.raise_()

    if path is not None:
        w.setCurrentPath(path)

    app.exec_()
    w.saveSettings()
    w.onDeleteWidget()
    return 0


if __name__ == "__main__":
    sys.exit(main())
