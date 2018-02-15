import io
import yamlsettings

from pyxchl import BaseObject


# region Settings
class SettingsBase(BaseObject):
    DEFAULTS = ''

    def __init__(self, filename, *args, **kwargs):
        super(SettingsBase, self).__init__(*args, **kwargs)
        self._filename = filename

    def get_settings(self):
        conf = yamlsettings.yamldict.load(io.StringIO(self.DEFAULTS))
        yamlsettings.update_from_file(conf, self._filename)
        return conf
# endregion
