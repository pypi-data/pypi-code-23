#!/usr/bin/python

"""
Author: Yuri <yuri@algoseek.com>
Date: 22.06.2017
Title: QuantGo CLI
Description: CLI wrapper around QuantGo API
"""

import re
import csv
import sys
import json
import argparse

from . import qgservice
from .qgapi import QuantGoApi

from datetime import datetime

# Display help on error
class CliParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('Error: %s\n' % message)
        #self.print_help()
        sys.exit(2)

# Custom formatter for command line arguments help
class Formatter(argparse.HelpFormatter):
    def _format_action_invocation(self, action):
        if not action.option_strings:
            metavar, = self._metavar_formatter(action, action.dest)(1)
            return metavar

        else:
            parts = []

            # if the Optional doesn't take a value, format is:
            #    -s, --long
            if action.nargs == 0:
                parts.extend(action.option_strings)

            # if the Optional takes a value, format is:
            #    -s ARGS, --long ARGS
            else:
                for option_string in action.option_strings:
                    parts.append(option_string)

            return ', '.join(parts)
    
    def _format_action(self, action):
        # determine the required width and the entry label
        help_position = min(self._action_max_length + 2,
                            self._max_help_position)
        help_width = self._width - help_position
        action_width = help_position - self._current_indent - 2
        action_header = self._format_action_invocation(action)
        
        hlp = action.help
        
        if action.required:
            choices = ', '.join(action.choices)
            hlp = '%s, valid are: %s' % (action.help, choices)
            action_header = action.dest
        else:
            action.dest = ''

        # ho nelp; start on same line and add a final newline
        if not hlp:
            tup = self._current_indent, '', action_header
            action_header = '%*s%s\n' % tup

        # short action name; start on the same line and pad two spaces
        elif len(action_header) <= action_width:
            tup = self._current_indent, '', action_width, action_header
            action_header = '%*s%-*s  ' % tup
            indent_first = 0

        # long action name; start on the next line
        else:
            tup = self._current_indent, '', action_header
            action_header = '%*s%s\n' % tup
            indent_first = help_position

        # collect the pieces of the action help
        parts = [action_header]

        # if there was help for the action, add lines of help text
        if hlp:
            help_text = hlp
            help_lines = self._split_lines(help_text, help_width)
            parts.append('%*s%s\n' % (indent_first, '', help_lines[0]))
            for line in help_lines[1:]:
                parts.append('%*s%s\n' % (help_position, '', line))

        # or add a newline if the description doesn't end with one
        elif not action_header.endswith('\n'):
            parts.append('\n')

        # if there are any sub-actions, add their help as well
        for subaction in self._iter_indented_subactions(action):
            parts.append(self._format_action(subaction))

        # return a single string
        return self._join_parts(parts)
    
    def _format_usage(self, usage, actions, groups, prefix):
        examples = '\n'.join(['  qg_cli get_symbols EQUITIES_TAQ --date 20090420   # get list of equities symbol',
                              '  qg_cli download FUTURES_TAQ --date 20090420 --symbol ESM0 --path "D:/qgdown"   # download single future',
                              '  qg_cli get_futures_by_base FUTURES_TAQ --date 20170315 --base ES   # get list of contracts for base future'])
        documentation = "API Documentation:\n  https://www.quantgo.com/documentation/QuantGo%20API/QuantGoApi.pdf\nCLI Documentation:\n  https://www.quantgo.com/documentation/QuantGo%20API/QuantGoCli.pdf"
        return 'Usage: qg_cli action service [optional parameters]\nExamples:\n%s\n\n%s\n\n' % (examples, documentation)

# print help and exit
def on_help_error(message):
    sys.stderr.write('Error: %s\n' % message)
    parser.print_help()
    sys.exit(2)

# print error and exit
def on_error(message):
    sys.stderr.write('Error: %s\n' % message)
    #parser.print_help()
    sys.exit(2)

# list available services from qgservice.py
def list_services():
    attrs = qgservice.__dict__
    res = []
    for attr in attrs:
        attrv = getattr(qgservice, attr)
        if type(attrv) is dict and 'bucket' in attrv:
            res.append(attr)
    return sorted(res)

# convert service name into service object (qgservice.py)
def get_service(service_name):
    if service_name in list_services():
        return getattr(qgservice, service_name)
    return None

