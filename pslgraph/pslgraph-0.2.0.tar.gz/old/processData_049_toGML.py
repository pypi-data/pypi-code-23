# TODO(eriq): Deprecated. Remove once ISI is migrated.

# Parse the raw data into the GML format that we will expect from a TA2.

import operator
import os
import sys

import networkx

# HACK(eriq): This is a bit messy, pulling the data dir off the ARGV outside of actual methods.
SEED_DATA_DIR = os.path.join('..', 'data', 'seed_datasets', 'r_49', 'data')

RAW_DATA_DIR = os.path.join(SEED_DATA_DIR, 'raw_data')
G1_PATH = os.path.join(RAW_DATA_DIR, 'G1.gml')
G2_PATH = os.path.join(RAW_DATA_DIR, 'G2.gml')
OBSERVED_LINKS_G1_PATH = os.path.join(SEED_DATA_DIR, 'trainData.csv')
OBSERVED_LINKS_G2_PATH = os.path.join(SEED_DATA_DIR, 'trainTargets.csv')

OUT_DATA_DIR = os.path.join('data', 'rawData')
GRAPH_PATH = os.path.join(OUT_DATA_DIR, 'graph.gml')
TARGETS_PATH = os.path.join(OUT_DATA_DIR, 'targets.txt')

NODE_ID_FIELD = 'id'
NODE_LABEL_FIELD = 'nodeID'
FEATURE_FIELDS = ['f0', 'f1', 'f2', 'f3', 'f4']

BLOCKING_TOP_SIM_COUNT = 10

# Returns:
#  - nodes: {id: {attributes}, ...}
#  - edges: {source: {target: T/F, ...}, ...}
# Symetric edges will be added.
# To ensure node id's are unique, we will prepend the graph identifier to each id.
def parseGraph(graph, graphId):
    # {id: {attributes}, ...}
    nodes = {}

    # {GMLId (NODE_ID_FIELD): graphId::id}
    nodeIdMapping = {}

    # {source: {target: T/F, ...}, ...}
    edges = {}

    # Fetch the nodes and build the id mapping.
    for nodeId in graph.nodes():
        newId = "%s::%s" % (graphId, graph.node[nodeId][NODE_LABEL_FIELD])
        nodeIdMapping[nodeId] = newId

        node = {}
        for featureField in FEATURE_FIELDS:
            node[featureField] = float(graph.node[nodeId][featureField])
        nodes[newId] = node

    # Fetch the edges (also add reverse edges)
    for (rawSource, rawTarget) in graph.edges():
        source = nodeIdMapping[rawSource]
        target = nodeIdMapping[rawTarget]

        if (not (source in edges)):
            edges[source] = {}

        if (not (target in edges)):
            edges[target] = {}

        edges[source][target] = True
        edges[target][source] = True

    return nodes, edges

# Will only get the top BLOCKING_TOP_SIM_COUNT sims for each node.
# Returns: {id1: {id2: similarity, ...}, ...}
def getSimilarities(g1Nodes, g2Nodes):
    # {id1: {id2: [distance, ...], ...}, ...}
    # id1 < id2
    distances = {}

    for featureKey in FEATURE_FIELDS:
        minVal = None
        maxVal = None

        for (id1, node1) in g1Nodes.items():
            for (id2, node2) in g2Nodes.items():
                if (id1 >= id2):
                    continue
                
                distance = abs(node1[featureKey] - node2[featureKey])

                if (minVal == None or distance < minVal):
                    minVal = distance

                if (maxVal == None or distance > maxVal):
                    maxVal = distance

                if (not (id1 in distances)):
                    distances[id1] = {}

                if (not (id2 in distances[id1])):
                    distances[id1][id2] = []

                distances[id1][id2].append(distance)

        # Just do a min/max normalization into a similarity.
        # TODO(eriq): Better normalization here can go a long way.
        rangeVal = float(maxVal - minVal)
        for (id1, id2Distances) in distances.items():
            for (id2, pairDistances) in id2Distances.items():
                distance = pairDistances[-1]
                pairDistances[-1] = (1.0 - min(1.0, max(0.0, float(distance - minVal) / rangeVal)))

    # For now, just combine the similarities into a single metric.
    # Just get the mean or the normalized values, but we could also do
    # something like a logistic regression on the raw values.
    for (id1, id2Sims) in distances.items():
        for (id2, pairSims) in id2Sims.items():
            distances[id1][id2] = float(sum(pairSims)) / len(pairSims)

    blockedSims = {}

    # For blocking purposes, choose the top N similarities for each node.
    for (id1, sims) in distances.items():
        sims = list(sims.items())
        sims.sort(reverse = True, key = operator.itemgetter(1))
        blockedSims[id1] = dict(sims[0:BLOCKING_TOP_SIM_COUNT])

    return blockedSims

