import fnmatch
import os
import shutil
from ..code_weld import BasicTextCodeWelder, WELD_POS
import logging


class FadingFiles(object):
    """
    Create files (and optionaly perform actions on them), and remove them on context exit
    """

    class FileOp(object):

        def __init__(self, to_remove=None):
            self._to_remove = to_remove or []

        def operate(self):
            pass

        def log_op(self):
            logging.warn("Performing %s" % self.__class__.__name__)

        def log_remove(self):
            logging.warn("Fading out files- %s for '%s'" % (self._to_remove, self.__class__.__name__))

        def remove(self):
            for path in self._to_remove:
                if os.path.isdir(path) and len(path) > 6:
                    shutil.rmtree(path)
                else:
                    os.remove(path)

    class CopyOp(FileOp):
        def __init__(self, src, dst):
            super(FadingFiles.CopyOp, self).__init__([dst])
            self.src = src
            self.dst = dst

        def log_op(self):
            logging.warn("FADING-COPY: '%s' -> '%s'" % (self.src, self.dst))

        def operate(self):
            shutil.copyfile(self.src, self.dst)

    class DumpOp(FileOp):
        def __init__(self, data, dst):
            super(FadingFiles.DumpOp, self).__init__([dst])
            self.dst = dst
            self.data = data

        def log_op(self):
            logging.warn("FADING-DUMP: Data['%s'... {%d}] -> '%s'" % (self.data[:10], len(self.data), self.dst))

        def operate(self):
            with open(self.dst, "wb") as dump:
                dump.write(self.data)

    class RevertOp(FileOp):
        def __init__(self, src):
            super(FadingFiles.RevertOp, self).__init__([])
            self.src = src
            self.data = None

        def operate(self):
            # backup
            with open(self.src, "rb") as org:
                self.data = org.read()

        def log_remove(self):
            logging.warn("Reverting (FadingFile): %s'" % self.src)

        def remove(self):
            # restore
            with open(self.src, "wb") as dump:
                dump.write(self.data)

    class InjectOp(RevertOp):
        def __init__(self, src, injection_rules):
            super(FadingFiles.InjectOp, self).__init__(src)
            self.rules = injection_rules

        def log_op(self):
            logging.warn("FADING-INJECTION: into '%s'" % self.src)

        def operate(self):
            super(FadingFiles.InjectOp, self).operate()
            with open(self.src, "wb") as target:
                weld = BasicTextCodeWelder(self.rules).weld(self.data)
                target.write(weld)

    def __init__(self, file_op_list, should_log=False):
        self._logging = should_log
        self.file_list = []
        for file_op in file_op_list:
            if isinstance(file_op, self.FileOp):
                self.file_list.append(file_op)
            else:
                self.file_list.append(self.FileOp([os.path.abspath(file_op)]))

    def __enter__(self):
        for op in self.file_list:
            if self._logging:
                op.log_op()
            op.operate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for op in self.file_list:
            if self._logging:
                op.log_remove()
            op.remove()


def collect_data_files(root_dir, directory_name, exclude=None):
    exclude = exclude or []
    directory = os.path.join(root_dir, directory_name)
    paths = []
    for (path, directories, file_names) in os.walk(directory):
        for filename in file_names:
            file_path = os.path.join(path[len(root_dir) + 1:], filename)
            if True not in [fnmatch.fnmatch(file_path, pattern) for pattern in exclude]:
                paths.append(file_path)
    return directory, paths