# check if parameter was passed to script
def validate(args, pname):
    if not hasattr(args, pname) or getattr(args, pname) is None:
        raise Exception('Parameter "%s" not found' % (pname))

# read file. one record per line. used to read dates and symbols
def read_file(fname):
    with open(fname) as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return content

# read record to download. one record per line. format: date, symbol
def read_records(fname):
    records = []
    with open(fname, "rb") as csvfile:
        datareader = csv.reader(csvfile, skipinitialspace=True)
        for row in datareader:
            records.append((row[0], row[1]))
    return records

actions = ['get_index','list_range_trade_dates','list_years','list_trade_dates','list_all_trade_dates','get_symbols_index','get_symbols','get_base_futures','get_futures_by_base','is_valid_symbol','is_valid_base_future','list_trade_date_symbols','download','download_base','download_records','download_records_bases']

# command line arguments parser
#parser = argparse.ArgumentParser(description='QuantGo CLI', formatter_class=Formatter)
parser = CliParser(description='QuantGo CLI', formatter_class=Formatter, add_help=False)
parser._optionals.title = 'Optional parameters'
parser._positionals.title = 'Required parameters'

#parser = CliParser(description='QuantGo CLI', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('action', nargs=1, help='Action', choices=actions)
parser.add_argument('service', nargs=1, help='QuantGo service name', choices=list_services())

parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')

parser.add_argument('-ak', '--access_key', action='store', dest='access_key', help='Access key')
parser.add_argument('-sk', '--secret_key', action='store', dest='secret_key', help='Secret key')
parser.add_argument('-pr', '--profile', action='store', dest='profile_name', help='AWS Configuration profile name')

parser.add_argument('-y', '--year', action='store', dest='year', help='Year. YYYY format')

date_group = parser.add_mutually_exclusive_group()
date_group.add_argument('-d', '--date', action='store', dest='date', help='Date. YYYYMMDD format')
date_group.add_argument('-dr', '--date_range', action='store', dest='date_range', help='Dates range. YYYYMMDD-YYYYMMDD format')
date_group.add_argument('-dl', '--date_list', action='store', dest='date_list', help='Dates list, comma or space separated. YYYYMMDD format')
date_group.add_argument('-df', '--date_file', action='store', dest='date_file', help='Dates file, one date per line. YYYYMMDD format')

base_group = parser.add_mutually_exclusive_group()
base_group.add_argument('-b', '--base', action='store', dest='base', help='Base future')
base_group.add_argument('-bl', '--base_list', action='store', dest='base_list', help='Base futures list, comma or space separated')
base_group.add_argument('-bf', '--base_file', action='store', dest='base_file', help='Base futures file, one symbol per line')

sym_group = parser.add_mutually_exclusive_group()
sym_group.add_argument('-s', '--symbol', action='store', dest='symbol', help='Symbol')
sym_group.add_argument('-sl', '--symbol_list', action='store', dest='symbol_list', help='Symbols list, comma or space separated')
sym_group.add_argument('-sf', '--symbol_file', action='store', dest='symbol_file', help='Symbols file, one symbol per line')

parser.add_argument('-r', '--records', action='store', dest='records', help='File with records to download. One line per record, format: date,symbol')
parser.add_argument('-u', '--uncompress', dest='uncompress', action='store_true', help='Uncompress downloaded data if parameter passed')
parser.add_argument('-t', '--threads', action='store', default=1, type=int, dest='threads', help='Number of threads to download data. Default: 1')
parser.add_argument('-p', '--path', action='store', dest='path', help='Output directory for data download')
parser.add_argument('-f', '--format', action='store', dest='format', help='Data download mask. Default is %%(path)s/%%(year)s/%%(date)s/%%(base)s/%%(file)s')

parser.add_argument('-v', '--debug', dest='debug', action='store_true', help='Enable debug mode (API will print downloaded files to console) if parameter passed')

