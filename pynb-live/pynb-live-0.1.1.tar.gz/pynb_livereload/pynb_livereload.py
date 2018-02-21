from livereload import Server

from livereload.watcher import Watcher

import logging
import argparse

import os
import sys
from pynb.notebook import Notebook


def build_notebook(build_dir, path):
    try:

        logging.info('Compiling {}'.format(os.path.basename(path)))
        nb = Notebook()
        from collections import namedtuple
        # Hacking a bit pynb
        NbTuple = namedtuple('Test', ['export_html', 'disable_footer', 'cells', 'log_level',
                                      'import_ipynb', 'export_pynb', 'param', 'disable_cache',
                                      'ignore_cache', 'no_exec', 'export_ipynb'])

        export_name = os.path.basename(path).split('.')[0]
        nb.args = NbTuple(export_html="{}/{}.html".format(build_dir, export_name),
                          disable_footer=True,
                          import_ipynb=False,
                          export_pynb=False,
                          param=None,
                          disable_cache=False,
                          ignore_cache=False,
                          export_ipynb=False,
                          no_exec=False,
                          cells='{}:cells'.format(path),
                          log_level='INFO')
        nb.run()
    except Exception as exp:
        logging.exception(exp)


class PyNBLiveReload:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Stuff')
        self.args = None

        pass

    def run(self):

        if not self.args:
            self.parse_args()

        server = Server(watcher=Watcher(provide_filename=True))

        from functools import partial

        build_partial = partial(build_notebook, self.args.build_path)

        server.watch('{}/*.py'.format(self.args.watch_path), build_partial)
        server.serve(root=self.args.build_path, liveport=self.args.lr_port, restart_delay=1, open_url_delay=1)

    def add_argument(self, *args, **kwargs):
        """
        Add application argument
        :param args: see parser.add_argument
        :param kwargs: see parser.add_argument
        :return:
        """
        self.parser.add_argument(*args, **kwargs)

    def parse_args(self):
        self.add_argument('--watch_path', help='Where the pynb files are residing', default='notebooks')
        self.add_argument('--build_path', help='Where the output files should be going', default='notebooks_build')
        self.add_argument('--lr_port', help='Port for the livereload server', default=35729)

        if len(sys.argv) == 1 and self.__class__ == Notebook:
            # no parameters and Notebook class not extended:
            # print help and exit.
            self.parser.print_help()
            print()
            sys.exit(1)

        self.args = self.parser.parse_args()


def main():
    """
    Entry point for cli
    :return:
    """

    nb_live = PyNBLiveReload()
    nb_live.run()


if __name__ == "__main__":
    main()
