import sys
import logging
from zcli import clargs, zcashcli, saferjson


def main(args=sys.argv[1:]):
    """
    Simplify certain useful tasks on top of the Zcash RPC interface.
    """
    (opts, cmdfunc, cmdkwargs) = clargs.parse_args(main.__doc__, args)
    init_logging(opts['DEBUG'])

    zc = zcashcli.ZcashCLI(opts['DATADIR'])
    result = cmdfunc(zc, **cmdkwargs)

    sys.stdout.write(saferjson.encode_param(result, pretty=True))


def init_logging(debug):
    logging.basicConfig(
        stream=sys.stderr,
        format='%(asctime)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        level=logging.DEBUG if debug else logging.INFO,
    )