def main(args):
    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(2)
    args = parser.parse_args(args)
    
    # initialize local variables from command line arguments
    action = args.action[0].lower()
    service_name = args.service[0]
    service = get_service(service_name.upper())
    
    access_key = args.access_key
    secret_key = args.secret_key
    profile_name = args.profile_name
    
    year = args.year
    
    dates = None
    date = args.date
    date_range = args.date_range
    date_list = args.date_list
    date_file = args.date_file
    
    symbols = None
    symbol = args.symbol
    symbol_list = args.symbol_list
    symbol_file = args.symbol_file
    
    bases = None
    base = args.base
    base_list = args.base_list
    base_file = args.base_file
    
    uncompress = args.uncompress
    num_threads = args.threads
    store_path = args.path
    store_format = args.format
    
    debug = args.debug
    
    records = None
    records_file = args.records
    
    if not service:
        on_error('Unknown service "%s"' % (service_name))
    
    qg = QuantGoApi(access_key, secret_key, profile_name)
    qg.set_default_service(service)
    qg.set_debug(debug)
    
    result = None
    try:
        #read records from file
        if records_file is not None:
            records = read_records(records_file)
        
        # validate date
        if date is not None:
            datetime.strptime(date, '%Y%m%d')
            dates = [date]
        if date_range is not None:
            dates_arr = [s.strip() for s in re.split(r"-", date_range)]
            if len(dates_arr) != 2:
                raise Exception('Use YYYYMMDD-YYYYMMDD format for date range')
            datetime.strptime(dates_arr[0], '%Y%m%d')
            datetime.strptime(dates_arr[1], '%Y%m%d')
            dates = qg.list_range_trade_dates(dates_arr[0], dates_arr[1])
        if date_list is not None:
            dates = [s.strip() for s in re.split(r"\s+|\s*,\s*|\s+", date_list)]
        if date_file is not None:
            dates = read_file(date_file)
        
        # validate symbol
        if symbol is not None:
            symbols = [symbol]
        if symbol_list is not None:
            symbols = [s.strip() for s in re.split(r"\s+|\s*,\s*|\s+", symbol_list)]
        if symbol_file is not None:
            symbols = read_file(symbol_file)
        
        # validate base futures
        if base is not None:
            bases = [base]
        if base_list is not None:
            bases = [s.strip() for s in re.split(r"\s+|\s*,\s*|\s+", base_list)]
        if base_file is not None:
            bases = read_file(base_file)
        
        if action == 'get_index':
            result = qg.get_index()
        elif action == 'list_range_trade_dates':
            validate(args, 'date_range')
            # date range was already converted to list of dates
            result = dates
        elif action == 'list_years':
            result = qg.list_years()
        elif action == 'list_trade_dates':
            validate(args, 'year')
            result = qg.list_trade_dates(year)
        elif action == 'list_all_trade_dates':
            result = qg.list_all_trade_dates()
        elif action == 'get_symbols_index':
            validate(args, 'date')
            result = qg.get_symbols_index(date)
        elif action == 'get_symbols':
            validate(args, 'date')
            result = qg.get_symbols(date)
        elif action == 'get_base_futures':
            validate(args, 'date')
            result = qg.get_base_futures(date)
        elif action == 'get_futures_by_base':
            validate(args, 'date')
            validate(args, 'base')
            result = qg.get_futures_by_base(date, base)
        elif action == 'is_valid_symbol':
            validate(args, 'date')
            validate(args, 'symbol')
            result = qg.is_valid_symbol(date, symbol)
        elif action == 'is_valid_base_future':
            validate(args, 'date')
            validate(args, 'base')
            result = qg.is_valid_base_future(date, base)
        elif action == 'list_trade_date_symbols':
            validate(args, 'date')
            result = qg.list_trade_date_symbols(date)
        elif action == 'download':
            if not symbols: raise Exception('Symbol(s) not specified')
            if not dates: raise Exception('Date(s) not specified')
            validate(args, 'path')
            result = qg.download_symbols(dates, symbols, store_path, num_threads, uncompress, store_format)
        elif action == 'download_base':
            if not bases: raise Exception('Base future(s) not specified')
            if not dates: raise Exception('Date(s) not specified')
            validate(args, 'path')
            result = qg.download_bases(dates, bases, store_path, num_threads, uncompress, store_format)
        elif action == 'download_records':
            if not records: raise Exception('Records file not specified or empty')
            validate(args, 'path')
            result = qg.download_list(records, store_path, num_threads, uncompress, store_format)
        elif action == 'download_records_bases':
            if not records: raise Exception('Records file not specified or empty')
            validate(args, 'path')
            result = qg.download_list_bases(records, store_path, num_threads, uncompress, store_format)
        else:
            raise Exception('Unknown action')
    except Exception as e:
        on_error(str(e))

    if result is None:
        print('None')
    else:
        print(json.dumps(result, indent=4, sort_keys=True))

if __name__ == '__main__':
    main(sys.argv)