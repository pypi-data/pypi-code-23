#! /usr/bin/env python

import re


def convert_to_bedpe(input_file, output_file, margin_major, margin_minor):

    hin = open(input_file, 'r')
    hout = open(output_file, 'w')
    for line in hin:
        F = line.rstrip('\n').split('\t')
        if F[0].startswith('#'): continue
        if F[0] == "Chr_1" and F[1] == "Pos_1" and F[2] == "Dir_1": continue

        chr1, pos1, dir1, chr2, pos2, dir2, inseq = F[0], F[1], F[2], F[3], F[4], F[5], F[6]
        start1, end1, start2, end2 = pos1, pos1, pos2, pos2
        ID = ','.join([chr1, pos1, dir1, chr2, pos2, dir2, inseq])

        read_num = 0

        if dir1 == '+':
            start1 = str(int(start1) - int(margin_minor))
            end1 = str(int(end1) + int(margin_major))
        else:
            start1 = str(int(start1) - int(margin_major))
            end1 = str(int(end1) + int(margin_minor))

        if dir2 == '+':
            start2 = str(int(start2) - int(margin_minor))
            end2 = str(int(end2) + int(margin_major))
        else:
            start2 = str(int(start2) - int(margin_major))
            end2 = str(int(end2) + int(margin_minor))

        print >> hout, '\t'.join([chr1, start1, end1, chr2, start2, end2, ID, str(read_num), dir1, dir2])

    hin.close()
    hout.close()


