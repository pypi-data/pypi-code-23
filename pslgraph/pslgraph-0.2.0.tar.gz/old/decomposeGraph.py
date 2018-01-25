# TODO(eriq): Deprecated. Remove once ISI is migrated.

import os
import sys

import networkx

DATA_DIR = 'data'
GRAPH_PREDICATE_PATH = os.path.join(DATA_DIR, 'graph_obs.txt')
BLOCK_PREDICATE_PATH = os.path.join(DATA_DIR, 'block_obs.txt')
EDGE_PREDICATE_PATH = os.path.join(DATA_DIR, 'edge_obs.txt')
LINK_OBS_PREDICATE_PATH = os.path.join(DATA_DIR, 'link_obs.txt')
LINK_PRIOR_OBS_PREDICATE_PATH = os.path.join(DATA_DIR, 'link_prior_obs.txt')
LINK_TARGET_PREDICATE_PATH = os.path.join(DATA_DIR, 'link_target.txt')

def writeTSV(path, rows):
    with open(path, 'w') as file:
        # TODO(eriq): Batch
        for row in rows:
            file.write("\t".join(row) + "\n")

def writeGraph(path, graph, targets):
    graphPredicate = []

    for id in graph.nodes():
        graphPredicate.append([str(graph.node[id]['part']), str(id)])

    writeTSV(path, graphPredicate)

# Write the edges.
# Only edges betwen the same part will be written.
# We refer to edges between parts as "links".
def writeEdges(path, graph, targets):
    edgePredicate = []

    for (source, target) in graph.edges():
        # Skip edges that are links (between different parts).
        if (graph.node[source]['part'] != graph.node[target]['part']):
            continue

        edgePredicate.append([str(source), str(target), str(graph[source][target]['weight'])])

    writeTSV(path, edgePredicate)

def writeLinkObs(path, graph, targets):
    linkPredicate = []

    for (source, target) in graph.edges():
        # Skip edges that are not links (between different parts).
        if (graph.node[source]['part'] == graph.node[target]['part']):
            continue

        # Skip links that are targets.
        if (source in targets and target in targets[source] and targets[source][target]):
            continue

        linkPredicate.append([str(source), str(target), str(graph[source][target]['weight'])])

    writeTSV(path, linkPredicate)

def writeLinkTargets(path, graph, targets):
    linkPredicate = []

    for source in targets:
        for dest in targets[source]:
            linkPredicate.append([str(source), str(dest)])

    writeTSV(path, linkPredicate)

def writeLinkPriorObs(path, graph, targets):
    linkPredicate = []

    for (source, target) in graph.edges():
        # Skip edges that are not links (between different parts).
        if (graph.node[source]['part'] == graph.node[target]['part']):
            continue

        # Skip links that are not targets.
        if (not (source in targets and target in targets[source] and targets[source][target])):
            continue

        linkPredicate.append([str(source), str(target), str(graph[source][target]['weight'])])

    writeTSV(path, linkPredicate)

# We will only consider links that appear in the graph or are targets.
def writeBlocks(path, graph, targets):
    linkPredicate = []

    for (source, target) in graph.edges():
        # Skip edges that are not links (between different parts).
        if (graph.node[source]['part'] == graph.node[target]['part']):
            continue

        # Skip links that are targets.
        if (source in targets and target in targets[source] and targets[source][target]):
            continue

        linkPredicate.append([str(source), str(target)])

    # Now add in all the targets
    for source in targets:
        for dest in targets[source]:
            linkPredicate.append([str(source), str(dest)])

    writeTSV(path, linkPredicate)

def processGraph(graph, targets):
    writeGraph(GRAPH_PREDICATE_PATH, graph, targets)
    writeEdges(EDGE_PREDICATE_PATH, graph, targets)
    writeLinkObs(LINK_OBS_PREDICATE_PATH, graph, targets)
    writeLinkTargets(LINK_TARGET_PREDICATE_PATH, graph, targets)
    writeLinkPriorObs(LINK_PRIOR_OBS_PREDICATE_PATH, graph, targets)
    writeBlocks(BLOCK_PREDICATE_PATH, graph, targets)

# Returns: {source: {dest: true, ...}, ...}
def readTargets(targetPath):
    targets = {}
    with open(targetPath, 'r') as file:
        for line in file:
            source, dest = line.strip().split("\t")
            if (not (source in targets)):
                targets[source] = {}
            targets[source][dest] = True

    return targets

def processFiles(graphPath, targetsPath):
    processGraph(networkx.read_gml(graphPath), readTargets(targetsPath))

def main():
    if (len(sys.argv) != 3):
        print("Expecting exactly two arguments (the graph path and the targets path), got: %d" % (len(sys.argv) - 1))
        sys.exit(1)
    
    processFiles(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
