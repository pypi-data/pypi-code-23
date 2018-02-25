###########################################################################
# Top30 is Copyright (C) 2016-2018 Kyle Robbertze <krobbertze@gmail.com>
#
# Top30 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Top30 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Top30.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
"""
Manages the settings that are used while running
"""
from PyQt5.QtCore import QSettings
import os

import top30

class Settings:
    """
    Holds the settings for the top30 module
    """
    def __init__(self):
        self.organisation = 'UCTRadio'
        self.application = 'top30'
        self.config = QSettings(self.organisation, self.application)
        # Set default values if they do not exist
        changed = False
        if (not self.config.contains('song/length')):
            changed = True
            self.config.setValue('song/length', 10000)
        if not self.config.contains('song/start_tag'):
            changed = True
            self.config.setValue('song/start_tag', 'description')
        if not self.config.contains('song/directory'):
            changed = True
            self.config.setValue('song/directory', '~/music/')
        if not self.config.contains('voice/start_overlap'):
            changed = True
            self.config.setValue('voice/start_overlap', 300)
        if not self.config.contains('voice/end_overlap'):
            changed = True
            self.config.setValue('voice/end_overlap', 1400)
        if not self.config.contains('voice/directory'):
            changed = True
            self.config.setValue('voice/directory', '~/music/')
        if not self.config.contains('reference_dbfs'):
            changed = True
            self.config.setValue('reference_dbfs', -20.0)
        if changed:
            del self.config
            self.config = QSettings(self.organisation, self.application)

    def song_length(self):
        """ Returns the length of the song section """
        return self.config.value('song/length', type=int)

    def set_song_length(self, length):
        """" Saves a new length of the song section """
        self.config.setValue('song/length', length)
        del self.config
        self.config = QSettings(self.organisation, self.application)

    def song_start_tag(self):
        """ Retuns the tag that indicates the start of the song section """
        return self.config.value('song/start_tag', type=str).lower()

    def song_directory(self):
        """ Returns the directory of the songs """
        song_directory = self.config.value('song/directory', type=str)
        if song_directory.startswith("~"):
            return os.path.expanduser(song_directory)
        return song_directory

    def voice_start_overlap(self):
        """ Returns the voice start overlap length """
        return self.config.value('voice/start_overlap', type=int)

    def set_voice_start_overlap(self, length):
        """" Saves a new voice sart overlap length """
        self.config.setValue('voice/start_overlap', length)
        del self.config
        self.config = QSettings(self.organisation, self.application)

    def voice_end_overlap(self):
        """ Returns the voice end overlap length """
        return self.config.value('voice/end_overlap', type=int)

    def set_voice_end_overlap(self, length):
        """" Saves a new voice sart overlap length """
        self.config.setValue('voice/end_overlap', length)
        del self.config
        self.config = QSettings(self.organisation, self.application)

    def voice_directory(self):
        """ Returns the directory of the voice """
        voice_directory = self.config.value('voice/directory', type=str)
        if voice_directory.startswith("~"):
            return os.path.expanduser(voice_directory)
        return voice_directory

    def set_reference_dbfs(self, level):
        """ Saves a new dBFS level to normalise clips to """
        self.config.setValue('reference_dbfs', level)
        del self.config
        self.config = QSettings(self.organisation, self.application)

    def reference_dbfs(self):
        """ Returns the reference dBFS used to normalise source clips """
        return self.config.value("reference_dbfs", type=float)
