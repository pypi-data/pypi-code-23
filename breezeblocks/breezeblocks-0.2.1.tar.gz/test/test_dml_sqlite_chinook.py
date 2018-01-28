import unittest
from unittest.mock import patch, Mock
import sqlite3
from breezeblocks import Database, Table

import os
DB_URL = os.path.join(os.path.dirname(__file__), 'Chinook.sqlite')

class SQLiteChinookTests(unittest.TestCase):
    """DML tests using SQLite with the Chinook Database"""
    
    def setUp(self):
        """Performs necessary SQLite3 setup."""
        with patch('sqlite3.Connection') as Connection:
            Connection.return_value.commit = Mock()
            with patch.object(sqlite3, 'Connection', Connection) as sqlite:
                print(sqlite)
                self.db = Database(DB_URL, sqlite)
                self.tables = {
                    'Artist': Table('Artist', ['ArtistId', 'Name']),
                    'Genre': Table('Genre', ['GenreId', 'Name']),
                    'Album': Table('Album', ['AlbumId', 'Title', 'ArtistId']),
                    'Track': Table('Track',
                        ['TrackId', 'Name', 'AlbumId', 'MediaTypeId', 'GenreId', 'Composer', 'Milliseconds', 'Bytes', 'UnitPrice']),
                    'Playlist': Table('Playlist', ['PlaylistId', 'Name'])
                }
    
    def test_basicInsert(self):
        i = self.db.insert(self.tables['Artist']).add_columns('Name').get()
        
        i.execute([
            ('The Shins',),
            ('Modest Mouse',),
            ('Weezer',)
        ])
    
    def test_selectInsert(self):
        pass
    
    def test_basicUpdate(self):
        pass
    
    def test_basicDelete(self):
        pass
