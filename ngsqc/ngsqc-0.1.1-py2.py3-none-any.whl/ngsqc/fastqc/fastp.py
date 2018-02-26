import os
from config import fastp,tsv2xls
from jbiot.logrun import log

sdir = os.path.dirname(os.path.abspath(__file__))
fp2tb = os.path.join(sdir,"fastp2table.py")

def qc(fqs,prefix):

    out = "%s.fastp" % prefix
    cmd = "mkdir %s" % out
    log.info(cmd,prefix)
    log.run(cmd,prefix)

    log.info("fastq file qc by `fastp`",prefix) 
    jsons = []    
    for item in fqs:
        fq = item[0]
        prex = item[1]
        html =  prex + ".html"
        html = os.path.join(out,html)
        json =  prex + ".json"
        json = os.path.join(out,json)
        jsons.append(json)
        cmd = "%s -Q -L -i %s -h %s -j %s " % (fastp,fq,html,json)
        log.run(cmd,prefix)    
    jstr = " ".join(jsons)
    
    log.info("convert fastp jsons to table ",prefix)
    cmd = "python %s %s %s" % (fp2tb,jstr,prefix)
    log.run(cmd,prefix)

    tsv = prefix + ".fastqInfo.tsv"
    log.info("convert tsv to xls ",prefix)
    cmd = "%s %s" % (tsv2xls,tsv)
    log.run(cmd,prefix)

    return out


    
