"""Module for map-matching source linestrings back to the topological graph."""

import math
from itertools import count
from heapq import heappush, heappop
import networkx as nx
from rtree import index
from shapely.geometry import Point
import numpy as np
import logging

logger = logging.getLogger('network-topology')
logger.setLevel(logging.INFO)


def getMatchedRoutes(lineStrings, DG, increment=100., scope=30.):
    """List the segments/edges that best match each linestring."""
    idx = _buildIndex(DG)
    paths = {}
    for i, ls in lineStrings.items():
        logger.info('Matching shape {}'.format(i))
        adjacency_list, s, t = _findCandidatePoints(DG, idx, ls,
                                                    increment=increment,
                                                    scope=scope)
        path = _viterbi_search(adjacency_list, s, t, DG, increment)
        paths[i] = path
    return paths


def _buildIndex(DG):
    shapeIdx = index.Index()
    for u, v, i, data in DG.edges(data=True, keys=True):
        shapeIdx.insert(hash((u, v, i)), data['geom'].bounds, obj=(u, v, i))
    return shapeIdx


def _getDirection(line, distance):
    if distance == line.length:
        n1 = 1. - 1e-9
        n2 = 1.
    else:
        n1 = distance / line.length
        n2 = n1 + 1e-9
    p1 = line.interpolate(n1, normalized=True)
    p2 = line.interpolate(n2, normalized=True)
    return (p2.x - p1.x, p2.y - p1.y)


def _findCandidatePoints(DG, shapeIdx, lineString, increment=100., scope=30.):
    adjacency_list = {}
    totalLength = lineString.length
    s = Candidate(DG, start=True)
    t = Candidate(DG, end=True)
    lastRound = [s]
    adjacency_list[t] = []

    simpleLine = lineString.simplify(scope/2.)
    cornerPts = [Point(c) for c in simpleLine.coords[1:-1]]

    points = [(Point(lineString.coords[0]), _getDirection(lineString, 0))]
    searchRange = [increment, min(increment*2.0, totalLength - increment)]
    failureCount = 0
    while searchRange[1] > searchRange[0]:
        d = np.random.uniform(*searchRange)
        p = lineString.interpolate(d)
        collision = False
        for corner in cornerPts:
            if abs(p.x - corner.x) < scope and abs(p.y - corner.y) < scope:
                if p.distance(corner) < scope:
                    failureCount += 1
                    collision = True
                    break
        if failureCount >= 20:
            searchRange = [searchRange[1],
                           min(searchRange[1]+scope, totalLength-increment)]
            failureCount = 0
        if not collision:
            points.append((p, _getDirection(lineString, d)))
            searchRange = [d + increment,
                           min(d + 2. * increment, totalLength-increment)]
    points.append((Point(lineString.coords[-1]),
                   _getDirection(lineString, totalLength)))

    firstLast = points[::len(points)-1]
    for p, pdir in points:
        nextRound = []
        for item in shapeIdx.intersection((p.x-scope, p.y-scope,
                                           p.x+scope, p.y+scope),
                                          objects=True):
            u, v, i = item.object
            if DG[u][v][i]['terminal'] and p not in firstLast:
                continue
            candidate = Candidate(DG, segment=item.object, measurement=p)
            if candidate.distance < scope:
                sdir = _getDirection(DG[u][v][i]['geom'], candidate.offset)
                if np.dot(pdir, sdir) >= 0:
                    nextRound.append(candidate)
        if nextRound:
            for prev in lastRound:
                adjacency_list[prev] = list(nextRound)
            lastRound = nextRound
            #pprint(nextRound)
    for prev in lastRound:
        adjacency_list[prev] = [t]
    return adjacency_list, s, t


