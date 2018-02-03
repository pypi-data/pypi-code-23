import unittest
from unittest.mock import patch, Mock
import sqlite3
from breezeblocks import Database, Table
from breezeblocks.sql.operators import Equal_, Like_
from breezeblocks.sql.values import QmarkStyleValue as Value

import os
DB_URL = os.path.join(os.path.dirname(__file__), 'Chinook.sqlite')

class SQLiteChinookTests(unittest.TestCase):
    """DML tests using SQLite with the Chinook Database"""
    
    def setUp(self):
        """Performs necessary SQLite3 setup."""
        self.db = Database(dsn=DB_URL, dbapi_module=sqlite3)
        self.tables = {
            'Artist': Table('Artist', ['ArtistId', 'Name']),
            'Genre': Table('Genre', ['GenreId', 'Name']),
            'Album': Table('Album', ['AlbumId', 'Title', 'ArtistId']),
            'Track': Table('Track',
                ['TrackId', 'Name', 'AlbumId', 'MediaTypeId', 'GenreId', 'Composer', 'Milliseconds', 'Bytes', 'UnitPrice']),
            'Playlist': Table('Playlist', ['PlaylistId', 'Name']),
            'PlaylistTrack': Table('PlaylistTrack', ['PlaylistId', 'TrackId'])
        }
    
    def test_insertIntoValues(self):
        conn = self.db.pool.get()
        
        i = self.db.insert(self.tables['Artist']).add_columns('Name').get()
        
        i.execute([
            ('Weezer',)
        ], conn=conn)
        
        cur = conn.cursor()
        
        q = self.db.query(self.tables['Artist'].columns['Name'])\
            .where(Equal_(self.tables['Artist'].columns['Name'], Value('Weezer')))\
            .get()
        
        rows = q.execute(conn=conn)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].Name, 'Weezer')
    
    def test_insertIntoSelect(self):
        t_genre = self.tables['Genre']
        t_track = self.tables['Track']
        t_playlist = self.tables['Playlist']
        t_playlistTrack = self.tables['PlaylistTrack']
        
        conn = self.db.pool.get()
        
        genre_id = self.db.query(t_genre.columns['GenreId'])\
            .where(t_genre.columns['Name'] == Value('Jazz'))\
            .get().execute(limit=1)[0].GenreId
        
        # Setting up the initial playlist row
        self.db.insert(t_playlist).add_columns(t_playlist.columns['Name'])\
            .get().execute([('LP Jazz Mix',)], conn=conn)
        playlist_id = self.db.query(t_playlist.columns['PlaylistId'])\
            .where(t_playlist.columns['Name'] == Value('LP Jazz Mix'))\
            .get().execute(conn=conn)[0].PlaylistId
        
        # Testing the INSERT INTO SELECT
        i = self.db.insert(t_playlistTrack).add_columns('PlaylistId', 'TrackId')\
            .get()
        q = self.db.query(Value(playlist_id), t_track.columns['TrackId'])\
            .where(t_track.columns['GenreId'] == Value(genre_id)).get()
        
        i.execute(q, conn=conn)
        
        q2 = self.db.query(t_playlistTrack.columns['TrackId'])\
            .where(t_playlistTrack.columns['PlaylistId'] == Value(playlist_id))\
            .get()
        
        self.assertEqual(len(q2.execute(conn=conn)), len(q.execute(conn=conn)))
    
    def test_update(self):
        t_genre = self.tables['Genre']
        t_album = self.tables['Album']
        t_track = self.tables['Track']
        
        genre_id = self.db.query(t_genre.columns['GenreId'])\
            .where(Equal_(t_genre.columns['Name'], Value('Pop')))\
            .get().execute(limit=1)[0].GenreId
        album_id = self.db.query(t_album.columns['AlbumId'])\
            .where(Equal_(t_album.columns['Title'], Value('American Idiot')))\
            .get().execute()[0].AlbumId
        conn = self.db.pool.get()
        
        # This album was recorded in their Pop period
        u = self.db.update(t_track)\
            .set_(t_track.columns['GenreId'], Value(genre_id))\
            .where(Equal_(t_track.columns['AlbumId'], Value(album_id))).get()
        
        u.execute(conn=conn)
        
        q = self.db.query(t_track.columns['GenreId'])\
            .where(Equal_(t_track.columns['AlbumId'], Value(album_id))).get()
        
        for row in q.execute(conn=conn):
            self.assertEqual(row.GenreId, genre_id)
    
    def test_delete(self):
        conn = self.db.pool.get()
        
        # My episodes of Lost are just taking up too much space on my HDD
        d = self.db.delete(self.tables['Album']).where(
            Like_(self.tables['Album'].columns['Title'], Value('Lost, Season%'))
        ).get()
        
        d.execute(conn)
        
        q = self.db.query(self.tables['Album'].columns['AlbumId']).where(
            Like_(self.tables['Album'].columns['Title'], Value('Lost, Season%'))
        ).get()
        
        rows = q.execute(conn=conn)
        # All corresponding rows should have been deleted on this connection
        self.assertEqual(len(rows), 0)
