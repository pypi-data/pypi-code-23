import sys
import os
import argparse
import hashlib
import logging
import json
from bdbag import bdbag_api as bdb
from bdbag import get_typed_exception as gte

logger = logging.getLogger(__name__)


def create_remote_file_manifest(args):
    with open(args.output_file, 'w') as rfm_file:
        rfm = list()
        for dirpath, dirnames, filenames in os.walk(args.input_path):
            subdirs_count = dirnames.__len__()
            if subdirs_count:
                logger.info("%s subdirectories found in input directory %s %s" %
                            (subdirs_count, args.input_path, dirnames))
            filenames.sort()
            for fn in filenames:
                rfm_entry = dict()
                input_file = os.path.join(dirpath, fn)
                logger.debug("Processing input file %s" % input_file)
                input_rel_path = input_file.replace(args.input_path, '')
                filepath = args.base_payload_path if args.base_payload_path else ""
                filepath = "".join([filepath, input_rel_path])
                rfm_entry["filename"] = filepath.replace("\\", "/").lstrip("/")
                rfm_entry["url"] = url_format(args.url_formatter,
                                              base_url=args.base_url,
                                              filepath=input_rel_path.replace("\\", "/").lstrip("/"),
                                              filename=fn)
                rfm_entry["length"] = os.path.getsize(input_file)
                rfm_entry.update(calculate_file_hashes(input_file, args.checksum))
                if args.streaming_json:
                    rfm_file.writelines(''.join([json.dumps(rfm_entry), '\n']))
                else:
                    rfm.append(rfm_entry)
        if not args.streaming_json:
            rfm_file.write(json.dumps(rfm, indent=4))
        logger.info("Successfully created remote file manifest: %s" % args.output_file)


def url_format(formatter, base_url, filepath=None, filename=None):
    url = None
    urlpath = None
    if formatter == "none":
        return base_url
    elif formatter == "append-path":
        urlpath = "/".join([filepath])
    elif formatter == "append-filename":
        urlpath = "/".join([filename])
    else:
        raise RuntimeError("Unknown URL formatter: %s" % formatter)
    if base_url.endswith("/"):
        url = "".join([base_url, urlpath])
    else:
        url = "/".join([base_url, urlpath])
    return url.replace('\\', '/')


# this function was "borrowed" from bagit-python/bagit.py since it has private scope in that module.
def calculate_file_hashes(full_path, hashes):
    f_hashers = dict()
    for alg in hashes:
        try:
            f_hashers[alg] = hashlib.new(alg)
        except ValueError:
            logger.warning("Unable to validate file contents using unknown %s hash algorithm", alg)

    logger.info("Calculating %s checksum(s) for file %s" % (set(f_hashers.keys()), full_path))
    if not os.path.exists(full_path):
        logger.warn("%s does not exist" % full_path)
        return

    try:
        with open(full_path, 'rb') as f:
            while True:
                block = f.read(1048576)
                if not block:
                    break
                for i in f_hashers.values():
                    i.update(block)
    except (IOError, OSError) as e:
        logger.warn("Could not read %s: %s" % (full_path, str(e)))
        raise

    return dict((alg, h.hexdigest()) for alg, h in f_hashers.items())


def parse_cli():
    description = 'Utility routines for working with BDBags'

    parser = argparse.ArgumentParser(
        description=description, epilog="For more information see: http://github.com/ini-bdds/bdbag")

    parser.add_argument(
        '--quiet', action="store_true", help="Suppress logging output.")

    parser.add_argument(
        '--debug', action="store_true", help="Enable debug logging output.")

    subparsers = parser.add_subparsers( dest="subparser", help="sub-command help")
    parser_crfm = \
        subparsers.add_parser('create-rfm',
                              description="Create a remote file manifest by recursively scanning a directory.",
                              help='create-rfm help')

    parser_crfm.add_argument(
        '--input-path', metavar="<path>", required=True,
        help="Path to a directory tree which will be traversed for input files.")

    parser_crfm.add_argument(
        '--output-file', metavar="<path>", required=True,
        help="Path of the filename where the remote file manifest will be written.")

    checksum_arg = parser_crfm.add_argument(
        "--checksum", action='append', required=True, choices=['md5', 'sha1', 'sha256', 'sha512', 'all'],
        help="Checksum algorithm to use: can be specified multiple times with different values. "
             "If \'all\' is specified, every supported checksum will be generated")

    base_payload_path_arg = parser_crfm.add_argument(
        '--base-payload-path', metavar="<url>",
        help="An optional path prefix to prepend to each relative file path found while walking the input directory "
             "tree. All files will be rooted under this base directory path in any bag created from this manifest.")

    base_url_arg = parser_crfm.add_argument(
        '--base-url', metavar="<url>", required=True,
        help="A URL root to prepend to each file listed in the manifest. Can be used to generate fetch URL "
             "fields dynamically.")

    url_map_arg = parser_crfm.add_argument(
        '--url-map-file', metavar="<path>",
        help="Path to a JSON formatted file that maps file relative paths to URLs.")

    url_formatter_arg = parser_crfm.add_argument(
        "--url-formatter", choices=['none', 'append-path', 'append-filename'], default='none',
        help="Format function for generating remote file URLs. "
             "If \'append-path\' is specified, the existing relative path including the filename will be appended to"
             " the %s argument. If \'append-path\' is specified, only the filename will be appended. If \"none\" is "
             "specified, the %s argument will be used as-is." %
             (base_url_arg.option_strings, base_url_arg.option_strings))

    streaming_json_arg = parser_crfm.add_argument(
        "--streaming-json", action='store_true', default=False,
        help=str("If \'streaming-json\' is specified, one JSON tuple object per line will be output to the output file."
                 "Enable this option if the default behavior produces a file that is prohibitively large to parse "
                 "entirely into system memory."))

    parser_crfm.set_defaults(func=create_remote_file_manifest)

    args = parser.parse_args()

    bdb.configure_logging(level=logging.ERROR if args.quiet else (logging.DEBUG if args.debug else logging.INFO))

    return args, parser


def main():

    sys.stderr.write('\n')
    args, parser = parse_cli()
    error = None
    result = 0

    try:
        if args.subparser is None:
            parser.print_usage()
        else:
            args.func(args)
    except Exception as e:
        result = 1
        error = "Error: %s" % gte(e)

    finally:
        if result != 0:
            sys.stderr.write("\n%s" % error)

    sys.stderr.write('\n')

    return result


if __name__ == '__main__':
    sys.exit(main())


