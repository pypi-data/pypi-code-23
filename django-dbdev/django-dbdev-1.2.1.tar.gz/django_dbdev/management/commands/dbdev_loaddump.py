from django.core.management import call_command

from ._base import BaseDbdevCommand


class Command(BaseDbdevCommand):
    help = 'Load a database dump.'
    args = '<dumpfile>'

    def add_extra_arguments(self, parser):
        parser.add_argument('dumpfile')

    def dbdev_handle(self):
        if not self.options.get('dumpfile'):
            self.stderr.write('Dumpfile is required. See --help.')
            raise SystemExit()
        dumpfile = self.options.get('dumpfile')
        self.dbdev_backend.load_dbdump(dumpfile)
