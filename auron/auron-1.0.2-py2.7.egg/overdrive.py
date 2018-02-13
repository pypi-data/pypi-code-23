"""

Usage:
    auron <process> <testname> <ldf> [--cell=<cellname>] [--filter] [--plot=<layer>]
    auron (-h | --help)
    auron (-V | --version)

Options:
    -h --help     Show this screen.
    -p --pretty   Prettify the output.
    -V --version  Show version.
    --quiet       print less text
    --verbose     print more text

"""

import sys

from docopt import docopt
from itertools import count
from yuna import tools as yt
from auron import version

import filters
import graphlvs
import tools
import yuna
import os
import gdsyuna
import meshio
import subprocess
import networkx as nx
import pygmsh as pg
import numpy as np


"""
Hacker: 1h3d*n
For: Volundr
Docs: Algorithm 1
Date: 31 April 2017

Description: Morph the moat layer and the wire layers.

1) Get a list of all the polygons inside the GDS file.
2) Send this list to the Clip library with the wiring
   layer number and the moat layer number as parameters.
3) Get the union of all the wiring layer polygons that
   are connected. Update this to check for vias.
4) Get the intersection of the moat layer with the
   wiring layer and save this in a new polygon.
5) Get the difference of the moat layer with the
   wiring layer and save this in a new polygon.
6) Join the intersected and difference polygons
   to form a list of atleast 3 polygons.
7) We now know which part of the wiring layer
   goes over the moat is most probably mutually
   connected to wiring layer 2.
8) Send this polygon structure to GMSH.
"""


def bushido():
    """  """

    args = docopt(__doc__, version=version.__version__)
    tools.red_print('Summoning Auron...')
    tools.parameter_print(args)

    examdir = os.getcwd() + '/tests/' + args['<process>'] + '/' + args['<testname>']
    gds_file = examdir + '/' + args['<testname>'] + '.gds'

    if args['--cell']:
        layoutcell, configdata = yuna.grand_summon(args, '')

        layergraphs = generate_lvs_network(layoutcell, configdata, args)

        G = combine_graphs(layergraphs, configdata['Params'])
        
        H = graph_to_netlist(G)

        tools.plot_network(layergraphs, H, args)
    else:
        tools.list_layout_cells(gds_file)
    
    tools.red_print('Auron. Done.')
    

def relabel_series_nodes(g, branches, Params, phase):
    if phase == 1:
        for n in g.nodes():
            e = [i for i in g[n]]
            if len(e) == 2:
                g.node[n]['type'] = 12
                g.node[n]['layer'] = 'S_' + str(n)
                g.node[n]['color'] = Params['LAYER']
    elif phase == 2:
        for key, branch in branches.items():
            edgenode_1 = branch[0]
            edgenode_2 = branch[-1]
            for n in branch:
                if g.node[n]['type'] == 12:
                    g.node[n]['type'] = 13
                    g.node[n]['layer'] = g.node[edgenode_1]['layer'] + '__' + g.node[edgenode_2]['layer']
                    g.node[n]['color'] = Params['LAYER']
            
            
def series_node_removal(g):
    """  """
    remove = list()
    for n in g.nodes():
        if g.node[n]['type'] == 13:
            e = [i for i in g[n]]
            g.add_edge(e[0], e[1])
            remove.append(n)

    g.remove_nodes_from(remove)
    

def is_node_grounded(g, n):
    # TODO: We have to update the ground terminal connections.
    if g.node[n]['type'] == 1:
        if len([i for i in g.neighbors(n)]) == 1:
            return True
        else:
            return False

    
def graph_to_netlist(g):
    G = g.copy()
    
    mfile = open('testfile.txt', 'w') 
 
    mfile.write('* Inductances\n')
    for i, e in enumerate(G.edges()):
        G[e[0]][e[1]]['label'] = 'L' + str(i)

        n1, n2 = None, None
        if is_node_grounded(G, e[0]):
            n1 = '0'
        else:
            n1 = str(e[0])
        
        if is_node_grounded(G, e[1]):
            n2 = '0'
        else:
            n2 = str(e[1])

        if n1 == '0':
            mfile.write('L' + str(i) + '\t' + n2 + '\t' + n1 + '\n')
        elif n2 == '0':
            mfile.write('L' + str(i) + '\t' + n1 + '\t' + n2 + '\n')
        else:
            mfile.write('L' + str(i) + '\t' + n1 + '\t' + n2 + '\n')
        
    num = 0
    mfile.write('\n* Ports\n')
    for n in G.nodes():
        if g.node[n]['type'] == 2:
            portname = g.node[n]['layer'].split(' ')[0]
            mfile.write(portname + '\t' + str(n) + '\t' + '0' + '\n')
            num += 1
    
    mfile.write('.end')
    mfile.close()
    
    return G
    

