# qa_graphs.py
# Created by Greg Kiar on 2016-05-11.
# Edited by Eric Bridgeford.
# Edited by Coleman Zhang
# Email: gkiar@jhu.edu

from __future__ import print_function
from argparse import ArgumentParser
from collections import OrderedDict
from scipy.stats import gaussian_kde, rankdata

import numpy as np
import nibabel as nb
import networkx as nx
import pickle
import sys
import os

def loadGraphs(filenames, atlas = None, verb=False):
    """
    Given a list of files, returns a dictionary of graphs
    Required parameters:
        filenames:
            - List of filenames for graphs
    Optional parameters:
        atlas:
            - Name of atlas of interest as it appears in the directory titles
        verb:
            - Toggles verbose output statements
    """
    #  Initializes empty dictionary
    if type(filenames) is not list:
        filenames = [filenames]
    gstruct = OrderedDict()
    for idx, files in enumerate(filenames):
        if verb:
            print("Loading: " + files)
        #  Adds graphs to dictionary with key being filename
        fname = os.path.basename(files)
        try:
            gstruct[fname] = nx.read_graphml(files)
        except:
            gstruct[fname] = nx.read_gpickle(files)
    return gstruct

def compute_metrics(fs, verb=False, modality='dwi'):
    """
    Given a set of files and a directory to put things, loads graphs and
    performs set of analyses on them, storing derivatives in a pickle format
    in the desired output location.
    Required parameters:
        fs:
            - List of filenames (string) in each dataset
    Optional parameters:
        verb:
            - Toggles verbose output statements
        modality:
            - Default: 'dwi'; but can also be 'func'
    Output:
        statsDict:
            - A dictionary of summary statistics of fs
    """
    gr = loadGraphs(fs, verb=verb)
    if modality == 'func':
        graphs = binGraphs(gr)
    else:
        graphs = gr
 
    nodes = nx.number_of_nodes(graphs.values()[0])
    #  Number of non-zero edges (i.e. binary edge count)
    print("Computing: NNZ")
    nnz = OrderedDict((subj, len(nx.edges(graphs[subj]))) for subj in graphs)
    statsDict = {'number_non_zeros': nnz}
    print("Sample Mean: %.2f" % np.mean(nnz.values()))

    # Scan Statistic-1
    print("Computing: Max Local Statistic Sequence")
    temp_ss1 = scan_statistic(graphs, 1)
    ss1 = temp_ss1
    statsDict['locality_statistic'] = ss1
    show_means(temp_ss1)

    if modality == 'func':
        graphs = rankGraphs(gr)
        wt_args = {'weight': 'weight'}
    else:
        wt_args = {}

    #   Clustering Coefficients
    print("Computing: Clustering Coefficient Sequence")
    temp_cc = OrderedDict((subj, nx.clustering(graphs[subj],
                                               **wt_args).values())
                          for subj in graphs)
    ccoefs = temp_cc
    statsDict['clustering_coefficients'] = ccoefs
    show_means(temp_cc)

    #  Degree sequence
    print("Computing: Degree Sequence")
    total_deg = OrderedDict((subj, np.array(nx.degree(graphs[subj],
                                                      **wt_args).values()))
                            for subj in graphs)
    ipso_deg = OrderedDict()
    contra_deg = OrderedDict()
    for subj in graphs:  # TODO GK: remove forloop and use comprehension maybe?
        g = graphs[subj]
        N = len(g.nodes())
        LLnodes = g.nodes()[0:N/2]  # TODO GK: don't assume hemispheres
        LL = g.subgraph(LLnodes)
        LLdegs = [LL.degree(**wt_args)[n] for n in LLnodes]

        RRnodes = g.nodes()[N/2:N]  # TODO GK: don't assume hemispheres
        RR = g.subgraph(RRnodes)
        RRdegs = [RR.degree(**wt_args)[n] for n in RRnodes]

        LRnodes = g.nodes()
        ipso_list = LLdegs + RRdegs
        degs = [g.degree(**wt_args)[n] for n in LRnodes]
        contra_deg[subj] = [a_i - b_i for a_i, b_i in zip(degs, ipso_list)]
        ipso_deg[subj] = ipso_list
        # import pdb; pdb.set_trace()

    deg = {'total_deg': total_deg,
           'ipso_deg': ipso_deg,
           'contra_deg': contra_deg}
    statsDict['degree_distribution'] = deg
    show_means(total_deg)

    #  Edge Weights
    if modality == 'dwi':
        print("Computing: Edge Weight Sequence")
        temp_ew = OrderedDict((s, [graphs[s].get_edge_data(e[0], e[1])['weight']
                               for e in graphs[s].edges()]) for s in graphs)
        ew = temp_ew
        statsDict['edge_weight'] = ew
        show_means(temp_ew)
    else:
        temp_pl = OrderedDict()
        print("Computing: Path Length Sequence")
        nxappl = nx.all_pairs_dijkstra_path_length
        for s in graphs:
            apd = nxappl(graphs[s])
            # iterate over the nodes to find the average distance to each node
            avg_path = [np.nanmean(v.values()) for k, v in apd.iteritems()]
            temp_pl[s] = np.array(avg_path)
        pl = temp_pl
        statsDict['path_length'] = pl
        show_means(pl)

    # Eigen Values
    print("Computing: Eigen Value Sequence")
    laplac = OrderedDict((subj, nx.normalized_laplacian_matrix(graphs[subj]))
                         for subj in graphs)
    eigs = OrderedDict((subj, np.sort(np.linalg.eigvals(laplac[subj].A))[::-1])
                       for subj in graphs)
    statsDict['eigen_sequence'] = eigs
    print("Subject Maxes: " + ", ".join(["%.2f" % np.max(eigs[key])
                                         for key in eigs.keys()]))

    # Betweenness Centrality
    print("Computing: Betweenness Centrality Sequence")
    nxbc = nx.algorithms.betweenness_centrality  # For PEP8 line length...
    temp_bc = OrderedDict((subj, nxbc(graphs[subj], **wt_args).values())
                          for subj in graphs)
    centrality = temp_bc
    statsDict['betweenness_centrality'] = centrality
    show_means(temp_bc)

    # Mean connectome
    print("Computing: Mean Connectome")
    nxnp = nx.to_numpy_matrix
    adj = OrderedDict((subj, nxnp(graph, nodelist=sorted(graph.nodes())))
                      for subj, graph in graphs.iteritems())
    mat = np.zeros(adj.values()[0].shape)
    for subj in adj:
        mat += adj[subj]
    mat = mat/len(adj.keys())
    statsDict['study_mean_connectome'] = mat
    return statsDict


