'''
Created on 28 sept. 2014

@author: coissac
'''
import sys
from orgasm import getOutput,getIndex, getSeeds
from orgasm.tango import restoreGraph, estimateFragmentLength, genesincontig,\
    pathConstraints, scaffold, selectGoodComponent, unfoldAssembling, path2fasta, \
    parseFocedScaffold
    
from orgasm.format.sam import path2sam,buildReadSequence
from orgasm.version import version

__title__="Universal assembling graph unfolder"

default_config = { 'circular' : False,
                   'force'    : False,
                   'format'   : "fasta",
                   "fscaffold": [],
                   "path"     : None,
                   "contigs"  : False,
                   'tags'      : None,
                   'extension' : None,
                   '1x-coverage' : None
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='output', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    
    parser.add_argument('--path',             dest='unfold:path', 
                                              action='store',
                                              metavar='<edgeid>',
                                              type=int, 
                                              nargs='+', 
                                              default=None, 
                        help='A list of edge id separated by space add -- at the end of the path')

    parser.add_argument('--contigs',         dest='unfold:contigs', 
                                              action='store_true', 
                                              default=None, 
                        help='Outputs each stem of the assembly graph')

    parser.add_argument('--circular',         dest='unfold:circular', 
                                              action='store_true', 
                                              default=None, 
                        help='Wish a circular unfolding')

    parser.add_argument('--sam',         dest='unfold:format', 
                                              action='store_const', 
                                              const="sam",
                                              default=None, 
                        help='Produce a SAM file of the assembly')

    parser.add_argument('--fasta',            dest='unfold:format', 
                                              action='store_const', 
                                              const="fasta",
                                              default=None, 
                        help='Produce a FASTA file of the assembly [default format]')

    parser.add_argument('--force',            dest='unfold:force', 
                                              action='store_true', 
                                              default=None, 
                        help='Force circular unfolding')

    parser.add_argument('--force-scaffold',   dest='unfold:fscaffold', 
                                              action='append', 
                                              default=None, 
                        help='Force circular unfolding')

    parser.add_argument('--back',             dest='orgasm:back', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with paired-ends [default: <estimated>]')
    
    parser.add_argument('--1x-coverage',      dest='unfold:1x-coverage', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='The expected coverage for not duplicated regions [default: <estimated>]')

    parser.add_argument('--set-tag','-S',     dest ='unfold:tags', 
                                              metavar='tag', 
                                              action='append',
                                              default=[], 
                                              type=str, 
                        help='Allows to add a tag in the OBITools format '
                             'to the header of the fasta sequences')



def buildPath(asm,compactgraph,back,minlink,config):
    logger=config['orgasm']['logger']
    logger.info("Select the good connected components")
    gcc = selectGoodComponent(compactgraph)
    
    if config['unfold']['circular']:
        if config['unfold']['force']:
            logger.info("Force circular sequence")
        else:
            logger.info("Unfolding in circular mode")

    constraints = pathConstraints(asm,compactgraph,
                                  back=int(back),minlink=minlink)

    paths = []
    for seeds in gcc:
        path = unfoldAssembling(asm,compactgraph,
                                seeds=seeds,
                                constraints=constraints,
                                circular=config['unfold']['circular'],
                                force=config['unfold']['force'],
                                cov1x=config['unfold']['1x-coverage'],
                                logger=logger)
            
        paths.append(path[-1][0])
        
    return(paths)
        
def contigPath(asm,compactgraph,config):
    edges = [compactgraph.getEdgeAttr(*i)['stemid']
              for i in compactgraph.edgeIterator(edgePredicate = lambda e : compactgraph.getEdgeAttr(*e)['class']=="sequence")]
    return [(i,) for i in edges if i > 0]
   
    
def run(config):

    logger=config['orgasm']['logger']
    output = getOutput(config)

    if config['unfold']['force']:
        config['unfold']['circular']= True
        
    forcedscaffold = parseFocedScaffold(config['unfold']['fscaffold'])
    
         
    r = getIndex(config)
    coverage,x,newprobes = getSeeds(r,config)  # @UnusedVariable
    
    asm = restoreGraph(output+'.oax',r,x)

    logger.info("Evaluate fragment length")
    
    meanlength,sdlength = estimateFragmentLength(asm)
    
    if meanlength is not None:
        logger.info("Fragment length estimated : %f pb (sd: %f)" % (meanlength,sdlength))

    if config['orgasm']['back'] is not None:
        back = config['orgasm']['back']
    elif config['orgasm']['back'] is None and meanlength is not None:
        back = int(meanlength + 4 * sdlength)
        if back > 500:
            back=500
    else:
        back = 300
        
    logger.info("Evaluate pair-end constraints")
    
    cg = asm.compactAssembling(verbose=False)
    
    genesincontig(cg,r,x)

    minlink=config['orgasm']['minlink']
    scaffold(asm,cg,minlink=minlink,
             back=int(back),
             addConnectedLink=False,
             forcedLink=forcedscaffold,
             logger=logger)
     

    #fastaout = open(output+".fasta","w")
    fastaout = sys.stdout
    pathout  = open(output+".path","w")
    
    paths=[]
    #### --->
    if config['unfold']['path'] is not None:
        paths.append(tuple(config['unfold']['path']))
        
    if config['unfold']['contigs']:
        paths.extend(contigPath(asm,cg,config))
    
    if not paths:
        paths=buildPath(asm, cg, back, minlink, config)
    
    logger.info("Print the result as a %s file" % config['unfold']['format'])
    
    paths.sort()
       
    seqid = config['orgasm']['outputfilename'].split('/')[-1]

    if config['unfold']['format']=="sam":
        c=1
        printedPath=set()

        print("@HD\tVN:1.5\tSO:coordinate",file=fastaout)
        print("@PG\tID:ORG.Asm\tVN:%s" % version)
        
        for path in paths:
            rpath = tuple(-i for i in reversed(path))
            if path not in printedPath and rpath not in printedPath:
                printedPath.add(tuple(path))
                identifier="%s_%d" % (seqid,c)
                seqlength = len(buildReadSequence(asm,cg,identifier=identifier,
                                                  path=path,back=back,logger=logger))
                                
                print("@SQ\tSN:%s\tLN:%d" % (identifier,seqlength)) # <=== !!! ATTENTION !!!
                c+=1

    c=1
    printedPath=set()
    for path in paths:
       
        rpath = tuple(-i for i in reversed(path))
        
        if path not in printedPath and rpath not in printedPath:
            
            printedPath.add(tuple(path))
        
            logger.info("Expanded path : %s" % str(path))

            if config['unfold']['format']=="fasta":                   
                fa = path2fasta(asm,cg,path,
                     identifier="%s_%d" % (seqid,c),
                     back=back,
                     minlink=config['orgasm']['minlink'],
                     logger=logger,
                     tags=config['unfold']['tags'])
            if config['unfold']['format']=="sam":                   
                fa = path2sam(asm,cg,path,
                     identifier="%s_%d" % (seqid,c),
                     back=back,
                     minlink=config['orgasm']['minlink'],
                     logger=logger,
                     tags=config['unfold']['tags'])
    
            print(fa,file=fastaout)
            print(" ".join([str(x) for x in path]),file=pathout)

            c+=1
        
    with open(output +'.path.gml','w') as gmlfile:
        print(cg.gml(),file=gmlfile)

              
