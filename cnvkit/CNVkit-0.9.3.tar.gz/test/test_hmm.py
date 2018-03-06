#!/usr/bin/env python
"""Unit tests for the CNVkit library, cnvlib."""
from __future__ import absolute_import, division, print_function
import time
#  import numpy as np

import cnvlib
from cnvlib import segmentation
from skgenome import tabio

for cnr_fname in ("amplicon.cnr", "p2-20_1.cnr",
                  #"p2-20_2.cnr",
                  #  "wgs-chr17.cnr"
                 ):
    cnarr = cnvlib.read("formats/" + cnr_fname)
    n_chroms = cnarr.chromosome.nunique()
    time1 = time.clock()

    print("Segmenting", cnr_fname, "by 'hmm'")
    segments = segmentation.do_segmentation(cnarr, "hmm")
    assert len(segments) > n_chroms
    time1, time2 = time.clock(), time1
    print("\t->", len(segments), "segments in", time1 - time2, "seconds")

    print("Segmenting", cnr_fname, "by 'hmm-tumor'")
    segments = segmentation.do_segmentation(cnarr, "hmm-tumor",
                                            skip_low=True)
    assert len(segments) > n_chroms
    time1, time2 = time.clock(), time1
    print("\t->", len(segments), "segments in", time1 - time2, "seconds")

    print("Segmenting", cnr_fname, "by 'hmm-germline'")
    segments = segmentation.do_segmentation(cnarr, "hmm-germline")
    assert len(segments) > n_chroms
    time1, time2 = time.clock(), time1
    print("\t->", len(segments), "segments in", time1 - time2, "seconds")

    #  varr = tabio.read("formats/na12878_na12882_mix.vcf", "vcf")
    #  segments = segmentation.do_segmentation(cnarr, "hmm", variants=varr)
    #  assert len(segments) > n_chroms
    #  time1, time2 = time.clock(), time1
    #  print("\t->", len(segments), "segments in", time1 - time2, "seconds")

    print(cnr_fname, "A-OK")
