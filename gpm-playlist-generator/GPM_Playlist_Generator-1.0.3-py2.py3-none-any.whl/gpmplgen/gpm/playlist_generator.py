import datetime
import logging

from . import *
from gpmplgen.db import *


class PlaylistGeneratorResults:
    def __init__(self, delete_playlists, new_playlists):
        self._to_delete = delete_playlists
        self._to_create = new_playlists

    def get_playlists_to_delete(self):
        return self._to_delete

    def get_playlists_to_create(self):
        return self._to_create


class PlaylistGenerator:
    MONTHLY_ADDED = 'monthly_added'
    MOST_PLAYED = 'most_played'

    def __init__(self, playlist_prefix, timestamp, library_db):
        self.logger = logging.getLogger(__name__)
        self.playlist_prefix = playlist_prefix
        self.timestamp = timestamp
        self.library_db = library_db

    def generate(self, playlist_type, config):
        method_name = "_gen_" + playlist_type
        self.logger.debug("Generating playlists with %s" % method_name)
        try:
            gen_func = getattr(self, method_name)
        except AttributeError:
            raise PlaylistGeneratorError("Unsupported playlist type '%s'" % playlist_type)
        return gen_func(config)

    def full_playlist_name(self, name):
        if self.playlist_prefix is not None and len(self.playlist_prefix) > 0:
            return self.playlist_prefix + ' ' + name
        else:
            return name

    @staticmethod
    def _gen_yearmonth(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m')

    @staticmethod
    def _is_yearmonth_old(current, tested):
        return tested < current

    def _gen_monthly_added(self, config):
        self.logger.debug("Generating monthly added playlists")
        songs_by_month = {}
        ignored_months = {}
        current_yearmonth = self._gen_yearmonth(self.timestamp)
        dbplaylist_cache = DbPlaylistCache()
        delete_playlists = []
        new_playlists = []
        exclude_before = None
        if config is not None and "exclude" in config:
            if "before" in config["exclude"]:
                exclude_before = config["exclude"]["before"]
        for track in self.library_db.get_tracks("ORDER BY creationTimestamp, discNumber, trackNumber"):
            # Group by year & month
            created_time_ms = track.creationTimestamp
            created_time = created_time_ms / (10 ** 6)
            created_yearmonth = self._gen_yearmonth(created_time)
            # Check if we should exclude any tracks
            if exclude_before and created_yearmonth < exclude_before:
                ignored_months[created_yearmonth] = 1;
                continue
            pl_type = self.MONTHLY_ADDED
            pl_args = created_yearmonth
            current_playlists_final = dbplaylist_cache.are_final_check(pl_type, pl_args)
            if current_playlists_final is None:
                existing_playlists = \
                    self.library_db.get_generated_playlists("WHERE type='%s' AND args='%s'" % (pl_type, pl_args))
                current_playlists_final = dbplaylist_cache.are_final(pl_type, pl_args, existing_playlists)
                if not current_playlists_final:
                    delete_playlists += existing_playlists
                else:
                    self.logger.info('Skipping %s:%s' % (pl_type, pl_args))
            if current_playlists_final:
                continue
            if not created_yearmonth in songs_by_month:
                pl = Playlist(self.full_playlist_name('Added in ' + created_yearmonth), self.timestamp)
                pl.set_type(pl_type)
                pl.set_args(pl_args)
                pl.set_final(self._is_yearmonth_old(current_yearmonth, created_yearmonth))
                songs_by_month[created_yearmonth] = pl
            songs_by_month[created_yearmonth].add_track(track.id)
        if len(ignored_months) > 0:
            self.logger.info("Skipping tracks added in %s " % (", ".join(sorted(ignored_months.keys()))))
        for m in sorted(songs_by_month.keys()):
            pl = songs_by_month[m]
            for p in pl.get_ingestable_playlists():
                new_playlists.append(p)
        return PlaylistGeneratorResults(delete_playlists, new_playlists)

    def _gen_most_played(self, config):
        self.logger.debug("Generating most played playlist")
        if config is not None and 'limit' in config:
            limit = min(int(config['limit']), Playlist.PLAYLIST_MAX)
        else:
            limit = Playlist.PLAYLIST_MAX
        self.logger.debug("Most played limit: %d" % limit)
        delete_playlists = self.library_db.get_generated_playlists("WHERE type='%s'" % (self.MOST_PLAYED))
        playlist = Playlist(self.full_playlist_name('Most played'), self.timestamp)
        playlist.set_type(self.MOST_PLAYED)
        for track in self.library_db.get_tracks("ORDER BY playCount DESC, recentTimestamp DESC LIMIT %d" % limit,
                                                self.library_db.ALLTRACKS_TABLE):
            playlist.add_track(track.id)
        return PlaylistGeneratorResults(delete_playlists, [playlist])

class PlaylistGeneratorError(Exception):
    pass
