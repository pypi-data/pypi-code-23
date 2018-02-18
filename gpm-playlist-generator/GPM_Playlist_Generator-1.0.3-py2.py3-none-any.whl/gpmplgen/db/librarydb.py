import logging
import os
import sqlite3

from . import *
from gpmplgen.db import *
from gpmplgen.gpm.gpmitem import GPMItem


class LibraryDb:
    LIBRARY_TABLE = 'library'
    STATIC_PL_TABLE = 'static_playlists'
    GENERATED_PL_TABLE = 'generated_playlists'
    ALLTRACKS_TABLE = 'alltracks'

    def __init__(self, db_filename=None):
        self.logger = logging.getLogger(__name__)

        if db_filename is not None:
            db = db_filename
            self.cache_mode = True
            self.logger.debug("Using %s as DB" % db)
        else:
            db = ':memory:'  # In-memory
            self.cache_mode = False
        self.db_conn = sqlite3.connect(db)

    def __del__(self):
        self.db_conn.commit()
        self.db_conn.close()

    def ingest_track_list(self, track_list, table):
        cursor = self.db_conn.cursor()
        self._create_table(cursor, table, DbTrack().get_schema())
        for track in track_list:
            t = GPMItem(track)
            db_track = DbTrack()
            db_track.from_track(t)
            cursor.execute("INSERT INTO {} VALUES {}".format(table, db_track.sql_field_parameters()),
                           db_track.values())
        self.db_conn.commit()

    def consolidate_all_tracks(self):
        cursor = self.db_conn.cursor()
        self._create_table(cursor, self.ALLTRACKS_TABLE, DbTrack().get_constrained_schema())
        for table in [self.LIBRARY_TABLE, self.STATIC_PL_TABLE]:
            cursor.execute("INSERT INTO {} SELECT * FROM {}".format(self.ALLTRACKS_TABLE, table))
        self.db_conn.commit()


    def ingest_generated_playlists(self, playlists):
        cursor = self.db_conn.cursor()
        self._create_table(cursor, self.GENERATED_PL_TABLE, DbPlaylist().get_schema())
        for pl in playlists:
            p = GPMItem(pl)
            db_playlist = DbPlaylist()
            db_playlist.from_playlist(p)

            cursor.execute("INSERT INTO {} VALUES {}".format(self.GENERATED_PL_TABLE, db_playlist.sql_field_parameters()),
                           db_playlist.values())
        self.db_conn.commit()

    def get_tracks(self, query='', table=LIBRARY_TABLE):
        c = self.db_conn.cursor()
        tracks = []
        for row in c.execute("SELECT * FROM {} {}".format(table, query)):
            db_tracks = DbTrack()
            db_tracks.from_db_row(row)
            tracks.append(db_tracks)
        return tracks

    def get_generated_playlists(self, query=''):
        c = self.db_conn.cursor()
        playlists = []
        for row in c.execute("SELECT * FROM {} {}".format(self.GENERATED_PL_TABLE, query)):
            db_playlist = DbPlaylist()
            db_playlist.from_db_row(row)
            playlists.append(db_playlist)
        return playlists

    def _create_table(self, cursor, table, schema):
        try:
            cursor.execute("DROP TABLE {}".format(table))
        except sqlite3.OperationalError:
            pass
        cursor.execute("CREATE TABLE {} {}".format(table, schema))