def constructGraph(g1Nodes, g1Edges, g2Nodes, g2Edges, crosspartEdges):
    graph = networkx.Graph()

    # Start with all the nodes.
    for id in g1Nodes:
        graph.add_node(id, id = id, part = 1)

    for id in g2Nodes:
        graph.add_node(id, id = id, part = 2)

    # Now add all inter-part edges.
    # In the facebook data, these are all full-strength edges.
    for edges in [g1Edges, g2Edges]:
        for (source, targets) in edges.items():
            for target in targets:
                if (source >= target):
                    continue
                graph.add_edge(source, target, weight = 1.0)

    # Add known (full weight) resolutions.
    seenCrosspartEdges = {}
    for (source, target) in crosspartEdges:
        if (source >= target):
            continue

        seenCrosspartEdges["%s_%s" % (source, target)] = True
        graph.add_edge(source, target, weight = 1.0)

    # Add computed similarities.
    # Note that we will not add sims for edges we already have.
    similarities = getSimilarities(g1Nodes, g2Nodes)

    # Every edge that we wite a similarity for is also a target.
    with open(TARGETS_PATH, 'w') as targetsFile:
        for (source, sims) in similarities.items():
            for (target, sim) in sims.items():
                if (source >= target):
                    continue

                if (("%s_%s" % (source, target)) in seenCrosspartEdges):
                    continue

                graph.add_edge(source, target, weight = sim)
                targetsFile.write("\t".join([source, target]) + "\n")

    networkx.write_gml(graph, GRAPH_PATH)

def readCrosspartEdges():
    g1Nodes = []
    g2Nodes = []

    work = [
        (OBSERVED_LINKS_G1_PATH, g1Nodes, '1'),
        (OBSERVED_LINKS_G2_PATH, g2Nodes, '2')
    ]

    for (path, nodes, prefix) in work:
        with open(path, 'r') as file:
            # The file format is sometimes inconsistent, so pick up the header
            # so we can tell which column we want.
            header = next(file)

            targetColumn = 2  # The normal index.
            columnNames = header.strip().split(',')
            for i in range(len(columnNames)):
                if (columnNames[i].endswith('.nodeID')):
                    targetColumn = i
                    break

            for line in file:
                parts = line.strip().split(',')
                nodes.append("%s::%s" % (prefix, parts[targetColumn]))

    return list(zip(g1Nodes, g2Nodes)) + list(zip(g2Nodes, g1Nodes))

# Take in all the data after it has been extracted from files and do
# the actual processing and writing to output files.
def processData(graph1, graph2, crosspartEdges):
    g1Nodes, g1Edges = parseGraph(graph1, '1')
    g2Nodes, g2Edges = parseGraph(graph2, '2')

    os.makedirs(OUT_DATA_DIR, exist_ok = True)
    constructGraph(g1Nodes, g1Edges, g2Nodes, g2Edges, crosspartEdges)

def main(seedDataDir = None):
    # Re-init all the raw data paths if we got a new dir.
    if (seedDataDir != None):
        global SEED_DATA_DIR
        global RAW_DATA_DIR
        global G1_PATH
        global G2_PATH
        global OBSERVED_LINKS_G1_PATH
        global OBSERVED_LINKS_G2_PATH

        SEED_DATA_DIR = seedDataDir
        RAW_DATA_DIR = os.path.join(SEED_DATA_DIR, 'raw_data')
        G1_PATH = os.path.join(RAW_DATA_DIR, 'G1.gml')
        G2_PATH = os.path.join(RAW_DATA_DIR, 'G2.gml')
        OBSERVED_LINKS_G1_PATH = os.path.join(SEED_DATA_DIR, 'trainData.csv')
        OBSERVED_LINKS_G2_PATH = os.path.join(SEED_DATA_DIR, 'trainTargets.csv')

    graph1 = networkx.read_gml(G1_PATH, label = NODE_LABEL_FIELD)
    graph2 = networkx.read_gml(G2_PATH, label = NODE_LABEL_FIELD)

    crosspartEdges = readCrosspartEdges()

    processData(graph1, graph2, crosspartEdges)

if __name__ == '__main__':
    seedDataDir = None
    if (len(sys.argv) > 1):
        seedDataDir = sys.argv[1]

    main(seedDataDir)
