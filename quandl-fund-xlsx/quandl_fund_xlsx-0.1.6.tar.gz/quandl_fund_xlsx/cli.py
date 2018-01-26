# -*- coding: utf-8 -*-
"""quandl_fund_xlsx

Usage:
  quandl_fund_xlsx (-i <ticker-file> | -t <ticker>) [-o <output-file>]
                                 [-y <years>] [-d <sharadar-db>]
                                 

  quandl_fund_xlsx.py (-h | --help)
  quandl_fund_xlsx.py --version

Options:
  -h --help             Show this screen.
  -i --input <file>     File containing one ticker per line
  -t --ticker <ticker>  Ticker symbol
  -o --output <file>    Output file [default: stocks.xlsx]
  -y --years <years>    How many years of results (max 7 with SF0) [default: 5]
  -d --database <database>    Sharadar Fundamentals database to use, SFO or
                              SF1 [default: SF0]
  --version             Show version.

"""
# the imports have to be under the docstring
# otherwise the docopt module does not work.
from docopt import docopt
from .fundamentals import stock_xlsx
import sys


def main(args=None):
    arguments = docopt(__doc__, version='0.1.6')
    print(arguments)

    file = arguments['--input']

    tickers = []
    if file is None:
        ticker = arguments['--ticker']
        print("Ticker =",ticker)
        tickers.append(ticker)
    else:
        with open(file) as t_file:
            for line in t_file: # Each line contains a ticker
                tickers.append(line.strip())
                print("Ticker =", line)

    years = arguments['--years']
    years = int(years)

    outfile = arguments['--output']
    database = arguments['--database']

    if database == 'SF0': 
        dimension = 'MRY' # Most recent year
    elif database == 'SF1': 
        dimension = 'MRT' # Most recent trailing 12 months
    else:
        print('Invalid database, use SF1 or SF0')
        sys.exit()

    print("Output will be written to {}".format(outfile))
    stock_xlsx(outfile, tickers, database, dimension, years)


if __name__ == '__main__':
    main()
