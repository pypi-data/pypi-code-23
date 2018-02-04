'''
Created on 28 sept. 2014

@author: coissac
'''

from orgasm import getOutput
import shutil
import sys
import os

__title__="copy an assembly"


default_config = { "source" : None,
                   "dest"   : None,
                   "force"  : False
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:outputfilename',  metavar='outputfilename', 
                        help='name of the assembly to be copied')
    
    parser.add_argument(dest='clone:dest',     metavar='dest', 
                        help='name of the new copy of the assembly' )
    
    parser.add_argument("--force","-f",
                        dest='clone:force',
                        action='store_true',
                        default=None,
                        help='Force cloning even if the destination already exist' )
    


def run(config):
    
    logger=config['orgasm']['logger']
    progress = config['orgasm']['progress']

    source = getOutput(config)
    
    logger.info("Copying the assembly %s to %s" % (config['orgasm']['outputfilename'],
                                                   config['clone']['dest'])) 
    
    if os.path.exists("%s.oas"  % config['clone']['dest']):
        if config['clone']['force']:
            shutil.rmtree("%s.oas"  % config['clone']['dest'])
        else:
            logger.error('Destination assembling exists')
            sys.exit(1)
        
    shutil.copytree("%s.oas"  % config['orgasm']['outputfilename'], 
                    "%s.oas"  % config['clone']['dest'])
    
    
