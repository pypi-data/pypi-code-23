'''
Created on 28 sept. 2014

@author: coissac
'''

from subprocess import Popen
from tempfile   import mkdtemp
from tempfile   import mktemp
from shutil     import rmtree

import atexit
import os.path
import sys

from orgasm.indexer import Index
from orgasm.reads._sequences import readPairedEnd, setLogger, getStats  # @UnresolvedImport

__title__="Index a set of reads"

default_config = { 'reformat' : False,
                   'single'   : False,
                   'forward'  : None,
                   'reverse'  : None,
                   '5trim'    : 0,
                   'qualtrim' : 0,
                   'badqual'  : 10,
                   'skip'     : 0,
                   'maxread'  : 0,
                   'length'   : 0,
                   'estimate' : 0,
                   'minlength': 0,
                   'nopipe'   : False,
                   'checkpairs':False,
                   'mate'     : False,
                   "phix"     : False,
                   "fastqdump": False,
                   'shift'    : 33,
                   "direct"   : False,
                   "zip"      : False
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='name of the produced index')

    parser.add_argument(dest='index:forward',  metavar='forward', 
                        nargs='?', 
                        default=None,
                        help='Filename of the forward reads')
    
    parser.add_argument(dest='index:reverse',     
                        metavar='reverse', 
                        nargs='?', 
                        default=None,
                        help='Filename of the reverse reads' )
    
    
    parser.add_argument("--reformat",
                        dest="index:reformat",
                        action='store_true',
                        default=None,
                        help='Asks for reformatting an old sequence index to the new format'
                       )
    
    parser.add_argument('--single',           
                        dest='index:single', 
                        action='store_true', 
                        default=None, 
                        help='Single read mode, pair-end reads will be simulated')

    parser.add_argument('--check-phiX174',           
                        dest='index:phix', 
                        action='store_true', 
                        default=None, 
                        help='Checks for PhiX174 contamination (default)')

    parser.add_argument('--no-check-phiX174',           
                        dest='index:phix', 
                        action='store_false', 
                        default=None, 
                        help='Does not check for PhiX174 contamination')

    parser.add_argument('--mate-pairs',       dest='index:mate', 
                                              action='store_true', 
                                              default=None, 
                        help='Mate pair library mode')

    parser.add_argument('--5-prime-trim',     dest='index:5trim', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='Cut the N first base pairs of '
                             'reads (default %dbp)' % default_config['5trim'])
    
    parser.add_argument('--3-prime-quality',  dest='index:qualtrim', 
                                              metavar="Q",
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help="Hard clips the 3' end of each reads"
                             'after the first base with a score '
                             "less or equal to Q (default 0 no clipping)")
    
    parser.add_argument('--bad-quality',  dest='index:badqual', 
                                              metavar="Q",
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help="Consider quality below Q as bad "
                             "quality score, and try to clip "
                             "reads to maximise the overall "
                             "quality. Zero means no clipping "
                             "(default %d)" % default_config['badqual'])
    
    parser.add_argument('--skip',             dest='index:skip', 
                                              metavar="N",
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='Skip the N first read pairs '
                             '(default %d)' % default_config['skip'])
    
    parser.add_argument('--max-reads',        dest='index:maxread', 
                                              metavar="N",
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='index a maximum of N read pairs '
                             '(default the full file)')
    
    parser.add_argument('--length',           dest='index:length', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='The length of the read to index '
                             ' (default indexed length is estimated from the first read)')
    
    parser.add_argument('--estimate-length',  dest='index:estimate', 
                                              metavar='FRACTION',
                                              type=float, 
                                              action='store', 
                                              default=None, 
                        help='Estimate the length to index for conserving FRACTION '
                             'of the overall data set')
    
    parser.add_argument('--minimum-length',   dest='index:minlength', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='The minimum length of the read to index '
                             'if the --estimate-length is activated (default 81)')
    
    parser.add_argument('--no-pipe',          dest='index:nopipe', 
                                              action='store_true', 
                                              default=None, 
                        help='do not use pipe but temp files instead')

    parser.add_argument('--bypass-filtering', dest='index:direct', 
                                              action='store_true', 
                                              default=None, 
                        help='Sequence files are considered as '
                             'pre-filtered fastq files')

    parser.add_argument('--fastq-dump',           
                        dest='index:fastqdump', 
                        action='store_true', 
                        default=None, 
                        help='Dump the fastq file or the trimmed reads')

    parser.add_argument('--check-pairing',            dest='index:checkpairs', 
                                              action='store_true', 
                                              default=False, 
                        help='ensure that forward and reverse files are correctly paired')

    parser.add_argument('--low-memory',       dest='index:zip', 
                                              action='store_true', 
                                              default=None, 
                        help='Reduce memory usage for optimal length computation')

    parser.add_argument('--quality-encoding-offset',  dest='index:shift', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='The code offset added to each quality '
                             'score to encode fastq quality '
                             '(default %d - Sanger format)' % default_config['shift'])
    

