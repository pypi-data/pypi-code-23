import os
from config import fastqc

from jbiot.logrun import log

def qc(fqs,prefix):

    out = "%s.fastqc" % prefix
    cmd = "mkdir %s" % out
    log.info(cmd,prefix)
    log.run(cmd,prefix)
    log.info("fastq file qc by `fastqc`",prefix) 
    for item in fqs:
        fq = item[0]
        prex = item[1]
        cmd = "%s -o %s %s " % (fastqc,out,fq)
        log.run(cmd,prefix)   

    log.info("unzip fastq zipfile",prefix) 
    cmd = "for x in  %s/*.zip ; do unzip $x ;rm $x;done " % out
    log.run(cmd,prefix)
    log.info("move fastqc file to fastqc direcorty ",prefix)
    cmd = "mv *fastqc %s " % out
    log.run(cmd,prefix)

    return out
    
