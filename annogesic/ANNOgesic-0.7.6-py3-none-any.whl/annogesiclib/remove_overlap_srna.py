import os
import sys
import csv
import argparse
import shutil
from annogesiclib.gff3 import Gff3Parser


def compare_srna_gff(gffs, strain, start, end, strand, args_srna):
    remove = False
    for gff in gffs:
        if (gff.seq_id == strain) and (
                gff.strand == strand):
            if ((gff.start >= start) and (
                 gff.end <= end)) or (
                (gff.start <= start) and (
                 gff.end >= end)) or (
                (gff.start >= start) and (
                 gff.start <= end) and (
                 gff.end >= end)) or (
                (gff.start <= start) and (
                 gff.end >= start) and (
                 gff.end <= end)):
                overlap = float(min(gff.end, end) -
                      max(gff.start, start)) / float(
                          gff.end - gff.start)
                if (args_srna.in_cds) and (
                     overlap > args_srna.cutoff_overlap):
                    remove = True
                elif not args_srna.in_cds:
                    remove = True
    return remove


def remove_overlap(srna_file, srna_table, gff_file, args_srna):
    out = open(srna_file + "_tmp", "w")
    out_t = open(srna_table + "_tmp", "w")
    gff_f = open(gff_file, "r")
    gffs = []
    for entry in Gff3Parser().entries(gff_f):
        if (entry.feature != "gene") and (
                entry.feature != "exon") and (
                entry.feature != "source") and (
                entry.feature != "region"):
            if args_srna.ex_srna:
                gffs.append(entry)
            else:
                if entry.feature != "ncRNA":
                    gffs.append(entry)
    srna_f = open(srna_file, "r")
    for srna in Gff3Parser().entries(srna_f):
        remove = compare_srna_gff(gffs, srna.seq_id, srna.start,
                                  srna.end, srna.strand, args_srna)
        if not remove:
            out.write(srna.info + "\n")
    fh = open(srna_table, "r")
    for row in csv.reader(fh, delimiter='\t'):
        remove = compare_srna_gff(gffs, row[0], int(row[2]),
                                  int(row[3]), row[4], args_srna)
        if not remove:
            out_t.write("\t".join(row) + "\n")
    shutil.move(srna_file + "_tmp", srna_file)
    shutil.move(srna_table + "_tmp", srna_table)
