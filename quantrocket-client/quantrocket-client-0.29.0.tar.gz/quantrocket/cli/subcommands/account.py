# Copyright 2017 QuantRocket - All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
from quantrocket.cli.utils.parse import dict_str

def add_subparser(subparsers):
    _parser = subparsers.add_parser("account", description="QuantRocket account CLI", help="quantrocket account -h")
    _subparsers = _parser.add_subparsers(title="subcommands", dest="subcommand")
    _subparsers.required = True

    examples = """
Query IB account balances.

Examples:

Query the latest account balances.

    quantrocket account balance --latest

Query the latest NLV (Net Liquidation Value) for a particular account:

    quantrocket account balance --latest --fields NetLiquidation --accounts U123456

Check for accounts that have fallen below a 5% cushion and log the results,
if any, to flightlog:

    quantrocket account balance --latest --below Cushion:0.05 | quantrocket flightlog log --name quantrocket.account --level CRITICAL

Query historical account balances over a date range:

    quantrocket account balance --start-date 2017-06-01 --end-date 2018-01-31
    """
    parser = _subparsers.add_parser(
        "balance",
        help="query IB account balances",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    filters = parser.add_argument_group("filtering options")
    filters.add_argument(
        "-s", "--start-date",
        metavar="YYYY-MM-DD",
        help="limit to account balance snapshots taken on or after "
        "this date")
    filters.add_argument(
        "-e", "--end-date",
        metavar="YYYY-MM-DD",
        help="limit to account balance snapshots taken on or before "
        "this date")
    filters.add_argument(
        "-l", "--latest",
        action="store_true",
        help="return the latest account balance snapshot")
    filters.add_argument(
        "-a", "--accounts",
        nargs="*",
        metavar="ACCOUNT",
        help="limit to these accounts")
    filters.add_argument(
        "-b", "--below",
        type=dict_str,
        nargs="*",
        metavar="FIELD:AMOUNT",
        help="limit to accounts where the specified field is below "
        "the specified amount (pass as field:amount, for example Cushion:0.05)")
    outputs = parser.add_argument_group("output options")
    outputs.add_argument(
        "-o", "--outfile",
        metavar="OUTFILE",
        dest="filepath_or_buffer",
        help="filename to write the data to (default is stdout)")
    output_format_group = outputs.add_mutually_exclusive_group()
    output_format_group.add_argument(
        "-j", "--json",
        action="store_const",
        const="json",
        dest="output",
        help="format output as JSON (default is CSV)")
    output_format_group.add_argument(
        "-p", "--pretty",
        action="store_const",
        const="txt",
        dest="output",
        help="format output in human-readable format (default is CSV)")
    outputs.add_argument(
        "-f", "--fields",
        metavar="FIELD",
        nargs="*",
        help="only return these fields (pass '?' or any invalid fieldname to see "
        "available fields)")
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="refresh account balances from IB (default is to query the "
        "database, which is refreshed every minute)")
    parser.set_defaults(func="quantrocket.account._cli_download_account_balances")

    examples = """
Query exchange rates for the base currency.

The exchange rates in the exchange rate database are sourced from the
European Central Bank's reference rates, which are updated each day at 4 PM
CET.

Examples:

Query the latest exchange rates.

    quantrocket account rates --latest
    """
    parser = _subparsers.add_parser(
        "rates",
        help="query exchange rates for the base currency",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    filters = parser.add_argument_group("filtering options")
    filters.add_argument(
        "-s", "--start-date",
        metavar="YYYY-MM-DD",
        help="limit to exchange rates on or after this date")
    filters.add_argument(
        "-e", "--end-date",
        metavar="YYYY-MM-DD",
        help="limit to exchange rates on or before this date")
    filters.add_argument(
        "-l", "--latest",
        action="store_true",
        help="return the latest exchange rates")
    filters.add_argument(
        "-b", "--base-currencies",
        nargs="*",
        metavar="CURRENCY",
        help="limit to these base currencies")
    filters.add_argument(
        "-q", "--quote-currencies",
        nargs="*",
        metavar="CURRENCY",
        help="limit to these quote currencies")
    outputs = parser.add_argument_group("output options")
    outputs.add_argument(
        "-o", "--outfile",
        metavar="OUTFILE",
        dest="filepath_or_buffer",
        help="filename to write the data to (default is stdout)")
    output_format_group = outputs.add_mutually_exclusive_group()
    output_format_group.add_argument(
        "-j", "--json",
        action="store_const",
        const="json",
        dest="output",
        help="format output as JSON (default is CSV)")
    output_format_group.add_argument(
        "-p", "--pretty",
        action="store_const",
        const="txt",
        dest="output",
        help="format output in human-readable format (default is CSV)")
    parser.set_defaults(func="quantrocket.account._cli_download_exchange_rates")
