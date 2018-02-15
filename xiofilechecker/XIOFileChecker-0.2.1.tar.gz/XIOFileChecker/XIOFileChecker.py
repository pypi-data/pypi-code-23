#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    :platform: Unix
    :synopsis: Tool to compare filedef produces by dr2xml with outfile file from XIOS.

"""

import logging
import os
import re
import sys
from copy import deepcopy as copy
from xml.etree.ElementTree import parse

from handler import Filename
from utils.constants import *
from utils.custom_exceptions import *
from utils.misc import _ArgumentParser, MultilineFormatter, DirectoryChecker, init_logging, keyval_converter

__version__ = 'v{} {}'.format(VERSION, VERSION_DATE)


def get_args():
    """
    Returns parsed command-line arguments.

    :returns: The argument parser
    :rtype: *argparse.Namespace*

    """
    parser = _ArgumentParser(
        prog='XIOFileChecker',
        description=PROGRAM_DESC,
        formatter_class=MultilineFormatter,
        add_help=False,
        epilog=EPILOG)
    parser._optionals.title = OPTIONAL
    parser._positionals.title = POSITIONAL
    parser.add_argument(
        '-h', '--help',
        action='help',
        help=HELP)
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='%(prog)s ({})'.format(__version__),
        help=VERSION_HELP)
    parser.add_argument(
        '--log',
        metavar='CWD',
        type=str,
        const='{}/logs'.format(os.getcwd()),
        nargs='?',
        help=LOG_HELP)
    parser.add_argument(
        '--debug',
        action='store_true',
        default=False,
        help=DEBUG_HELP)
    parser.add_argument(
        '--show-common',
        action='store_true',
        default=False,
        help=SHOW_COMMON_HELP)
    parser.add_argument(
        '--display-all',
        action='store_true',
        default=False,
        help=DISPLAY_ALL_HELP)
    parser.add_argument(
        'directory',
        action=DirectoryChecker,
        help=DIRECTORY_HELP)
    parser.add_argument(
        '--filedef',
        action=DirectoryChecker,
        help=FILEDEF_HELP)
    parser.add_argument(
        '--set-filter',
        metavar='FACET_KEY=REGEX',
        type=keyval_converter,
        action='append',
        help=SET_FILTER_HELP)

    return parser.parse_args()


def get_patterns_from_files(path, filters):
    """
    Yields all non-hidden NetCDF file into the directory recursively scan.
    Each filename pattern is deserialized as a dictionary of facet: value.

    :param str path: The path to scan
    :param dict filters: The facet filters
    :returns: The filename deserialized with facets
    :rtype: *dict*

    """
    for root, _, filenames in os.walk(path, followlinks=True):
        for filename in filenames:
            if os.path.isfile(os.path.join(root, filename)) and re.search('^.*\.nc$', filename):
                logging.debug('DEBUG :: process netCDF file :: {}'.format(filename))
                fn = Filename(filename, filters)
                if fn.in_scope():
                    yield fn


def get_patterns_from_filedef(path, filters):
    """
    Yields all file definition produced by dr2xml as input for XIOS.
    Each filename pattern is deserialized as a dictionary of facet: value.

    :param str path: The path to scan
    :param dict filters: The facet filters
    :returns: The filename deserialized with facets
    :rtype: *dict*

    """
    for root, _, filenames in os.walk(path, followlinks=True):
        for filename in filenames:
            ffp = os.path.join(root, filename)
            if os.path.isfile(ffp) and re.search('^dr2xml_.*\.xml$', filename):
                logging.debug('DEBUG :: parse XML filedef :: {}'.format(ffp))
                xml_tree = parse(ffp)
                for item in xml_tree.iterfind('*/file'):
                    # Get XML file_id entry name
                    item = os.path.basename(item.attrib['name'].strip())
                    # Ignore "cfsites_grid" entry
                    if item == 'cfsites_grid':
                        continue
                    logging.debug('DEBUG :: process XML file_id entry :: {}'.format(item))
                    fn = Filename(item, filters)
                    if fn.in_scope():
                        yield fn


def tupleized(facets, filenames):
    """
    Returns the filename patterns as a set of tuples

    :param list filenames: The list of deserialized filenames dictionaries
    :param dict facets: The facet dictionary
    :returns: The filename patterns tupleized
    :rtype: *set*

    """
    patterns = list()
    for filename in filenames:
        assert len(filename) == len(facets)
        x = list()
        for i in sorted(facets.values()):
            facet = facets.keys()[facets.values().index(i)]
            if facet not in IGNORED_FACETS:
                x.append(filename[facet])
        patterns.append(tuple(x))
    return set(patterns)


def get_labels(facets):
    """
    Returns the labels of table columns to display results

    :param dict facets: The facet dictionary
    :returns: The title labels
    :rtype: *list*

    """
    labels = list()
    for i in sorted(facets.values()):
        facet = facets.keys()[facets.values().index(i)]
        if facet not in IGNORED_FACETS:
            labels.append(facet)
    return labels


def get_widths(labels, fields):
    """
    Returns the column widths to display results

    :param list labels: The list of labels
    :param list fields: The list of entries
    :returns: The list of widths
    :rtype: *list*

    """
    widths = list()
    fields = list(fields)
    fields.append(tuple(labels))
    li = zip(*fields)
    for i in range(len(li)):
        widths.append(len(max(li[i], key=len)) + 2)
    return widths


def align(fields, widths, sep='| '):
    """
    Returns line with alignment.

    :param list fields: The list of fields to align
    :param list widths:  The list of width for each field
    :param list or str sep: The column separators
    :returns: The formatted line
    :rtype: *str*

    """
    assert len(fields) == len(widths)
    line = list()
    for field in fields:
        line.append(field.ljust(widths[fields.index(field)]))
    if isinstance(sep, list):
        assert len(sep) == (len(line) - 1)
        for i in range(len(line) - 2, -1, -1):
            line.insert(i + 1, sep[i])
        return ''.join(line)
    else:
        return sep.join(line)


def run():
    """
    Run main program

    """
    # Get command-line arguments
    args = get_args()
    # Set file definition path depending on arguments
    setattr(args, 'filedef', args.filedef or args.directory)
    # Initialize logger depending on log and debug mode
    init_logging(log=args.log, debug=args.debug)
    # Get facet keys
    facets = re.compile(CMIP6_FILENAME_PATTERN).groupindex
    for facet in IGNORED_FACETS:
        del(facets[facet])
    # Clear re.compile cache to avoid groupindex deletion
    re.purge()
    # Get filters
    setattr(args, 'set_filter', args.set_filter or tuple())
    filters = dict(args.set_filter)
    wrong_filters = set(filters.keys()).difference(set(facets.keys()))
    if wrong_filters:
        raise InvalidFilters(wrong_filters, facets)
    # Collecting data
    logging.info("Collecting data, please wait...\r")
    xios_input = list(get_patterns_from_filedef(args.filedef, filters))
    if not xios_input:
        raise NoPatternFound()
    xios_output = list(get_patterns_from_files(args.directory, filters))
    if not xios_output:
        raise NoFileFound()
    # Remove unchanged facet among all entries for better display
    if not args.display_all:
        xios_all = [x.get_attrs().values() for x in xios_input]
        xios_all.extend([x.get_attrs().values() for x in xios_output])
        fn_facets = xios_input[0].get_attrs()
        hidden_facets = [fn_facets.keys()[fn_facets.values().index(i[0])] for i in zip(*xios_all) if len(set(i)) == 1]
        for facet in hidden_facets:
            del (facets[facet])
        xios_input = tupleized(facets, [x.mask(hidden_facets) for x in xios_input])
        xios_output = tupleized(facets, [x.mask(hidden_facets) for x in xios_output])
    else:
        xios_input = tupleized(facets, [x.get_attrs() for x in xios_input])
        xios_output = tupleized(facets, [x.get_attrs() for x in xios_output])
    # Run comparison between input and output
    # What is in input AND in output
    common = xios_input.intersection(xios_output)
    # What is in input BUT NOT in output
    missing_output = xios_input.difference(xios_output)
    # What is in output BUT NOT in input
    missing_input = xios_output.difference(xios_input)
    # Build table title
    labels = get_labels(facets)
    # Build table width
    widths = get_widths(labels, xios_input.union(xios_output))
    # Add labels for results
    labels.extend([DR2XML_LABEL, XIOS_LABEL])
    widths.extend([DR2XML_WIDTH, XIOS_WIDTH])
    # Table separators
    separators = ['| '] * (len(facets) - 1)
    separators += ['|| ', '| ']
    # Get total width for display
    total_width = len(align(labels, widths, sep=separators)) + 1
    # Print table header
    logging.info('+' + ''.center(total_width, '=') + '+')
    logging.info('| ' + align(labels, widths, sep=separators) + '|')
    logging.info('+' + ''.center(total_width, '-') + '+')
    # Print results for each entry
    lines = 0
    input_total = 0
    output_total = 0
    for tup in sorted(xios_input.union(xios_output)):
        line = list(tup)
        if tup in common:
            if args.show_common:
                line.extend(['X', 'X'])
                input_total += 1
                output_total += 1
            else:
                continue
        elif tup in missing_input:
            line.extend(['', 'X'])
            output_total += 1
        elif tup in missing_output:
            line.extend(['X', ''])
            input_total += 1
        else:
            line.extend(['', ''])
        lines += 1
        logging.info('| ' + align(line, widths, sep=separators) + '|')
    # Print table footer with totals
    logging.info('+' + ''.center(total_width, '-') + '+')
    line = align(fields=['Totals = {}'.format(lines), str(input_total), str(output_total)],
                 widths=[len(align(labels[:-2], widths[:-2])), widths[-2], widths[-1]],
                 sep=['|| ', '| '])
    logging.info('| ' + line + '|')
    logging.info('+' + ''.center(total_width, '=') + '+')


if __name__ == "__main__":
    # PyCharm workaround
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    run()
