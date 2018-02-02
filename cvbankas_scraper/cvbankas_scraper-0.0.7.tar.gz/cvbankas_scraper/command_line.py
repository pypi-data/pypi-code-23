import argparse
import json
from .core import scrape_multiple_pages


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("-v", action='store',
                        dest="verbose",
                        type=bool,
                        default=False,
                        help="Set verbose True/False")

    parser.add_argument("-t", action="store",
                        dest="timeout",
                        type=int,
                        default=1,
                        help="Timeout between single page requests, default 1 second")

    parser.add_argument("-o", action="store",
                        default="",
                        type=str,
                        dest="file_path",
                        help="JSON file path to store results")

    parser.add_argument("-u", action="store",
                        default="",
                        type=str,
                        required=True,
                        dest="url",
                        help="URL to start scraping")

    args = parser.parse_args()

    print(json.dumps(vars(args), indent=4))

    scrape_multiple_pages(url=args.url, file_path=args.file_path, verbose=args.verbose)
