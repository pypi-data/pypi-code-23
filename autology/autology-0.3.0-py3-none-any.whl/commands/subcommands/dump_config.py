"""Sub-command that will dump the current configuration, to include all of the default values."""
import pathlib
from autology.configuration import get_configuration_root, dump_configuration


def register_command(subparser):
    """Register the sub-command with any additional arguments."""
    parser = subparser.add_parser('dump_config', help='Create a new note object.')
    parser.set_defaults(func=_main)

    parser.add_argument('--output', '-o', default='config.yaml', help='File that will store the output.')


def _main(args):
    """
    Dump the current configuration file
    :param args:
    :return:
    """
    output_path = pathlib.Path(args.output)

    if not output_path.is_absolute():
        output_path = get_configuration_root() / output_path

    # Now need to find the templates definition of that zip file and locate it in the file system so that it can be
    dump_configuration(output_path)