def _viterbi_search(adjacency_list, s, t, DG, increment):
    # With credit to the "Map Matching in a Programmer's Perspective" guide
    # in Valhalla by Mapzen:
    # https://github.com/valhalla/meili/blob/master/docs/meili/algorithms.md

    # Initialize joint probability for each node
    if 'path_cache' not in DG.graph:
        DG.graph['path_cache'] = SequenceCache()
    cost = {}
    for u in adjacency_list:
        cost[u] = 1e100
    predecessor = {}
    queue = PriorityQueue()

    cost[s] = s.emission_cost()
    queue.add_or_update(s, cost[s])
    predecessor[s] = None
    while not queue.empty():
        # Extract node u
        u = queue.pop()
        if u == t:
            break
        for v in adjacency_list[u]:
            # Relaxation
            new_cost = (cost[u] +
                        u.transition_cost(v, DG.graph['path_cache']) +
                        v.emission_cost())
            if cost[v] > new_cost:
                cost[v] = new_cost
                predecessor[v] = u
            queue.add_or_update(v, cost[v])
    return _construct_path(predecessor, s, t, DG, increment)


def _construct_path(predecessor, s, t, DG, increment):
    cache = DG.graph['path_cache']
    cur = predecessor[t]
    sequence = [cur.segment]
    prev = predecessor[cur]
    while prev is not s:
        if not(prev.segment == cur.segment and prev.offset <= cur.offset):
            if (prev.segment[1], cur.segment[0]) in cache:
                cVal = cache[prev.segment[1], cur.segment[0]][1]
                sequence = cVal + sequence
        if (len(sequence) == 0 or sequence[0] != prev.segment):
            sequence.insert(0, prev.segment)
        cur = prev
        prev = predecessor[cur]
    sequence = [(u, v, i) for u, v, i in sequence if not DG[u][v][i]['terminal']]

    duplicates = []
    lastIndex = -10
    for i, (s1, s2) in enumerate(zip(sequence[:-1], sequence[1:])):
        if i == lastIndex:
            continue
        if s1[0] == s2[1] and s1[2] == s2[2]:
            if DG[s1[0]][s1[1]][s1[2]]['geom'].length < increment*4.:
                duplicates.append(i)
                duplicates.append(i+1)
                lastIndex = i + 1

    return [p for i, p in enumerate(sequence) if i not in duplicates]


def _distanceBetweenNodes(G, a, b):
    x1 = G.node[a]['x']
    y1 = G.node[a]['y']
    x2 = G.node[b]['x']
    y2 = G.node[b]['y']
    return math.sqrt((x1-x2)**2. + (y1-y2)**2.)


def _astar_path(G, source, target, weight='length'):
    """Return a list of edges in a shortest path between source and target
    using the A* ("A-star") algorithm.
    There may be more than one shortest path.  This returns only one.
    This code is adapted for multigraph from the networkx library
    Parameters
    ----------
    G : NetworkX graph
    source : node
       Starting node for path
    target : node
       Ending node for path
    heuristic : function
       A function to evaluate the estimate of the distance
       from the a node to the target.  The function takes
       two nodes arguments and must return a number.
    weight: string, optional (default='weight')
       Edge data key corresponding to the edge weight.
    Raises
    ------
    NetworkXNoPath
        If no path exists between source and target.
    Examples
    --------
    >>> G = nx.path_graph(5)
    >>> print(nx.astar_path(G, 0, 4))
    [0, 1, 2, 3, 4]
    >>> G = nx.grid_graph(dim=[3, 3])  # nodes are two-tuples (x,y)
    >>> nx.set_edge_attributes(G, {e: e[1][0]*2 for e in G.edges()}, 'cost')
    >>> def dist(a, b):
    ...    (x1, y1) = a
    ...    (x2, y2) = b
    ...    return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
    >>> print(nx.astar_path(G, (0, 0), (2, 2), heuristic=dist, weight='cost'))
    [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]
    See Also
    --------
    shortest_path, dijkstra_path
    """
    if source not in G or target not in G:
        msg = 'Either source {} or target {} is not in G'
        raise nx.NodeNotFound(msg.format(source, target))

    # if heuristic is None:
    #     # The default heuristic is h=0 - same as Dijkstra's algorithm
    #     def heuristic(u, v):
    #         return 0

    push = heappush
    pop = heappop

    # The queue stores priority, node, cost to reach, and parent.
    # Uses Python heapq to keep in priority order.
    # Add a counter to the queue to prevent the underlying heap from
    # attempting to compare the nodes themselves. The hash breaks ties in the
    # priority and is guarenteed unique for all nodes in the graph.
    c = count()
    queue = [(0, next(c), source, 0, None, None)]

    # Maps enqueued nodes to distance of discovered paths and the
    # computed heuristics to target. We avoid computing the heuristics
    # more than once and inserting the node into the queue too many times.
    enqueued = {}
    # Maps explored nodes to parent closest to the source.
    explored = {}

    while queue:
        # Pop the smallest item from queue.
        _, __, curnode, dist, parent, via = pop(queue)

        if curnode == target:
            path = []
            node = curnode
            edge = via
            while parent is not None:
                path.append((parent, node, edge))
                node = parent
                parent, edge = explored[node]
            path.reverse()
            return path

        if curnode in explored:
            continue

        explored[curnode] = parent, via

        for neighbor, es in G[curnode].items():
            for edge, w in es.items():
                if neighbor in explored:
                    continue
                ncost = dist + w.get(weight, 1)
                if neighbor in enqueued:
                    qcost, h = enqueued[neighbor]
                    # if qcost < ncost, a longer path to neighbor remains
                    # enqueued. Removing it would need to filter the whole
                    # queue, it's better just to leave it there and ignore
                    # it when we visit the node a second time.
                    if qcost <= ncost:
                        continue
                else:
                    h = _distanceBetweenNodes(G, neighbor, target)
                enqueued[neighbor] = ncost, h
                push(queue, (ncost + h, next(c), neighbor, ncost, curnode, edge))

    raise nx.NetworkXNoPath("Node %s not reachable from %s" % (source, target))

