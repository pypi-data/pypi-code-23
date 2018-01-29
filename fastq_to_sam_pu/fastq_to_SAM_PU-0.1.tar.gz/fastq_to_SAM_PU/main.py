#!/usr/bin/env python

import argparse
import gzip
import lzma
import sys

from Bio import SeqIO

def main():
    parser = argparse.ArgumentParser('generate a PU from the first record of a fastq{.gz} file')
    parser.add_argument('-f', '--fastq_path',
                        required = True
    )
    args = parser.parse_args()
    fastq_path = args.fastq_path

    if fastq_path.endswith('.fq') or fastq_path.endswith('.fastq'):
        f_open = open(fastq_path, 'r')
    elif fastq_path.endswith('.gz'):
        f_open = gzip.open(fastq_path, 'rt')
    elif fastq_path.endswith('.xz'):
        f_open = lzma.open(fastq_path, 'rt')
    else:
        sys.exit(fastq_path + ' is not recognized file type')
    for record in SeqIO.parse(f_open, 'fastq'):
        if (record.id.count(':') == 6):
            flow_cell = record.id.split(':')[2]
            flow_cell_lane = record.id.split(':')[3]
            sample_barcode = record.description.split(' ')[1].split(':')[3]
            PU = flow_cell+':'+flow_cell_lane+':'+sample_barcode
            break
        elif (record.id.count(':') == 4):
            sys.exit('no flow cell ID')
        else:
            sys.exit('uknown fastq format')
    f_open.close()

    print(PU, file=sys.stdout)
    return

if __name__ == '__main__':
    main()
