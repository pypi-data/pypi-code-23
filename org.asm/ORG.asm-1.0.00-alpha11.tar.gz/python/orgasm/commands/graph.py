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

__title__="Build a graph file from the assembling graph"

default_config = { 'format': 'gml'
                 }

def addOptions(parser):
    parser.add_argument(dest='orgasm:indexfilename',  metavar='<index>', 
                        help='index root filename (produced by the oa index command)')
    
    parser.add_argument(dest='orgasm:outputfilename',     metavar='<output>', 
                                                          nargs='?', 
                                                          default=None,
                        help='output prefix' )
    
    parser.add_argument('--gml',              dest='graph:format',
                                              action='store_const',
                                              const='gml',
                                              default=None,
                        help="Write the assembling graph in gml format [default]")
        
    
    parser.add_argument('--gml-path',         dest='graph:format',
                                              action='store_const',
                                              const='gmlpath',
                                              default=None,
                        help="Write the assembling graph in gml format with "
                             "the indication of the last exported sequence path")
        
    parser.add_argument('--lastgraph',        dest='graph:format',
                                              action='store_const',
                                              const='lastgraph',
                                              default=None,
                        help="Write the assembling graph in lastgraph format (Velvet). "
                             "This format is readable by the Bandage visualizer")
        
    
    parser.add_argument('--back',             dest='orgasm:back', 
                                              metavar='<insert size>',
                                              type=int, 
                                              action='store', 
                                              default=None, 
                        help='the number of bases taken at the end of '
                             'contigs to jump with pared-ends [default: <estimated>]')



def compactGraph2lastgraph(asm,paths=[],minlink=5,back=250,logger=None):
#FASTG:begin;
#FASTG:version=1.0:assembly_name=”tiny example”;
    cg = asm.compactAssembling(verbose=False)
    genesincontig(cg,asm.index,asm.seeds)

    scaffold(asm,
             cg,
             minlink=minlink,
             back=int(back),
             addConnectedLink=False,
             logger=logger)
    
    edges = list(cg.stemIterator())
    nodes = [e for e in edges if "stemid" in e]
    seqcount = sum(e['length'] for e in nodes if 'gappairs' not in e) / 2
    
    nodes = dict((n['stemid'],n) for n in nodes)
    
    # Print the header of the file
    
    print("{nodecount:d} {seqcount:d} {hash:d} 1".format(
                nodecount = int(len(nodes)/2),
                seqcount  = int(seqcount),
                hash      = int(asm.index.getReadSize())
            )
          )
 
    begins  = {}
 
    # print the nodes -- here nodes corresponds to edge in oa
    for n in range(1,int(len(nodes)/2)+1): 
        first = nodes[n]['first']
        if first not in begins:
            begins[first]=[]
        begins[first].append(n)

        first = nodes[-n]['first']
        if first not in begins:
            begins[first]=[]
        begins[first].append(-n)
        
               
        print("NODE    {NODE_ID:d}  {LENGTH:d}  {COV_SHORT1:d}   {O_COV_SHORT1:d}  {COV_SHORT2:d}  {O_COV_SHORT2:d}".format(
                NODE_ID=n,
                LENGTH=len(nodes[n]['sequence']),
                COV_SHORT1=nodes[n]['weight'] * len(nodes[n]['sequence']),
                O_COV_SHORT1=nodes[n]['weight'] * len(nodes[n]['sequence']),
                COV_SHORT2=0,
                O_COV_SHORT2=0
             )
            )
        print(nodes[n]['sequence'].decode('ASCII'))
        print(nodes[-n]['sequence'].decode('ASCII'))
        
    # Print arc joining nodes
    done=set()
    for n in range(1,int(len(nodes)/2)+1): 
        last = nodes[n]['last']
        if last in begins:
            for ne in begins[last]:
                if 'path' not in nodes[n]:
                    connected=nodes[n]['pairendlink']
                elif 'path' not in nodes[ne]:
                    connected=nodes[ne]['pairendlink']
                else:
                    connected,ml,sl,delta = pairEndedConnected(asm,cg,n,ne,back)  # @UnusedVariable
                done.add((n,ne))
                print("ARC {START_NODE}    {END_NODE}    {MULTIPLICITY}".format(
                            START_NODE=n,
                            END_NODE=ne,
                            MULTIPLICITY=connected
                        )
                      )
        last = nodes[-n]['last']
        if last in begins:
            for ne in begins[last]:
                if (-ne,-n) not in done:
                    if 'path' not in nodes[n]:
                        connected=nodes[-n]['pairendlink']
                    elif 'path' not in nodes[ne]:
                        connected=nodes[ne]['pairendlink']
                    else:
                        connected,ml,sl,delta = pairEndedConnected(asm,cg,-n,ne,back)  # @UnusedVariable
                    print("ARC {START_NODE}    {END_NODE}    {MULTIPLICITY}".format(
                                START_NODE=-n,
                                END_NODE=ne,
                                MULTIPLICITY=connected
                            )
                          )
            

def compactGraph2gfa(cg,paths=[]):

    print("# Organelle Assembler - version {}".format(version))
    print("# Graphical Fragment Assembly (GFA) file")
    print('H    VN:Z:1.0')
    
    begins = {}
    ends = {}
    for node1,node2,edge in cg.edgeIterator():
        stem = cg.getEdgeAttr(node1,node2,edge)
        
        if 'stemid' in stem:
            bl = begins.get(node1,[])
            begins[node1]=bl
            bl.append(stem["stemid"])
    
            ends[stem["stemid"]]=node2
    
            if (stem["stemid"] > 0) :    
                print("S    {:6d}    {}    RC:i:{}".format(
                            stem["stemid"],
                            (stem['head'] + stem['sequence']).decode("ASCII"),
                            stem["weight"]
                        )
                      )
            
    for stemid1 in ends:
        if stemid1 > 0:
            if ends[stemid1] in begins:
                for stemid2 in begins[ends[stemid1]]:
                    if stemid2 > 0:
                        print('L    {:6d} + {:6d} + *'.format(
                                    stemid1,
                                    stemid2
                                )
                              )

    print(begins)
    print(ends)
    
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

