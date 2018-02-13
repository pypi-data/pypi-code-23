import yaml
import logging
import sys

class Config:
    DEFAULT_PREFIX = '[PG]'

    def __init__(self):
        self.username = None
        self.password = None
        self.playlist_prefix = self.DEFAULT_PREFIX
        self.log_level = logging.INFO
        self.library_cache = None
        self.db_cache = None
        self.force = False
        self.dry_run = False
        self.delete_all_playlists = False
        self.playlists = []
        self.dev_db_operation = None
        self.client_id = None

    def fromYaml(self, path):
        cfg = yaml.safe_load(path)
        self.username = cfg['auth']['user']
        self.password = cfg['auth']['passwd']
        self.playlist_prefix = cfg['prefix']
        self.playlists = cfg['playlists']
        try:
            self.client_id = cfg['client_id']
        except KeyError:
            pass

    def fromCli(self, args):
        self.force = args.force
        self.dry_run = args.dry_run
        self.delete_all_playlists = args.delete_all_playlists
        if args.write_to_db and args.db_path is None:
            logging.fatal('Invalid --write-to-db use without a --db-path')
            sys.exit(1)
        self.local_db = args.db_path
        self.write_to_db = args.write_to_db
        if args.debug:
            self.log_level = logging.DEBUG
