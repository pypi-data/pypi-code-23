from argparse import ArgumentParser, Namespace
import logging
import logging.handlers
from os import unlink, getpid
from os.path import basename
import sys

from purge_old_files import filters, age, finder


LOGGER = logging.getLogger(__name__)
DEFAULT_MESSAGE_FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s %(message)s'
SYSLOG_MESSAGE_FORMAT = '{name}[{pid}]: %(message)s'.format(
    name=basename(sys.argv[0]), pid=getpid())
DEFAULT_DATE_FORMAT = '%Y/%m/%d %H:%M:%S'


def parse_arguments(argv=None):
    """Parse command line arguments.
    """
    parser = ArgumentParser()

    log_level_parser = parser.add_mutually_exclusive_group()
    log_level_parser.add_argument(
        '--debug', '-D', dest='log_level', action='store_const',
        const=logging.DEBUG, help='Show debug messages')
    log_level_parser.add_argument(
        '--quiet', '-q', dest='log_level', action='store_const',
        const=logging.WARNING, help='Only show warning messages')

    parser.add_argument(
        '--syslog', '-s', action='store_true', default=False,
        help='Send log messages to /dev/log instead of stdout')
    parser.add_argument(
        '--dry-run', '-d', action='store_true', default=False,
        help='Show which files should be deleted')
    parser.add_argument(
        '--include', '-i', metavar='PATTERN', dest='filters', action='append',
        type=filters.glob, help='Include only files matching pattern')
    parser.add_argument(
        '--exclude', '-e', metavar='PATTERN', dest='filters', action='append',
        type=lambda x: filters.negate(filters.glob(x)),
        help='Exclude files matching pattern')
    parser.add_argument(
        'filters', metavar='MIN_AGE', action='append',
        type=lambda x: filters.age(age.parse(x)),
        help='Minimum age of files')
    parser.add_argument(
        'directory', metavar='DIRECTORY', help='Directory to be scanned')

    # Create a namespace and set the default log_level
    namespace = Namespace(log_level=logging.INFO)

    return parser.parse_args(argv, namespace)


def configure_logging(level, use_syslog=False, stream=sys.stdout):
    """Configure logging.
    """
    if use_syslog:
        message_format = SYSLOG_MESSAGE_FORMAT
        date_format = None
        handler = logging.handlers.SysLogHandler('/dev/log')
    else:
        message_format = DEFAULT_MESSAGE_FORMAT
        date_format = DEFAULT_DATE_FORMAT
        # XXX: Looks like a pylint bug, because both SysLogHandler and
        # StreamHandler inherit from Logger.
        handler = logging.StreamHandler(stream)  # pylint: disable=R0204

    formatter = logging.Formatter(message_format, date_format)
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)


def main(argv=None):
    """Command line entry point.
    """
    arguments = parse_arguments(argv)
    configure_logging(arguments.log_level, arguments.syslog)

    files = finder.find(arguments.directory, arguments.filters)

    for file_ in files:
        if arguments.dry_run:
            LOGGER.info('To be deleted: %s', file_)
        else:
            LOGGER.info('Deleting: %s', file_)
            unlink(file_.path)

    if arguments.dry_run:
        LOGGER.info('%s files to be deleted', len(files))
    else:
        LOGGER.info('Deleted %s files', len(files))
