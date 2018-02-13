import itertools
import json
import logging
import time

import gpmplgen


class Playlist:
    VERSION = 1
    GENERATEDBY = 'GPMPlGen'
    PLAYLIST_MAX = 1000

    def __init__(self, name, generated_timestamp=None, id=None):
        self.logger = logging.getLogger(__name__)
        self.name = name
        self.id = id
        if generated_timestamp:
            self.generated = generated_timestamp
        else:
            self.generated = time.time()
        self.tracks = []
        self.type = None
        self.args = None
        self.final = False

    def get_name(self):
        return self.name

    def set_type(self, playlist_type):
        self.type = playlist_type

    def set_args(self, args):
        self.args = args

    def set_final(self, value=True):
        self.final = value

    def get_description(self):
        description = {
            'version': Playlist.VERSION,
            'generatedby': Playlist.GENERATEDBY,
            'generated': self.generated,
            'type': self.type,
            'args': self.args,
            'final': self.final
        }
        return json.dumps(description)

    def add_track(self, track):
        self.tracks.append(track)

    def inherit_attributes(self, other):
        self.type = other.type
        self.args = other.args
        self.final = other.final

    def get_ingestable_playlists(self):
        it = iter(self.tracks)
        item = list(itertools.islice(it, Playlist.PLAYLIST_MAX))
        total_count = 1 + len(self.tracks) / Playlist.PLAYLIST_MAX
        n = 1
        while item:
            name = self.name
            if total_count > 1:
                name += " (%d/%d)" % (n, total_count)
            pl = Playlist(name, self.generated)
            pl.inherit_attributes(self)
            pl.tracks = item
            yield pl
            item = list(itertools.islice(it, Playlist.PLAYLIST_MAX))
            n += 1

    @staticmethod
    def is_generated_by_gpmplgen(playlist_dict):
        try:
            desc = json.loads(playlist_dict['description'])
            if desc['generatedby'] == Playlist.GENERATEDBY:
                if desc['version'] == Playlist.VERSION:
                   return True
                else:
                    logging.error("Unsupported version")
        except:
            return False
        return False

    def create_in_gpm(self, client):
        self.logger.info("Creating playlist " + self.get_name())
        try:
            self.id = client.create_playlist(self.get_name(), description=self.get_description())
        except Exception as e:
            raise gpmplgen.GPMPlGenException("Error creating playlists on Google Play Music", e)
        try:
            client.add_songs_to_playlist(self.id, self.tracks)
        except Exception as e:
            raise gpmplgen.GPMPlGenException("Error adding songs to playlist on Google Play Music", e)

    def delete_in_gpm(self, client):
        if self.id is None:
            self.logger.debug('Not deleting non-existing playlist %s' % (self.name))
            return
        self.logger.info('Deleting %s: %s' % (self.id, self.name))
        client.delete_playlist(self.id)
