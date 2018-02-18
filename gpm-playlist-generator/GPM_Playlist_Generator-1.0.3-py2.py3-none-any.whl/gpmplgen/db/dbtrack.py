from .dbitem import *

class DbTrack(DbItem):

    UNIQUE_CONSTRAINT = 'UNIQUE (trackId, albumId, discNumber, trackNumber, playCount) ON CONFLICT IGNORE'

    def __init__(self):
        columns = [
            DbColumn('id', 'TEXT'),
            DbColumn('trackId', 'TEXT'),
            DbColumn('albumId', 'TEXT'),
            DbColumn('discNumber', 'INTEGER'),
            DbColumn('trackNumber', 'INTEGER'),
            DbColumn('creationTimestamp', 'INTEGER'),
            DbColumn('recentTimestamp', 'INTEGER'),
            DbColumn('playCount', 'INTEGER')
        ]
        DbItem.__init__(self, columns)

    def get_constrained_schema(self):
        return '(%s, %s)' % (self.get_schema_inner(), self.UNIQUE_CONSTRAINT)

    def from_track(self, track):
        self.id = track.get('id')
        self.trackId = track.get('trackId', '')
        self.albumId = track.get('albumId', '')
        self.discNumber = int(track.get('discNumber', 0))
        self.trackNumber = int(track.get('trackNumber', 0))
        self.creationTimestamp = int(track.get('creationTimestamp', 0))
        self.recentTimestamp = int(track.get('recentTimestamp', 0))
        self.playCount = int(track.get('playCount', 0))
