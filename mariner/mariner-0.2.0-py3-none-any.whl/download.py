import logging
import pathlib

from cliff import lister

from mariner import downloader
from mariner.plugins import distrowatch


class Download(lister.Lister):
    """Download torrent with given ID."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('ID', nargs='+', type=int)
        return parser

    def take_action(self, parsed_args):
        # TODO Remove this ugly hack
        engine = distrowatch.Distrowatch()

        torrents = []
        for tid in parsed_args.ID:
            torrent = engine.get_torrent(tid)
            self.log.debug('tid=%s torrent=%s', tid, torrent)
            if torrent.torrent_url:
                torrents.append(torrent)
                self.log.debug('Torrent appended.')
                self.log.info(f'Downloading torrent ID {tid}.')
            else:
                self.log.warning(
                    f'{torrent.name} has no downloadable torrents. Use magnet link.')

        filelist = ((t.torrent_url, t.filename) for t in torrents)
        path = self.app.config['download_path']
        torrent_downloader = downloader.Downloader(download_path=path)
        self.log.debug('filelist=%s download_path=%s', filelist, path)
        torrent_downloader(filelist)

        headers = ('ID', 'Name', 'Saved to')
        columns = ((t.tid, t.name[:60], pathlib.Path(path) / t.filename)
                   for t in torrents)
        return (headers, columns)
