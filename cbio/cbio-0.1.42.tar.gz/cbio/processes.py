from .biofiles.vcf import VCF
from .biofiles.bed import BED

import sys
import os

def vcf_peek(args):

    filepath = os.path.abspath(args.vcf)
    lines = args.lines
    pretty = args.pretty

    vcf = VCF(filepath)

    if all([args.head, args.tail]) is False:
        vcf.head(lines, pretty)
        vcf.tail(lines, pretty)

    if args.head:
        vcf.head(lines, pretty)

    if args.tail:
        vcf.tail(lines, pretty)


def bed_sort(args):
    filepath = os.path.abspath(args.bed)

    bed = BED(filepath)

    bed.sort()
