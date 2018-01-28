import unittest
import sqlite3
from breezeblocks import Database, Table
from breezeblocks.exceptions import QueryError
from breezeblocks.sql.aggregates import Count_, RecordCount
from breezeblocks.sql.join import InnerJoin, LeftJoin, CrossJoin
from breezeblocks.sql.operators import Equal_, In_
from breezeblocks.sql.values import QmarkStyleValue as Value

import os
DB_URL = os.path.join(os.path.dirname(__file__), 'Chinook.sqlite')

class SQLiteChinookTests(unittest.TestCase):
    """Tests using SQLite with the Chinook Database"""
    
    def setUp(self):
        """Performs necessary SQLite3 setup."""
        
        self.db = Database(DB_URL, sqlite3)
        self.tables = {
            'Artist': Table('Artist', ['ArtistId', 'Name']),
            'Genre': Table('Genre', ['GenreId', 'Name']),
            'Album': Table('Album', ['AlbumId', 'Title', 'ArtistId']),
            'Track': Table('Track',
                ['TrackId', 'Name', 'AlbumId', 'MediaTypeId', 'GenreId', 'Composer', 'Milliseconds', 'Bytes', 'UnitPrice']),
            'Playlist': Table('Playlist', ['PlaylistId', 'Name'])
        }
    
    def test_tableQuery(self):
        """Tests a simple select on a table."""
        q = self.db.query(self.tables['Artist']).get()
        
        # Assertion checks that all columns in the table are present in
        # each row returned.
        for row in q.execute():
            self.assertTrue(hasattr(row, 'ArtistId'))
            self.assertTrue(hasattr(row, 'Name'))
    
    def test_columnQuery(self):
        """Tests a simple select on a column."""
        q = self.db.query(self.tables['Artist'].getColumn('Name')).get()
    
        # Assertion checks that only the queried columns are returned.
        for row in q.execute():
            self.assertTrue(hasattr(row, 'Name'))
            self.assertFalse(hasattr(row, 'ArtistId'))
    
    def test_simpleWhereClause(self):
        """Tests a simple where clause."""
        tbl_genre = self.tables['Genre']
        tbl_track = self.tables['Track']
        genre_id = self.db.query(tbl_genre)\
            .where(tbl_genre.getColumn('Name') == Value('Alternative & Punk'))\
            .get().execute()[0].GenreId
    
        q = self.db.query(tbl_track.getColumn('GenreId'))\
                .where(tbl_track.getColumn('GenreId') == Value(genre_id))\
                .get()
    
        # Assertion checks that the where condition has been applied to
        # the results of the query.
        for track in q.execute():
            self.assertEqual(genre_id, track.GenreId)
    
    def test_nestedQueryInWhereClause(self):
        tbl_album = self.tables['Album']
        tbl_genre = self.tables['Genre']
        tbl_track = self.tables['Track']
    
        genre_id = self.db.query(tbl_genre)\
            .where(tbl_genre.getColumn('Name') == Value('Alternative & Punk'))\
            .get().execute()[0].GenreId
    
        q = self.db.query(tbl_album.getColumn('Title'))\
                .where(
                    In_(
                        tbl_album.getColumn('AlbumId'),
                        self.db.query(tbl_track.getColumn('AlbumId'))\
                            .where(tbl_track.getColumn('GenreId') == Value(genre_id)).get()
                    )
                ).get()
    
        # No assertion here because subqueries because subqueries in the select
        # clause have not been implemented.
        # However, the query running without error is important to test.
        q.execute()
    
    def test_aliasTable(self):
        tbl_album = self.tables['Album']
        tbl_artist = self.tables['Artist']
        
        artist_id = self.db.query(tbl_artist.getColumn('ArtistId'))\
            .where(Equal_(tbl_artist.getColumn('Name'), Value('Queen')))\
            .get().execute()[0].ArtistId
        
        musician = tbl_artist.as_('Musician')
        q = self.db.query(musician).where(Equal_(musician.getColumn('ArtistId'), Value(artist_id))).get()
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'ArtistId'))
            self.assertTrue(hasattr(row, 'Name'))
            self.assertEqual(artist_id, row.ArtistId)
    
    def test_selectFromQuery(self):
        tbl_album = self.tables['Album']
        tbl_artist = self.tables['Artist']
        
        artist_id = self.db.query(tbl_artist.getColumn('ArtistId'))\
            .where(Equal_(tbl_artist.getColumn('Name'), Value('Queen')))\
            .get().execute()[0].ArtistId
        
        inner_q = self.db.query(tbl_album.getColumn('ArtistId'), tbl_album.getColumn('Title'))\
            .where(Equal_(tbl_album.getColumn('ArtistId'), Value(artist_id))).get()
        
        q = self.db.query(inner_q.as_('q')).get()
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'ArtistId'))
            self.assertTrue(hasattr(row, 'Title'))
            self.assertEqual(artist_id, row.ArtistId)
    
    def test_groupBy(self):
        tbl_track = self.tables['Track']
        
        q = self.db.query(tbl_track.getColumn('GenreId'), Count_(tbl_track.getColumn('TrackId')).as_('TrackCount'))\
            .group_by(tbl_track.getColumn('GenreId')).get()
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'GenreId'))
            self.assertTrue(hasattr(row, 'TrackCount'))
    
    def test_having(self):
        tbl_track = self.tables['Track']
        
        q = self.db.query(tbl_track.getColumn('GenreId'), Count_(tbl_track.getColumn('TrackId')).as_('TrackCount'))\
            .group_by(tbl_track.getColumn('GenreId'))\
            .having(Count_(tbl_track.getColumn('TrackId')) > Value(25)).get()
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'GenreId'))
            self.assertTrue(hasattr(row, 'TrackCount'))
            self.assertLess(25, row.TrackCount,
                'The track count should be greater than specified in the'\
                'having clause.'
            )
    
    def test_havingMustHaveGroupBy(self):
        tbl_track = self.tables['Track']
        
        with self.assertRaises(QueryError):
            self.db.query(tbl_track.getColumn('GenreId'), Count_(tbl_track.getColumn('TrackId')).as_('TrackCount'))\
                .having(Count_(tbl_track.getColumn('TrackId')) > Value(25)).get()
    
    def test_orderByAsc(self):
        tbl_artist = self.tables['Artist']
        
        q = self.db.query(tbl_artist.getColumn('Name'))\
            .order_by(tbl_artist.getColumn('Name')).get()
        
        rows = q.execute()
        prev_name = rows[0].Name
        for row in rows:
            self.assertLessEqual(prev_name, row.Name)
            prev_name = row.Name
    
    def test_orderByDesc(self):
        tbl_artist = self.tables['Artist']
        
        q = self.db.query(tbl_artist.getColumn('Name'))\
            .order_by(tbl_artist.getColumn('Name'), ascending=False).get()
        
        rows = q.execute()
        prev_name = rows[0].Name
        for row in rows:
            self.assertGreaterEqual(prev_name, row.Name)
            prev_name = row.Name
    
    # NULLS { FIRST | LAST } syntax not supported by SQLite currently.
    # def test_orderByNullsFirst(self):
    #     pass
    
    # NULLS { FIRST | LAST } syntax not supported by SQLite currently.
    # def test_orderByNullsLast(self):
    #     pass
    
    def test_limit(self):
        limit_amount = 5
        
        tbl_track = self.tables['Track']
        
        q = self.db.query(tbl_track.getColumn('Name')).get()
        
        rows = q.execute(limit=limit_amount)
        self.assertLessEqual(len(rows), limit_amount,
            'Number of rows should not be more than the limit amount.')
    
    def test_limitAndOffset(self):
        limit_amount = 100
        tbl_track = self.tables['Track']
        
        q0 = self.db.query(tbl_track.getColumn('TrackId'))\
            .order_by(tbl_track.getColumn('TrackId'))\
            .get()
        q1 = self.db.query(tbl_track.getColumn('TrackId'))\
            .order_by(tbl_track.getColumn('TrackId'))\
            .get()
        
        id_set = set(r.TrackId for r in q0.execute(limit=limit_amount))
        
        for row in q1.execute(limit_amount, limit_amount):
            self.assertTrue(row.TrackId not in id_set,
                'Using offset should result in different data being'
                'returned than that of a non-offset query.'
            )
    
    def test_distinct(self):
        # Uses album 73 (Eric Clapton Unplugged) because it has multiple genres
        # of track on the album. It just seems a bit less trivial than most
        # albums as a test case.
        album_id = 73
        tbl_track = self.tables['Track']
        
        q0 = self.db.query(tbl_track.getColumn('GenreId'))\
            .where(tbl_track.getColumn('AlbumId') == Value(album_id)).get()
        
        q1 = self.db.query(tbl_track.getColumn('GenreId'))\
            .where(tbl_track.getColumn('AlbumId') == Value(album_id))\
            .distinct().get()
        
        genres0 = set(row.GenreId for row in q0.execute())
        genres1 = [row.GenreId for row in q1.execute()]
        self.assertEqual(len(genres0), len(genres1),
            'Set of all genres in the album should be the same size as'
            'the list of genres retrieved with SELECT DISTINCT.'
        )
    
    def test_innerJoin(self):
        tbl_album = self.tables['Album']
        tbl_track = self.tables['Track']
    
        tbl_joinAlbumTrack = InnerJoin(tbl_album, tbl_track, using=['AlbumId'])
    
        q = self.db.query(
            tbl_joinAlbumTrack.left,
            tbl_joinAlbumTrack.right.getColumn('Name')).get()
    
        for row in q.execute():
            self.assertEqual(4, len(row))
            self.assertTrue(hasattr(row, 'AlbumId'))
            self.assertTrue(hasattr(row, 'Title'))
            self.assertTrue(hasattr(row, 'ArtistId'))
            self.assertTrue(hasattr(row, 'Name'))
    
    def test_leftOuterJoin(self):
        tbl_album = self.tables['Album']
        tbl_track = self.tables['Track']
        
        tbl_leftJoinTrackAlbum = LeftJoin(tbl_track, tbl_album, using=['AlbumId'])
        
        q = self.db.query(
            tbl_leftJoinTrackAlbum.left.getColumn('Name'),
            tbl_leftJoinTrackAlbum.right.getColumn('Title').as_('AlbumTitle')
        ).get()
        
        for row in q.execute():
            self.assertTrue(hasattr(row, 'Name'))
            self.assertTrue(hasattr(row, 'AlbumTitle'))
    
    # Right Join not supported by SQLite currently.
    # def test_rightOuterJoin(self):
        # pass
    
    # Full Outer Join not supported by SQLite currently
    # def test_fullOuterJoin(self):
        # pass
    
    def test_crossJoin(self):
        tbl_playlist = self.tables['Playlist']
        tbl_track = self.tables['Track']
        
        playlistRecordCount = self.db.query()\
            .from_(tbl_playlist)\
            .select(RecordCount())\
            .get().execute()[0][0]
        
        trackRecordCount = self.db.query()\
            .from_(tbl_track)\
            .select(RecordCount())\
            .get().execute()[0][0]
        
        q = self.db.query()\
            .from_(CrossJoin(tbl_playlist, tbl_track))\
            .select(RecordCount().as_('RecordCount'))\
            .get()
        
        joinSizeRow = q.execute()[0]
        
        self.assertEqual(playlistRecordCount * trackRecordCount, joinSizeRow.RecordCount,
            'The cross join should contain as many records as '\
            'the number of playlists times the number of tracks.'
        )