def show_means(data):
    print("Subject Means: " + ", ".join(["%.2f" % np.mean(data[key])
                                         for key in data.keys()]))

def binGraphs(graphs, thr=0.1):
    """
    Binarizes a set of graphs given a threshold.
    Required Parameters:
        graphs:
            - a list of graphs.
        thr:
            - the threshold below which edges will be assumed disconnected.
              .1 is chosen as default according to discriminability results.
    """
    binGraphs = {}
    for subj, graph in graphs.iteritems():
        bin_graph = nx.Graph()
        for (u, v, d) in graph.edges(data=True):
            if d['weight'] > thr:
                bin_graph.add_edge(u, v, weight=1)
        binGraphs[subj] = bin_graph
    return binGraphs


def rankGraphs(graphs):
    """
    Ranks the edges in each element of a list of graphs.
    Required Parameters:
        graphs:
            - a list of graphs.
    """
    rankGraphs = {}
    for subj, graph in graphs.iteritems():
        rgraph = nx.Graph()
        edge_ar = np.asarray([x[2]['weight'] for x in graph.edges(data=True)])
        rank_edge = rankdata(edge_ar)  # rank the edges
        for ((u, v, d), rank) in zip(graph.edges(data=True), rank_edge):
            rgraph.add_edge(u, v, weight=rank)
        rankGraphs[subj] = rgraph
    return rankGraphs


def scan_statistic(mygs, i):
    """
    Computes scan statistic-i on a set of graphs
    Required Parameters:
        mygs:
            - Dictionary of graphs
        i:
            - which scan statistic to compute
    """
    ss = OrderedDict()
    for key in mygs.keys():
        g = mygs[key]
        tmp = np.array(())
        for n in g.nodes():
            sg = nx.ego_graph(g, n, radius=i)
            tmp = np.append(tmp, np.sum([sg.get_edge_data(e[0], e[1])['weight']
                            for e in sg.edges()]))
        ss[key] = tmp
    return ss


def density(data, nbins=500, rng=None):
    """
    Computes density for metrics which return vectors
    Required parameters:
        data:
            - Dictionary of the vectors of data
    """
    density = OrderedDict()
    xs = OrderedDict()
    for subj in data:
        hist = np.histogram(data[subj], nbins)
        hist = np.max(hist[0])
        dens = gaussian_kde(data[subj])
        if rng is not None:
            xs[subj] = np.linspace(rng[0], rng[1], nbins)
        else:
            xs[subj] = np.linspace(0, np.max(data[subj]), nbins)
        density[subj] = dens.evaluate(xs[subj])*np.max(data[subj]*hist)
    return {"xs": xs, "pdfs": density}


def main():
    """
    Argument parser and directory crawler. Takes organization and atlas
    information and produces a dictionary of file lists based on datasets
    of interest and then passes it off for processing.
    Required parameters:
        atlas:
            - Name of atlas of interest as it appears in the directory titles
        basepath:
            - Basepath for which data can be found directly inwards from
        outdir:
            - Path to derivative save location
    Optional parameters:
        fmt:
            - Determines file organization; whether graphs are stored as
              .../atlas/dataset/graphs or .../dataset/atlas/graphs. If the
              latter, use the flag.
        verb:
            - Toggles verbose output statements
    """
    parser = ArgumentParser(description="Computes Graph Metrics")
    parser.add_argument("atlas", action="store", help="atlas directory to use")
    parser.add_argument("indir", action="store", help="base directory loc")
    parser.add_argument("-f", "--fmt", action="store_true", help="Formatting \
                        flag. True if bc1, False if greg's laptop.")
    parser.add_argument("-v", "--verb", action="store_true", help="")
    result = parser.parse_args()

    #  Sets up directory to crawl based on the system organization you're
    #  working on. Which organizations are pretty clear by the code, methinks..
    indir = result.indir
    atlas = result.atlas

    #  Crawls directories and creates a dictionary entry of file names for each
    #  dataset which we plan to process.
    fs = [indir + "/" + fl
          for root, dirs, files in os.walk(indir)
          for fl in files
          if fl.endswith(".graphml") or fl.endswith(".gpickle")]
    #  The fun begins and now we load our graphs and process them.
    compute_metrics(fs, atlas, result.verb)


if __name__ == "__main__":
    main()