def layer_graph(ugds, layoutcell, configdata, layername):
    """ Generating the individual layer graphs."""
    tools.magenta_print('Generating layer graphs')
    
    gds = int(ugds)
    layoutwires = layoutcell.get_polygons(True)
    layoutlabels = layoutcell.get_labels(0)
        
    g = nx.Graph()
    mgraph = graphlvs.LayerGraph(g, layoutlabels)

    mgraph.generate_mesh(layername, layoutwires, gds)

    mgraph.add_network_edge()
    mgraph.add_network_nodes()
    mlabels = mgraph.add_network_labels(configdata, gds, layoutcell)

    return mgraph, mlabels


def generate_lvs_network(layoutcell, configdata, args):
    graphs = dict()

    for gds, layer in configdata['Layers'].items():
        # TODO: Add the skyplane and gndplane
        mtype = ['wire', 'shunt']
        if layer['type'] in mtype:
            mgraph, mlabels = layer_graph(gds, layoutcell, configdata, layer['name'])

            if mgraph is not None:
                if args['--filter']:
                    tools.green_print('Applying graph node filter')
                    
                    """ First filtering:
                    This filters the minor noise nodes 
                    and added the userdefined nodes. """
                    mgraph.g = get_quotient_nodes(mgraph.g)
                    filters.create_conducting_paths(mgraph.g)

                    mgraph.g = mlabels.get_loops(mgraph.g, configdata)
                    mgraph.g = get_quotient_nodes(mgraph.g)
                    filters.create_conducting_paths(mgraph.g)
                    mlabels.user_triangles(mgraph.g)
                    
                    """ Second filtering:
                    Once the usernodes are added, we
                    have to filter the network again
                    and relabel the branch nodes.
                    Group label the nodes for the quotient graph. """
                    branches = filters.create_conducting_paths(mgraph.g)
                    mlabels.wire_nodes(mgraph.g, branches)
                    mgraph.g = get_quotient_nodes(mgraph.g)

                graphs[layer['name']] = mgraph

    return graphs

    
def combine_graphs(graphs, Params):
    """ Read in Mesh and manipulate it from here on out. """
    layergraphs = [lg.g for key, lg in graphs.items()]
    g = nx.disjoint_union_all(layergraphs)
    
    G = get_quotient_nodes(g)

    relabel_series_nodes(G, None, Params, 1)
    branches = filters.create_conducting_paths(G)
    relabel_series_nodes(G, branches, Params, 2)

    H = get_quotient_nodes(G)

    series_node_removal(H)

    return H
    

def get_quotient_nodes(g):
    """ Combine all nodes of the same type into one node. """
    
    def partition_nodes(u, v):
        masternodes = [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 13]
        if g.node[u]['type'] in masternodes:
            if g.node[u]['layer'] == g.node[v]['layer']:
                return True

    def sub_nodes(b):
        S = g.subgraph(b)
        color = nx.get_node_attributes(S, 'color')
        layer = nx.get_node_attributes(S, 'layer')
        center = nx.get_node_attributes(S, 'pos')
        mtype = nx.get_node_attributes(S, 'type')

        sub_pos = list()
        for key, value in center.items():
            sub_pos = [value[0], value[1]]
            
        return dict(color=color, layer=layer, pos=sub_pos, type=mtype)

    Q = nx.quotient_graph(g, partition_nodes, node_data=sub_nodes, edge_data=None)
    
    Pos = nx.get_node_attributes(Q, 'pos')
    Color = nx.get_node_attributes(Q, 'color')
    Layer = nx.get_node_attributes(Q, 'layer')
    Type = nx.get_node_attributes(Q, 'type')
    Edges = nx.get_edge_attributes(Q, 'weight')
    
    g1 = nx.Graph()
    
    for key, value in Edges.items():
        n1, n2 = list(key[0]), list(key[1])
        g1.add_edge(n1[0], n2[0])
        
    for n in g1.nodes():
        for key, value in Pos.items():
            if n == list(key)[0]:
                g1.node[n]['pos'] = [value[0], value[1]]
        for key, value in Color.items():
            if n == list(key)[0]:
                g1.node[n]['color'] = value[n]
        for key, value in Layer.items():
            if n == list(key)[0]:
                g1.node[n]['layer'] = value[n]
        for key, value in Type.items():
            if n == list(key)[0]:
                g1.node[n]['type'] = value[n]
    return g1
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
