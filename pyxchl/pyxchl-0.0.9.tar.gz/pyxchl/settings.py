import io
import yamlsettings

from . import BaseObject


# region Settings
class Settings(BaseObject):
    _filename = None

    DEFAULTS = u''

    def __init__(self, filename=None, *args, **kwargs):
        super(Settings, self).__init__(*args, **kwargs)
        self._filename = filename

    def get_settings(self):
        conf = yamlsettings.yamldict.load(io.StringIO(self.DEFAULTS))
        if self._filename is not None:
            yamlsettings.update_from_file(conf, self._filename)

        return conf
# endregion


__all__ = ['Settings']
