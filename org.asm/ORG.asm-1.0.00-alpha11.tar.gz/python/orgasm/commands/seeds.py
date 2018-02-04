'''
Created on 28 sept. 2014

@author: coissac
'''

import orgasm.samples

from orgasm import getOutput,getIndex, getSeeds



__title__="Build the set of seed reads"


default_config = { "reformat" : None
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='index', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='output', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    
    parser.add_argument('--phiX',              dest='orgasm:phix', 
                                              action='store_true', 
                                              default=None, 
                        help='activate the filtering of Phi-X174 sequences [default]')
    
    parser.add_argument('--phiX-off',              dest='orgasm:phix', 
                                              action='store_false', 
                                              default=None, 
                        help='desactivate the filtering of Phi-X174 sequences')
    
    parser.add_argument('--seeds',            dest ='orgasm:seeds', 
                                              metavar='seeds', 
                                              action='append',
                                              default=[], 
                                              type=str, 
                        help='protein or nucleic seeds; either a fasta file containing '
                        'seed sequences or the name of one of the internal set of seeds '
                        'among %s' % str(list(filter(lambda s: s.startswith('prot') or 
                                                s.startswith('nuc'),dir(orgasm.samples)))))

    parser.add_argument('--kup',              dest='orgasm:kup', 
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='The word size used to identify the seed reads '
                             '[default: protein=4, DNA=12]')

    parser.add_argument("--reformat",
                        dest="seeds:reformat",
                        action='store_true',
                        default=None,
                        help='Asks for reformatting an old sequence index to the new format'
                       )


def run(config):
    
    logger=config['orgasm']['logger']
    output = getOutput(config)                      # @UnusedVariable

    logger.info("Looking for the seed reads")
    
    r = getIndex(config)
    ecoverage,x,newprobes = getSeeds(r,config)      # @UnusedVariable

    logger.info('Coverage estimated from probe matches at : %d' % ecoverage)
    
