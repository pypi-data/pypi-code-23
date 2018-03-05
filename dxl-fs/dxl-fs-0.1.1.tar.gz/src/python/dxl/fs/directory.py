from .path import Path
from .base import ObjectOnFileSystem
from .file import File
from .utils import outputs_observable
import rx


class Directory(ObjectOnFileSystem):
    def __init__(self, path: Path, filesystem=None):
        super().__init__(filesystem, path)

    def exists(self):
        result = super().exists()
        if not result:
            return result
        with self.filesystem.open() as fs:
            if not fs.isdir(self.path.s):
                raise NotADirectoryError(self.path.s)
        return result

    def listdir(self):
        with self.filesystem.open() as fs:
            children = fs.listdir(self.path.s)
            paths = [self.path / c for c in children]
            results = []
            for p in paths:
                if fs.isfile(p.s):
                    results.append(File(p, self.filesystem))
                else:
                    results.append(Directory(p, self.filesystem))
            return tuple(results)

    def listdir_as_observable(self):
        return rx.Observable.from_(self.listdir(),
                                   scheduler=rx.concurrency.ThreadPoolScheduler())

    def copy_to(self, target_path: Path):
        with self.filesystem.open() as fs:
            fs.copydir(self.path.s, target_path.s)
        return Directory(target_path, self.filesystem)

    def sync(self, source: 'Observable[ObjectOnFileSystem] or List[ObjectOnFileSystem]'):
        is_observable = isinstance(source, rx.Observable)
        if not isinstance(source, rx.Observable):
            source = rx.Observable.from_(source,
                                         scheduler=rx.concurrency.ThreadPoolScheduler())
        with self.filesystem.open() as fs:
            result = (source.map(lambda o: o.copy_to(self.path / o.path.n))
                      .to_list()
                      .to_blocking()
                      .first())
        if is_observable:
            return rx.Observable.from_(result,
                                       scheduler=rx.concurrency.ThreadPoolScheduler())
        return result


def match_directory(patterns):
    if isinstance(patterns, str):
        patterns = (patterns, )
    return lambda o: isinstance(o, Directory) and (o.match(patterns))


def match_file(patterns):
    if isinstance(patterns, str):
        patterns = (patterns,)
    from .file import File
    return lambda o: isinstance(o, File) and (o.match(patterns))
