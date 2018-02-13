import json
import logging

from .dbitem import *


class DbPlaylist(DbItem):

    def __init__(self):
        columns = [
            DbColumn('id', 'TEXT'),
            DbColumn('name', 'TEXT'),
            DbColumn('description', 'TEXT'),
            DbColumn('version', 'TEXT'),
            DbColumn('type', 'TEXT'),
            DbColumn('args', 'TEXT'),
            DbColumn('final', 'INTEGER'),
        ]
        DbItem.__init__(self, columns)

    def from_playlist(self, p):
        self.id = p.get('id')
        self.name = p.get('name', '')
        self.description = p.get('description')
        d = json.loads(p.get('description'))
        self.version = d.get('version', '')
        self.type = d.get('type', '')
        self.args = d.get('args', '')
        if d.get('final', False) == True:
            self.final = 1
        else:
            self.final = 0


class DbPlaylistCache():
    final_cache = {}

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def are_final_check(self, pl_type, pl_args):
        key = "%s:%s" % (pl_type, pl_args)
        if key in self.final_cache:
            return self.final_cache[key]
        return None

    def are_final(self, pl_type, pl_args, playlists):
        key = "%s:%s" % (pl_type, pl_args)
        if key in self.final_cache:
            return self.final_cache[key]
        final = False
        for p in playlists:
            if p.final != True:
                final = False
                break
            else:
                final = True
        self.logger.info("Playlist for %s:%s final? " % (pl_type, pl_args) + str(final))
        self.final_cache[key] = final
        return final