SIGMA_Z = 4.07
BETA = 3
INVERSE_2_SIGMA_SQUARED = 1. / (SIGMA_Z ** 2. * 2.)
INVERSE_BETA = 1. / BETA

class Candidate:
    """Class for candidate segment."""

    def __init__(self, DG, segment=None, measurement=None,
                 start=False, end=False):
        """Initialize."""
        self.start = start
        self.end = end
        self.measurement = measurement
        self.segment = segment
        self.DG = DG
        if segment:
            geom = DG.get_edge_data(*segment)['geom']
            self.offset = geom.project(measurement)
            self.distance = geom.distance(measurement)
            self.remaining = geom.length - self.offset
            self.hash = hash((self.segment, self.offset))
        else:
            self.distance = 0
            self.offset = 0
            self.remaining = 0
            if self.start:
                self.hash = hash('start')
            else:
                self.hash = hash('end')


    def __hash__(self):
        """Hash for use as dictionary keys."""
        return self.hash

    def __str__(self):
        """String representation as segment id and offset."""
        return '{}>{}'.format(self.segment, self.offset)

    def __repr__(self):
        """Just use string representation."""
        return self.__str__()

    def emission_cost(self):
        """Gaussian distribution."""
        #c = 1 / (SIGMA_Z * math.sqrt(2 * math.pi))
        #prob = c * math.exp(-(self.distance**2))
        #return -1 * math.log10(max(prob, sys.float_info.min))
        return self.distance ** 2. * INVERSE_2_SIGMA_SQUARED

    def transition_cost(self, nextCandidate, cache):
        """Empirical distribution."""
        if self.measurement is None:
            return nextCandidate.offset
        elif nextCandidate.measurement is None:
            return self.remaining
        #c = 1 / BETA
        route_distance, crossed = self._route_distance_to(nextCandidate, cache)
        delta = abs(route_distance -
                    self.measurement.distance(nextCandidate.measurement))
        # Apply a small bias against changing edges, to avoid swithcing between
        # opposide edges unnecessarily.
        #delta *= 1.000000000001**crossed
        delta += .001 * crossed

        #prob = c * math.exp(-delta*c)
        #return -1 * math.log10(max(prob, sys.float_info.min))
        return delta * INVERSE_BETA

    def _route_distance_to(self, nextCandidate, cache):
        if nextCandidate.segment == self.segment and nextCandidate.offset >= self.offset:
            return nextCandidate.offset - self.offset, 0
        if self.segment is None or nextCandidate.segment is None:
            return 0, 0
        terminalDistance = self.remaining + nextCandidate.offset
        if self.segment[1] == nextCandidate.segment[0]:
            return terminalDistance, 1
        sumDistance = 0
        index = (self.segment[1], nextCandidate.segment[0])
        if index in cache:
            sumDistance, edgeSequence = cache[index]
        else:
            edgeSequence = []
            distances = []
            try:
                sequence = _astar_path(self.DG, self.segment[1],
                                            nextCandidate.segment[0],
                                            weight='length')
                #for u, v in zip(sequence[:-1], sequence[1:]):
                #    i = min(self.DG[u][v],
                #            key=lambda x: self.DG[u][v][x]['length'])
                for u, v, i in sequence:
                    edgeSequence.append((u, v, i))
                    distances.append(self.DG[u][v][i]['length'])
            except nx.NetworkXException:
                distances = [float('inf')]
            #cache[index] = sumDistance, edgeSequence
            cache.add(distances, edgeSequence)
        return sumDistance + terminalDistance, len(edgeSequence) + 1


