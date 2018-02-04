'''
Created on 27 sept. 2016

@author: coissac
'''
from orgasm import getOutput, getIndex, getSeeds
from orgasm.tango import restoreGraph, estimateFragmentLength, genesincontig,\
    scaffold, pairEndedConnected
    
from orgasm.version import version
import pathlib
import sys

__title__="Restore the intermediate graph saved regularly during the assembling process."

default_config = {}

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='<index>', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='<output>', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
        
    
    parser.add_argument('--back',             dest='orgasm:back', 
                                              metavar='<insert size>',
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with pared-ends [default: <estimated>]')



   
def cat(filename):
    with open(filename,'r') as f:
        for line in f:
            print(line)
            
def run(config):

    logger=config['orgasm']['logger']
    output = getOutput(config)


    if not pathlib.Path(output+'.gml').is_file():
        logger.error("No assembly graph available")
        sys.exit(1)
        
    if config['graph']['format']=='gml':
        cat(output+'.gml')
    elif  config['graph']['format']=='gmlpath':
        if pathlib.Path(output+'.path.gml').is_file():
            cat(output+'.path.gml')
        else:
            cat(output+'.gml')
    elif  config['graph']['format']=='lastgraph':
        r = getIndex(config)
        ecoverage,seeds,newprobes = getSeeds(r,config)  # @UnusedVariable
        
        asm = restoreGraph(output+'.oax',r,seeds)
    
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
        compactGraph2lastgraph(asm,logger=logger)

