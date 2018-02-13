import time
import logging

from gmusicapi import Mobileclient

from .clientmock import ClientMock
from .db.librarydb import LibraryDb
from .gpm import *


class GPMPlGen:
    def __init__(self, config):
        self.config = config

        logging.basicConfig(level=config.log_level)
        self.logger = logging.getLogger(__name__)

        # Client
        self.client = Mobileclient(debug_logging=False)
        gmusicapi_logger = logging.getLogger('gmusicapi.utils')
        gmusicapi_logger.setLevel(logging.INFO)

        # Logging in
        self.logger.info('Logging in %s' % config.username)
        try:
            android_id = config.client_id
            if android_id is None:
                android_id = Mobileclient.FROM_MAC_ADDRESS
            success = self.client.login(config.username, config.password, android_id)
            if not success:
                raise GPMPlGenException("Could not log in")
        except Exception as e:
            raise GPMPlGenException("Could not log in", e)

        # Setting up writer
        if config.dry_run:
            self.logger.info('Running in DRY-RUN mode; setting up mock client...')
            self.writer_client = ClientMock()
        else:
            self.writer_client = self.client

        # Local database
        self.db = LibraryDb(config.local_db)

        # Internal stuff
        self.timestamp = time.time()

    def _get_all_songs(self):
        self.logger.info("Downloading all tracks from library")
        try:
            library_from_gpm = self.client.get_all_songs(incremental=False)
        except Exception as e:
            GPMPlGenException("Could not download library", e)
        self.logger.info("Loaded %d songs" % (len(library_from_gpm)))
        return library_from_gpm

    def _get_all_playlists_songs(self, static_playlists):
        self.logger.info("Downloading all tracks from playlists (this may take a few minutes)")
        try:
            playlists_with_contents = self.client.get_all_user_playlist_contents()
            self.logger.info("Loaded %d playlists" % (len(playlists_with_contents)))
        except Exception as e:
            GPMPlGenException("Could not download playlist contents", e)
        songs_from_static_playlists = []
        static_playlists_ids = map((lambda p: p['id']), static_playlists)
        for p in playlists_with_contents:
            if p['id'] in static_playlists_ids:
                if 'tracks' in p:
                    for t in p['tracks']:
                        if 'track' in t:
                            track = t['track']
                            track['id'] = t['id']
                        else:
                            track = t
                        songs_from_static_playlists.append(track)
        self.logger.info("Loaded %d songs" % (len(songs_from_static_playlists)))
        return songs_from_static_playlists

    def store_songs_in_db(self):
        library_from_gpm = self._get_all_songs()
        self.db.ingest_track_list(library_from_gpm, LibraryDb.LIBRARY_TABLE)

    def store_playlists_in_db(self, get_songs=True):
        self.logger.info("Downloading all generated playlists from library")
        (generated_playlists, other_playlists) = self._get_all_playlists()
        self.logger.info("Loading %d generated playlists"
                         % (len(generated_playlists)))
        self.db.ingest_generated_playlists(generated_playlists)
        if not get_songs:
            return
        self.logger.info("Loading %d static playlists"
                         % (len(other_playlists)))
        tracks = self._get_all_playlists_songs(other_playlists)
        self.db.ingest_track_list(tracks, LibraryDb.STATIC_PL_TABLE)

    def retrieve_library(self, get_songs=True):
        if self.db.cache_mode:
            if self.config.write_to_db:
                self.logger.info("Storing into cache")
                self.store_songs_in_db()
                self.store_playlists_in_db()
                self.db.consolidate_all_tracks()
            else:
                self.logger.info("Using cache")
            return

        # Get songs
        if get_songs:
            self.store_songs_in_db()

        # Get playlists and potentially their contents
        self.store_playlists_in_db(get_songs)

        # Generate full track list
        if get_songs:
            self.db.consolidate_all_tracks()

    def _get_all_playlists(self):
        self.logger.info('Getting playlists')
        playlists_from_gpm = []
        try:
            playlists_from_gpm = self.client.get_all_playlists()
        except Exception as e:
            GPMPlGenException("Could not download playlists", e)
        generated_playlists = []
        static_playlists = []
        for pl in playlists_from_gpm:
            if Playlist.is_generated_by_gpmplgen(pl):
                generated_playlists.append(pl)
            else:
                static_playlists.append(pl)
        return (generated_playlists, static_playlists)

    def delete_playlists(self, playlists):
        # FIXME: replace with playlist.delete
        for pl in playlists:
            self.logger.info('Deleting %s: %s' % (pl.id, pl.name))
            self.writer_client.delete_playlist(pl.id)

    def cleanup_all_generated_playlists(self):
        self.delete_playlists(self.db.get_generated_playlists())

    def generate_playlist(self, playlist_type, playlistConfig):
        generator = PlaylistGenerator(self.config.playlist_prefix, self.timestamp, self.db)
        try:
            generator_results = generator.generate(playlist_type, playlistConfig)
        except PlaylistGeneratorError as e:
            self.logger.error(e)
            return
        self.delete_playlists(generator_results.get_playlists_to_delete())
        playlists_to_create = generator_results.get_playlists_to_create()
        try:
            for pl in playlists_to_create:
                pl.create_in_gpm(self.writer_client)
        except GPMPlGenException as e:
            self.logger.error("Error talking to Google Play Music; attempting to clean-up")
            for pl in playlists_to_create:
                pl.delete_in_gpm(self.writer_client)
            self.logger.debug(e.parent_exception)
            raise e  # FIXME: maybe not?


class GPMPlGenException(Exception):
    def __init__(self, message, parent_exception):
        self.message = message
        self.parent_exception = parent_exception

    def __str__(self):
        logging.getLogger(__name__).debug(self.parent_exception)
        return "%s: %s" % (self.message, self.parent_exception)
