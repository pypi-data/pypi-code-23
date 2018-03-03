#!/usr/bin/env python


import Job
import Processor

import logging
import sys
import multiprocessing
from optparse import OptionParser

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logger = logging.getLogger('main')

def main():
    """The main function of thumbup.
    """
    optparser = OptionParser()
    optparser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False)
    optparser.add_option("-R", action="store_true", dest="recur", default=False)
    optparser.add_option("-O", "--overwrite", action="store_true", dest="overwrite", default=False)
    optparser.add_option("--offset", action="store", dest="offset", type="int", default=60, metavar="OFFSET")

    try:
        (options, args) = optparser.parse_args()
        assert args
    except:
        print 'Usage: python thumbup.py file1 file2'
        sys.exit(-1)

    jobs = []

    try:
        for filename in args:
            jobs += Job.dir_scanner(filename, options)
    except:
        print 'Cannot parse input'
        sys.exit(-1)

    logger.info('collected %d jobs' % len(jobs))

    pool = multiprocessing.Pool(multiprocessing.cpu_count())
    procs = [Processor.Processor(j, pool, options) for j in jobs]

    for idx, p in enumerate(procs):
        print '[%d / %d]' % (idx, len(procs))
        p.run_noexcept()

    logger.info('Done.')


if __name__ == '__main__':
    main()
