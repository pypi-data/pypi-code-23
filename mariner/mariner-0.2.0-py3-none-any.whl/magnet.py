import logging

from cliff import command
import pyperclip

from mariner.plugins import distrowatch


class Magnet(command.Command):
    """Copy magnet link with given ID to clipboard."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(Magnet, self).get_parser(prog_name)
        parser.add_argument('ID', nargs=1, type=int)
        return parser

    def take_action(self, parsed_args):
        # TODO Remove this ugly hack
        engine = distrowatch.Distrowatch()
        tid = parsed_args.ID[0]
        torrent = engine.get_torrent(tid)
        self.log.debug('tid=%s torrent=%s', tid, torrent)
        if torrent.magnet_link:
            pyperclip.copy(torrent.magnet_link)
            self.log.info(f'Copied {torrent.name} magnet link to clipboard.')
            self.log.debug('magnet=%s', torrent.magnet_link)
        else:
            self.log.warning(
                f'{torrent.name} has no magnet link. Download the torrent.')
