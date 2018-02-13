from __future__ import print_function
from termcolor import colored
from collections import defaultdict
from plotly.graph_objs import *

import os
import sys
import json
import plotly
import gdsyuna
import pyclipper
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt

masternodes = [1, 2, 3, 4, 5, 6, 8, 11]

def plot_network(layergraphs, g,  args):
    if args['--plot'] == 'all':
        draw_plotly(g, 'netlist_graph')
        # draw_matplotlib(g, 'netlist_graph')
    elif args['--plot'] == 'layers':
        for name, lg in layergraphs.items():
            draw_plotly(lg.g, name)
            # draw_matplotlib(lg.g, name)


def draw_plotly(G, layername):
    edge_trace = Scatter(
        x=[],
        y=[], 
        line=Line(width=0.75, color='#888'),
        hoverinfo='none',
        mode='line')
        
    edge_label_trace = Scatter(
        x=[], 
        y=[], 
        text=[],
        mode='markers', 
        hoverinfo='text',
        marker=Marker(
            color='#6666FF', 
            size=1,         
            line=dict(width=2)))
            
    for e in G.edges():
        x0, y0 = G.node[e[0]]['pos']
        x1, y1 = G.node[e[1]]['pos']
        
        edge_trace['x'] += [x0, x1, None]
        edge_trace['y'] += [y0, y1, None]
        
        x = x0 + (x1-x0)/2.0
        y = y0 + (y1-y0)/2.0
        
        edge_label_trace['x'].append(x)
        edge_label_trace['y'].append(y)
        edge_label_trace['text'].append(G[e[0]][e[1]]['label'])

    node_trace = Scatter(
        x=[], 
        y=[], 
        text=[],
        name='markers',
        mode='markers', 
        hoverinfo='text',
        marker=Marker(
            color=[], 
            size=25,         
            line=dict(width=2)))

    for n in G.nodes():
        x, y = G.node[n]['pos']
        node_trace['x'].append(x)
        node_trace['y'].append(y)
        node_trace['marker']['color'].append(G.node[n]['color']['color'])
        node_trace['text'].append(G.node[n]['layer'])
        # node_trace['text'].append(G.node[n]['type'])
        # node_trace['text'].append(n)

    fig = Figure(data=Data([edge_trace, node_trace, edge_label_trace]),
                layout=Layout(
                title='<br>' + layername,
                titlefont=dict(size=24),
                showlegend=False, 
                width=1200,
                height=1200,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))

    plotly.offline.plot(fig, filename=layername)
    

def draw_matplotlib(g, layername):
    pos = {n: g.nodes[n]['pos'] for n in g.nodes()}
    labels = {n: n for n in g.nodes()}
    # labels = {n: g.node[n]['layer'] for n in g.nodes()}
    # colors = [g.node[n]['color'] for n in g.nodes()]

    nx.draw_networkx_edges(g, pos=pos, edgelist=g.edges(), alpha=0.5, with_labels=True)
    nx.draw_networkx_nodes(g, pos=pos, nodelist=g.nodes(), node_size=600, cmap=plt.cm.jet)
    nx.draw_networkx_labels(g, pos=pos, labels=labels, font_size=8)
    
    plt.title(layername)
    plt.show()


def list_layout_cells(gds):
    """ List the Cells in the GDS layout. """

    gdsii = gdsyuna.GdsLibrary()
    gdsii.read_gds(gds, unit=1.0e-12)

    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print('Cell List:')
    for key, value in gdsii.cell_dict.items():
        print('      -> ' + key)


def convert_node_to_3d(wire):
    layer = np.array(wire).tolist()

    polygons = []
    for pl in layer:
        poly = [[float(y*10e-9) for y in x] for x in pl]
        for row in poly:
            row.append(0.0)
        polygons.append(poly)
    return polygons


def convert_node_to_2d(layer):
    um = 10e7

    layer = list(layer)
    del layer[2]

    layer[0] = layer[0] * um
    layer[1] = layer[1] * um

    return layer


def parameter_print(arguments):
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print ('Parameters:')
    for key, value in arguments.items():
        print('      ' + str(key) + ' : ' + str(value))


def red_print(header):
    """ Main program header (Red) """
    print ('\n' + '[' + colored('*', 'red', attrs=['bold']) + '] ', end='')
    print(header)


def magenta_print(header):
    """ Python package header (Purple) """
    print ('\n' + '[' + colored('*', 'magenta', attrs=['bold']) + '] ', end='')
    print ('--- ' + header + ' ----------')


def green_print(header):
    """ Function header (Green) """
    print ('\n  ' + '[' + colored('*', 'green', attrs=['bold']) + '] ', end='')
    print(header)


def cyan_print(header):
    """ Function header (Green) """
    print ('\n[' + colored('*', 'cyan', attrs=['bold']) + '] ', end='')
    print(header)
