import os
import shutil

import zc.buildout


class ZipEggs:
    def __init__(self, buildout, name, options):
        self.source_dir = options['source']
        self.target_dir = options['target']
        if not os.path.isdir(self.source_dir):
            raise zc.buildout.UserError('Invalid Source {s!r}'.format(s=self.source_dir))
        if self.target_dir is None:
            raise zc.buildout.UserError('Invalid Target {t!r}'.format(t=self.target_dir))

    def _zipit(self):
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
        for entry in os.listdir(self.source_dir):
            try:
                source = os.path.join(self.source_dir, entry)
                target = os.path.join(self.target_dir, entry)
                print "ZipEggs: {s} > {t}".format(s=source, t=target)
                shutil.make_archive(target, "zip", source)
                os.rename(target + ".zip", target)
                yield target
            except OSError, e:
                print "ZipEggs: ignore {s!r}: {e!r}".format(s=entry, e=e)

    def install(self):
        return list(self._zipit())

    def update(self):
        return list(self._zipit())
