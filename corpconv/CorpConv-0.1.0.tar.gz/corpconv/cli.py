#!/usr/bin/env python3

import argparse
import functools
import logging


from corpconv import corpus_readers
from corpconv import corpus_writers


# format, --only-tokens, delimiter, number of fields

def arguments():
    parser = argparse.ArgumentParser(description="Convert a corpus from a given input format to the desired output format.")
    parser.add_argument("-i", "--input-format", choices=["conll", "osl", "tsv", "vrt"], required=True, help="Input format. conll: Tab-separated, one token per line with token id, empty line after sentences, empty fields marked with \"_\"; osl: One sentence per line, custom delimiter for annotation; tsv: Tab-separated, one token per line, empty line after sentences; vrt: Tab-separated, one token per line, sentences as s-tags")
    parser.add_argument("-o", "--output-format", choices=["conll", "osl", "tsv", "vrt"], required=True, help="Output format. See --input-format.")
    parser.add_argument("-d", "--delimiter", type=str, default="\t", help="Delimiter in osl format (default: \"\\t\".")
    parser.add_argument("-n", "--nfields", type=int, help="Number of fields in osl format (only for reading from osl).")
    parser.add_argument("FILE", type=argparse.FileType("r"), help="The input file")
    args = parser.parse_args()
    return args


def main():
    args = arguments()
    readers = {"conll": corpus_readers.read_conll,
               "osl": functools.partial(corpus_readers.read_osl, delimiter=args.delimiter, nr_of_fields=args.nfields),
               "tsv": corpus_readers.read_tsv,
               "vrt": corpus_readers.read_vrt}
    writers = {"conll": corpus_writers.write_conll,
               "osl": functools.partial(corpus_writers.write_osl, delimiter=args.delimiter),
               "tsv": corpus_writers.write_tsv,
               "vrt": corpus_writers.write_vrt}
    reader = readers[args.input_format]
    writer = writers[args.output_format]
    for line in writer(reader(args.FILE)):
        print(line)


if __name__ == "__main__":
    main()
