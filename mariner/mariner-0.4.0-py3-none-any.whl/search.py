import logging

from cliff import lister

from mariner import searchengine


class Search(lister.Lister):
    """Search for torrents."""

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument('title', nargs=1)
        parser.add_argument('--limit', '-l', nargs='?', default=10, type=int)
        parser.add_argument('--tracker', '-t', nargs='?',
                            default=self.app.config['default_tracker'])
        return parser

    def take_action(self, parsed_args):
        title = parsed_args.title[0].lower()
        limit = parsed_args.limit
        tracker = parsed_args.tracker.lower()
        self.log.debug('title=%s limit=%s tracker=%s', title, limit, tracker)

        self.log.info(f'Searching for "{title}".')
        engine = searchengine.engines[tracker]()
        torrents = engine.search(title, limit)
        self.log.debug(f'torrents={torrents}')

        headers = ('ID', 'Name', 'Available as')
        columns = ((t.tid, t.name[:80], t.mods) for t in torrents)
        return (headers, columns)
