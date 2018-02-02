from inspector import run_inspector
import sys
from os import getenv, path
from user_exception import UserException as Ux
from yaml import load, Loader
import platform
import argparse
import six
parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description='  helper for writing Appium locators to test Android applications')


def start_inspector():
    # default is to use temporary directory for:
    #   inspector.png - screenshot
    #   inspector.xml - xml dump of display elements
    #   inspector.csv - conversion of xml xpaths to zpaths, element info in csv format
    #   inspector_locators.json - history of locators used to find elements from inspector
    # temporary directory is set by mtaf-inspector command line argument "tmp_dir=<path>", if it exists;
    # else, the value of environment variable "MTAF_TMP_DIR", if it exists;
    # else, platform-dependent temporary directory is used:
    #    Linux - /tmp
    #    Windows - os.getenv('TMP')
    #    Darwin - /tmp
    #
    # note: log directory is set in mtaf_logging module from MTAF_LOG_DIR environment variable, defaults to ./log
    parser.add_argument('-c', '--config_file', type=str, default='./inspector_config.yml',
                        help='YAML configuration file (default "./config.yml")')
    parser.add_argument('-p', '--plugin_dir', type=str, default='.',
                        help='plugin directory (default="." or set in configuration file)')
    parser.add_argument('opts', type=str, nargs='*', metavar='key=value',
                        help='key=value pairs will be added to configuration')
    parser.add_argument('-s', '--show_config_only', action='store_true',
                        help='show configuration without calling run_inspector')
    parser.add_argument('-l', '--log_window_height', default=10,
                        help='text height of standard output and recorded output windows')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='print debug messages')
    args = parser.parse_args()
    if args.debug:
        six.print_("config_file = %s" % args.config_file)
    system = platform.system()
    if system in ['Darwin', 'Linux']:
        default_tmp_dir = path.join('/tmp', 'MtafInspector')
    elif system == 'Windows':
        default_tmp_dir = path.join(getenv('TMP'), 'MtafInspector')
    else:
        raise Ux('Unknown system type %s' % system)
    if args.debug:
        six.print_("tmp_dir = %s" % default_tmp_dir)
    cfg = {
        'tmp_dir': default_tmp_dir,
        'plugin_dir': args.plugin_dir,
        'log_window_height': args.log_window_height}
    # if args.config_file is the path of a YAML configuration file, update
    # configuration to the default
    try:
        with open(args.config_file) as f:
            cfg2 = load(f, Loader=Loader)
        cfg.update(cfg2)
    except IOError:
        pass
    progname = path.basename(sys.argv[0])
    for arg in args.opts:
        terms = arg.split('=')
        if len(terms) != 2:
            raise Ux("arguments to %s must be of the form <key>=<value>, with no spaces" % progname)
        cfg[terms[0]] = terms[1]
    if args.debug or args.show_config_only:
            six.print_(repr(cfg))
    if not args.show_config_only:
        run_inspector(cfg)