tmpdir = []

# @atexit.register
# def cleanup():
#     try:
#         os.unlink(FIFO)
#     except:
#         pass

def reformatOldIndex(config):

    logger  = config['orgasm']['logger']
    output  = config['orgasm']['indexfilename']
    if not (os.path.exists('%s.ofx' % output ) and
            os.path.exists('%s.ogx' % output ) and
            os.path.exists('%s.opx' % output ) and
            os.path.exists('%s.orx' % output )
           ):
        logger.error('The %s index does not exist or is not complete' % output)
        sys.exit(1)
    
    dirname = '%s.odx' % output
    if not os.path.exists(dirname):
        os.makedirs(dirname) 

    os.rename('%s.ofx' % output, '%s/index.ofx' % dirname)
    os.rename('%s.ogx' % output, '%s/index.ogx' % dirname)
    os.rename('%s.opx' % output, '%s/index.opx' % dirname)
    os.rename('%s.orx' % output, '%s/index.orx' % dirname)

    sys.exit(0)

def postponerm(filename):
    def trigger():
        print("Deleting tmp file : %s" % filename,file=sys.stderr)
        try:
            os.unlink(filename)
        except:
            pass
        
    return trigger

def postponermdir(filename):
    def trigger():
        print("Deleting tmp directory : %s" % filename,file=sys.stderr)
        try:
            rmtree(filename)
        except:
            pass
        
    return trigger

def getTmpDir():
    global tmpdir

    if not tmpdir:
        tmpdir.append(mkdtemp())
        atexit.register(postponermdir(tmpdir[0]))
        
    return tmpdir[0]


def ungzip(filename,nopipe):
    tmpdir = getTmpDir()

    fifo = mktemp(prefix="unziped-", dir=tmpdir)
    command="gzip -d -c %s > %s" % (filename,fifo)
    
    if nopipe:
        os.system(command)
    else:
        os.mkfifo(fifo)
        process = Popen(command,                                            # @UnusedVariable
                        shell=True,
                        stderr=open('/dev/null','w')) 
    
    atexit.register(postponerm(fifo))

    return fifo

def unbzip(filename,nopipe):
    tmpdir = getTmpDir()

    fifo = mktemp(prefix="unziped-", dir=tmpdir)
    command="bzip2 -d -c %s > %s" % (filename,fifo)
    atexit.register(postponerm(fifo))
    
    if nopipe:
        os.system(command)
    else:
        os.mkfifo(fifo)
        process = Popen(command,                                            # @UnusedVariable
                        shell=True,
                        stderr=open('/dev/null','w')) 
    
    return fifo
                
def formatFastq(seq):
    fastq = '@{id:0>7}\n{seq}\n+\n{qual}'
    return fastq.format(id=seq[0].decode('ascii'),
                        seq=seq[1].decode('ascii'),
                        qual=bytes(seq[2]).decode('ascii'))
                       
def writeToFifo(pairs,forward,reverse,fastq,logger):
    logger.info("Forward tmp file : %s" % forward)
    logger.info("Reverse tmp file : %s" % reverse)
    i=0
    
    if fastq:
        ffq=open("%s.odx/forward.fastq" % fastq,'w')
        rfq=open("%s.odx/reverse.fastq" % fastq,'w')
        
    with open(forward,'w',buffering=1) as f, \
         open(reverse,'w',buffering=1) as r:
        for p in pairs:
            i+=1
            if not i % 1000000:
                logger.info('%d sequence pairs written' % i)
            if len(p[0][1]) > 0 and len(p[1][1]) > 0:
                fread = formatFastq(p[0])
                rread = formatFastq(p[1])
                print(fread,file=f)
                print(rread,file=r)
                if fastq:
                    print(fread,file=ffq)
                    print(rread,file=rfq)
        
    if fastq:
        ffq.close()
        rfq.close()