class PriorityQueue:
    """Priority queue for use in Dijkstra search."""

    REMOVED = '<removed-item>'  # placeholder for a removed item

    def __init__(self):
        """Initialize priority queue."""
        # self.pq = Fibonacci_heap()
        # self.entry_finder = {}
        self.pq = []                       # list of entries arranged in a heap
        self.entry_finder = {}             # mapping of items to entries
        self.counter = count()   # unique sequence count

    def add_or_update(self, item, priority=0):
        """Add a new item or update the priority of an existing item."""
        # if item in self.entry_finder:
        #     self.pq.decrease_key(self.entry_finder[item], priority)
        # else:
        #     entry = self.pq.enqueue(item, priority)
        #     self.entry_finder[item] = entry
        if item in self.entry_finder:
            self.remove(item)
        count = next(self.counter)
        entry = [priority, count, item]
        self.entry_finder[item] = entry
        heappush(self.pq, entry)

    def remove(self, item):
        """Mark an existing item as REMOVED.  Raise KeyError if not found."""
        entry = self.entry_finder.pop(item)
        entry[-1] = self.REMOVED

    def pop(self):
        """Remove and return the lowest priority task. Raise error if empty."""
        while self.pq:
            priority, count, item = heappop(self.pq)
            if item is not self.REMOVED:
                del self.entry_finder[item]
                return item
        raise KeyError('pop from an empty priority queue')
        # item = self.pq.dequeue_min().get_value()
        # return item

    def empty(self):
        """Return true if the priority queue is empty."""
        return len(self.pq) == 0


class SequenceCache(dict):
    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __contains__(self, key):
        s, t = key
        return dict.__contains__(self, (s, t)) or dict.__contains__(self, (t, s))

    def __getitem__(self, key):
        s, t = key
        if dict.__contains__(self, (s, t)):
            return dict.__getitem__(self, key)
        elif dict.__contains__(self, (t, s)):
            length, sequence = dict.__getitem__(self, (t, s))
            sequence = [(v, u, i) for u, v, i in reversed(sequence)]
            return length, sequence
        else:
            raise KeyError(key)

    def add(self, lengths, sequence):
        if sequence:
            s, t = sequence[0][0], sequence[-1][1]
            dict.__setitem__(self, (s, t), (sum(lengths), sequence))
            if len(sequence) > 1:
                s, t = sequence[0][0], sequence[-2][1]
                if (s, t) not in self:
                    self.add(lengths[:-1], sequence[:-1])
                s, t = sequence[1][0], sequence[-1][1]
                if (s, t) not in self:
                    self.add(lengths[1:], sequence[1:])

    # def __setitem__(self, key, sequence):
    #     dict.__setitem__(self, key, sequence)
    #     if len(sequence) > 1:
    #         if

    def __repr__(self):
        dictrepr = dict.__repr__(self)
        return '{}({})'.format(type(self).__name__, dictrepr)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).iteritems():
            self[k] = v
