#! /usr/bin/env python

import argparse
from getpass import getpass
import sys

from dateutil import parser as date_parser
from datetime import date, timedelta
from requests import post as http_post


def _gen_date_ranges(start_date, end_date):
    ranges = []
    start = start_date
    while start < end_date:
        end = start + timedelta(6)
        ranges.append((date.isoformat(start), date.isoformat(end)))
        start = end + timedelta(1)
    return ranges


def _parse_args():
    parser = argparse.ArgumentParser(
        description="Get the weekly ticket counts for the "
                    "provided range",
        epilog="This utility enables a client to obtain weekly "
               "ticket counts by generating source over time "
               "in a human readable format.")
    parser.add_argument("--start", dest="start_date",
                        required=True, help="Start date (ISO 8601)")
    parser.add_argument("--end", dest="end_date",
                        required=True, help="End date (ISO 8601)")
    args = parser.parse_args()

    try:
        sdate = date_parser.parse(args.start_date)
        edate = date_parser.parse(args.end_date)
    except ValueError as e:
        print("Invalid date: %s\n" % e.message)
        parser.print_help()
        return 1

    return sdate, edate


def _print_row(date, customer, employee, system, total, print_header=False):
    dhdr = 'date range'
    chdr = 'customer'
    ehdr = 'employee'
    shdr = 'system'
    thdr = 'total'
    sep = ', '
    if print_header:
        print(dhdr.rjust(len(date)), chdr, ehdr, shdr, thdr, sep=sep)
    print(date,
          repr(customer).rjust(len(chdr)),
          repr(employee).rjust(len(ehdr)),
          repr(system).rjust(len(shdr)),
          repr(total).rjust(len(thdr)),
          sep=sep
          )


def _wow_tickets(sdate, edate, token, headers, endpoint):
    print("Retrieving week over week ticket counts by generating source ...")
    ranges = _gen_date_ranges(sdate, edate)
    print_header = True
    for s, e in ranges:
        data = {"filters": {"range": "%s,%s" % (s, e)},
                "groups": ["source"]}
        r = http_post(endpoint, headers=headers, json=data)
        if r.status_code == 200:
            src = r.json().get('source')
            tot = r.json().get('metrics').get('created_count')
            cus = src.get('customer').get('metrics').get('created_count')
            emp = src.get('employee').get('metrics').get('created_count')
            sys = src.get('system').get('metrics').get('created_count')
            date = "%s - %s" % (s, e)
            _print_row(date, cus, emp, sys, tot, print_header)
            print_header = False
        else:
            print("Warning: %d for:" % r.status_code)
            print("      url: %s" % r.url)
            print("  headers: %s" % headers)
            print("     data: %s" % data)
    print("... done!")


def _main():
    sdate, edate = _parse_args()
    token = getpass("Enter auth token: ")
    headers = {'X-Auth-Token': token}
    endpoint = "https://latest.api.ops-fabric.com/analytics/reports/tickets"
    _wow_tickets(sdate, edate, token, headers, endpoint)
    return 0


if __name__ == "__main__":
    sys.exit(_main())