def run(config):

    logger  = config['orgasm']['logger']
    output  = config['orgasm']['indexfilename']
    forward = config['index']['forward']
    reverse = config['index']['reverse']
    nopipe  = config['index']['nopipe']
    
    if config['index']['reformat']:
        reformatOldIndex(config)
    else:
        if forward is None:
            logger.error('No sequence file specified')
            sys.exit(1)
    
    if nopipe:
        logger.info("Indexing in no pipe mode")
    
    if reverse is None:
        if config['index']['mate']:
            mode="IMP"
        elif config['index']['single']:
            mode="SimPE"
        else:
            mode='IPE'
    else:
        if config['index']['mate']:
            mode="MP"
        elif config['index']['single']:
            logger.error('Two sequence files provided and --single specified')
            sys.exit(1)
        else:
            mode='PE'
  
    if not os.path.exists('%s.odx' % output ):
        os.makedirs('%s.odx' % output ) 
        
    command = ['orgasmi','-o','%s.odx/index'  % output]
          
    if config['index']['direct']:
        if mode!='PE':
            logger.error('Bypass filtering mode but no regular pair-end files used')
            sys.exit(1)
        else:
            if forward[-3:]=='.gz':
                logger.info('Forward file compressed by gzip')
                forward = ungzip(forward,nopipe)
                 
            if forward[-4:]=='.bz2':
                logger.info('Forward file compressed by bzip2')
                forward = unbzip(forward,nopipe)
         
                 
            if reverse[-3:]=='.gz':
                logger.info('Reverse file compressed by gzip')
                reverse = ungzip(reverse,nopipe)
          
            if reverse[-4:]=='.bz2':
                logger.info('Reverse file compressed by bzip2')
                reverse = unbzip(reverse,nopipe)
                
    else:
        filenames = [forward]
        if reverse is not None:
            filenames.append(reverse)
            
        forward = mktemp(prefix="forward-", dir=getTmpDir())
        atexit.register(postponerm(forward))
        
        if not nopipe:
            os.mkfifo(forward)
        
        reverse = mktemp(prefix="reverse-", dir=getTmpDir())
        atexit.register(postponerm(reverse))
        
        if not nopipe:
            os.mkfifo(reverse)
            
        setLogger(logger)

        pairs = readPairedEnd(filenames,
                              mode            = mode,
                              checkIds        = config['index']['checkpairs'],
                              cut             = config['index']['5trim'],
                              badQualityLimit = config['index']['badqual'],
                              qualityCut      = config['index']['qualtrim'],
                              length          = config['index']['length'],
                              lengthestimate  = config['index']['estimate'],
                              minlength       = config['index']['minlength'],
                              skip            = config['index']['skip'],
                              maxread         = config['index']['maxread'],
                              phix            = config['index']['phix'],
                              shift           = config['index']['shift'],
                              zip             = config['index']['zip']
                             )
        
        if config['index']['fastqdump']:
            fastq = output
        else:
            fastq = None
                                       
    command.append(forward)
    command.append(reverse)
    
    logger.info(" ".join(command))
    
    if not config['index']['direct']:
        if nopipe:
            logger.info("Writting transformed sequence files...")
            writeToFifo(pairs,forward,reverse,fastq,logger)
            logger.info("Done.")
            
            logger.info("Starting indexing...")
            logger.info(" ".join(command))
            os.system(" ".join(command)) 
        else:
            try:
                logger.info("Starting indexing...")
                process=Popen(command)
                writeToFifo(pairs,forward,reverse,fastq,logger)
                process.wait()
                logger.info('Done.')
            except BrokenPipeError:
                process.wait()
                logger.info('Done.')
                logger.warning("Maximum count of read indexed.")
                logger.warning("Indexing stopped but the index is usable.")
    else: 
        logger.info("Starting indexing...")
        logger.info(" ".join(command))
        os.system(" ".join(command)) 
    
        
    stats = getStats()
    
    if "paircount" in stats:
        logger.info("%9d reads pairs processed" % stats["paircount"])
    
    if "phix174" in stats:
        logger.info("%9d phix174 reads pairs sorted out" % stats["phix174"])
    
    if "SoftQualityTrim" in stats:
        logger.info("%9d reads pairs soft trimmed on a quality of %d" % (stats["SoftQualityTrim"],
                                                                         config['index']['badqual']))
    if "ACGTtrim" in stats:
        logger.info("%9d reads pairs clipped for not [A,C,G,T] bases" % stats["ACGTtrim"])
    
    if "bad_ids" in stats:
        logger.info("%9d reads pairs sorted out because of not corresponding ids" % stats["bad_ids"]) 
        
    
    
    r=Index('%s.odx/index'  % output)
            
    logger.info('Count of indexed reads: %d' % len(r))  

              
