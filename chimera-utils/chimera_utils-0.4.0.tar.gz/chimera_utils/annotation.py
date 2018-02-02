#! /usr/bin/env python

import pysam

junction_margin = 5

def get_gene_info(chr, pos, gene_tb):

    tabixErrorFlag = 0
    try:
        records = gene_tb.fetch(chr, int(pos) - 1, int(pos) + 1)
    except Exception as inst:
        # print >> sys.stderr, "%s: %s" % (type(inst), inst.args)
        tabixErrorFlag = 1
        
    gene = [];
    if tabixErrorFlag == 0:
        for record_line in records:
            record = record_line.split('\t')
            gene.append(record[3])

    return list(set(gene))


def get_junc_info(chr, pos, exon_tb, junction_margin):

    tabixErrorFlag = 0
    try:
        records = exon_tb.fetch(chr, int(pos) - junction_margin, int(pos) + junction_margin)
    except Exception as inst:
        # print >> sys.stderr, "%s: %s" % (type(inst), inst.args)
        tabixErrorFlag = 1
        
    junction = []
    if tabixErrorFlag == 0:
        for record_line in records:
            record = record_line.split('\t')
            if abs(int(pos) - int(record[1])) < junction_margin:
                if record[5] == "+": junction.append(record[3] + ".start")
                if record[5] == "-": junction.append(record[3] + ".end")
            if abs(int(pos) - int(record[2])) < junction_margin:
                if record[5] == "+": junction.append(record[3] + ".end")
                if record[5] == "-": junction.append(record[3] + ".start")

    return list(set(junction))


