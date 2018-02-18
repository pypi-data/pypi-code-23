# Copyright 2017 SrMouraSilva
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from enum import Enum
from pathlib import Path

from application.controller.controller import Controller
from application.dao.plugins_dao import PluginsDao

from pluginsmanager.model.lv2.lv2_effect_builder import Lv2EffectBuilder
from pluginsmanager.observer.autosaver.persistence import Persistence


class PluginTechnology(Enum):
    """
    Enumeration for informs audio plugins technology
    """
    LV2 = 'lv2'
    """
    LV2 is an open standard for audio plugins, used by hundreds of plugins and other projects.
    At its core, LV2 is a simple stable interface, accompanied by extensions which add functionality
    to support the needs of increasingly powerful audio software.Informs that the change is caused by
    the creation of an object
    """
    LADSPA = 'ladspa'
    VST = 'vst'


class PluginsController(Controller):

    def __init__(self, application):
        super(PluginsController, self).__init__(application)
        self.lv2_builder = None

    def configure(self):
        self.lv2_builder = self._configure_lv2_plugins_data()

    @property
    def _dao(self):
        return self.app.dao(PluginsDao)

    def _configure_lv2_plugins_data(self):
        if not self._dao.exists_data:
            try:
                self.reload_lv2_plugins_data()
                self.app.log("Lv2Plugins data - Loaded lv2 plugins data installed")
            except ImportError as e:
                self.app.log("Lv2Plugins data - It's not possible reload lv2 plugins data")
                self.app.log("                  {}", str(e))
                self.app.log("Lv2Plugins data - Using PluginsManager default lv2 plugins data")
                self._dao.save(Persistence.read(Path(Lv2EffectBuilder.plugins_json_file)))

        return Lv2EffectBuilder(plugins_json=self._dao.path)

    def by(self, technology):
        """
        Get the plugins registered in PedalPi by technology

        :param PluginTechnology technology: PluginTechnology identifier
        """
        if technology == PluginTechnology.LV2 \
        or str(technology).upper() == PluginTechnology.LV2.value.upper():
            return self.lv2_builder.all
        else:
            return []

    def lv2_effect(self, lv2_uri):
        """
        Generates a lv2 effect based in lv2_uri.

        For a effect is effectively generate, it's necessary that is installed in operational system and
        the metadata has loaded.

        For check the installed plugins, use ``lv2ls``::

            sudo apt-get install lilv-utils
            lv2ls

        For check the plugins with metadata loaded, uses::

            >>> plugin = 'http://guitarix.sourceforge.net/plugins/gx_scream_#_scream_'
            >>> plugin in plugins_controller.lv2_builder.plugins
            >>> True

        For force reload plugins data, uses::

            >>> plugins_controller.reload_lv2_plugins_data

        For reload the lv2_plugins_aata, it's necessary the installation of lilv.
        Check `Lv2EffectBuilder.lv2_plugins_data()`_ method documentation for details.

        .. _Lv2EffectBuilder.lv2_plugins_data(): http://pedalpi-pluginsmanager.readthedocs.io/en/latest/model_lv2.html#pluginsmanager.model.lv2.lv2_effect_builder.Lv2EffectBuilder.lv2_plugins_data

        :param string lv2_uri: String thats identifier a effect. Example: `http://guitarix.sourceforge.net/plugins/gx_scream_#_scream_`

        :return: :class:`.Lv2Effect`
        """
        return self.lv2_builder.build(lv2_uri)

    def reload_lv2_plugins_data(self):
        """
        Search for LV2 audio plugins in the system and extract the metadata
        needed by pluginsmanager to generate audio plugins.
        """
        plugins_data = Lv2EffectBuilder().lv2_plugins_data()
        self._dao.save(plugins_data)
