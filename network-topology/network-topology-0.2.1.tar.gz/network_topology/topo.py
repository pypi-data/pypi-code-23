"""Module for creating a simplified graph from a set of linestrings."""

import networkx as nx
from triangle import triangulate
from shapely.geometry import LineString, Point, Polygon, MultiPolygon, mapping
from shapely.ops import cascaded_union
from itertools import combinations
import numpy as np
import random
from rtree import index
import logging
import json
import pyproj
from shapely.ops import transform
from functools import partial
import os

logger = logging.getLogger('network-topology')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
logger.addHandler(ch)


def getNetworkTopology(lineStrings, thickness=14.0, splitAtTeriminals=None,
                       turnThreshold=20.0, minInnerPerimeter=200,
                       debugFolder=None):
    """Generate a bidirectional graph of the topology created by the lines."""
    # Make buffered shape
    big_shape = _makeBufferedShape(lineStrings, thickness, minInnerPerimeter)
    if debugFolder:
        _dumpBigShape(big_shape, debugFolder)

    triangles = _triangulate(big_shape, lineStrings, thickness,
                             minInnerPerimeter)
    if debugFolder:
        _dumpTriangles(triangles, debugFolder)

    polygons = _polygonize(triangles, big_shape)
    if debugFolder:
        _dumpPolygons(polygons, triangles, debugFolder)

    poly_graph = _buildInitialGraph(polygons)
    _tidyIntersections(poly_graph, triangles, polygons)
    skel_graph = _buildSkeletonGraph(poly_graph, triangles, polygons)
    if splitAtTeriminals:
        _insertAtTerminals(skel_graph, splitAtTeriminals)
    graph = _simplifyGraph(skel_graph, turnThreshold, thickness/100.0)
    # _findSegmentsAndIntersections(skel_graph, turnThreshold)
    return graph


def _makeBufferedShape(lineStrings, thickness=14.0, minInnerPerimeter=200):
    logger.info('Creating buffered shape')
    bufferedShapes = []
    buf = thickness / 2.0
    for ls in lineStrings:
        bufferedShapes.append(ls.buffer(buf, resolution=2, join_style=3))
    big_shape = cascaded_union(bufferedShapes)
    if big_shape.geom_type == 'MultiPolygon':
        filled_shape = MultiPolygon([[g.exterior.coords,
                                     [ring.coords for ring in g.interiors
                                      if ring.length > minInnerPerimeter]]
                                     for g in big_shape.geoms])
    else:
        filled_shape = Polygon(big_shape.exterior.coords,
                               [ring.coords for ring in big_shape.interiors
                                if ring.length > minInnerPerimeter])
    bs = filled_shape.simplify(thickness/10.0)
    logger.info('Completed buffered shape')
    return bs


def _triangulate(big_shape, lineStrings, thickness=14.0, minInnerPerimeter=200):
    logger.info('Reticulating shape')
    tri = {
        'vertices': [],
        'segments': []
        }
    if big_shape.geom_type == 'MultiPolygon':
        geoms = big_shape.geoms
    else:
        geoms = [big_shape]
    for shape in geoms:
        lastIndex = len(tri['vertices'])
        tri['vertices'].append(list(shape.exterior.coords[0]))
        for x, y in shape.exterior.coords[1:]:
            if [x, y] in tri['vertices']:
                currentIndex = tri['vertices'].index([x, y])
            else:
                currentIndex = len(tri['vertices'])
                tri['vertices'].append([x, y])
            tri['segments'].append([lastIndex, currentIndex])
            lastIndex = currentIndex

        if shape.interiors and 'holes' not in tri:
            tri['holes'] = []
        for ring in shape.interiors:
            if ring.length > minInnerPerimeter:
                x, y = 0, 0
                minx, miny, maxx, maxy = ring.bounds
                while not Polygon(ring).contains(Point(x, y)):
                    x = random.uniform(minx, maxx)
                    y = random.uniform(miny, maxy)
                tri['holes'].append([x, y])
                lastIndex = len(tri['vertices'])
                tri['vertices'].append(list(ring.coords[0]))
                for x, y in ring.coords[1:]:
                    if [x, y] in tri['vertices']:
                        currentIndex = tri['vertices'].index([x, y])
                    else:
                        currentIndex = len(tri['vertices'])
                        tri['vertices'].append([x, y])
                    tri['segments'].append([lastIndex, currentIndex])
                    lastIndex = currentIndex

    for ls in lineStrings:
        if ls.geom_type == 'LineString':
            geoms = [ls]
        else:
            geoms = ls.geoms
        for geom in geoms:
            for i in [0, -1]:
                coords = list(geom.coords[i])
                if coords not in tri['vertices']:
                    tri['vertices'].append(coords)
    tri = triangulate(tri, 'pq0Da{}i'.format(thickness**2.0))
    logger.info('Reticulating complete')
    return tri


def _polygonize(res, big_shape):
    logger.info('Removing internal nodes')
    interior_pts = {}
    for i, v in enumerate(res['vertex_markers']):
        if v == 0:
            interior_pts[i] = []
    for tri, pts in enumerate(res['triangles']):
        for p in pts:
            if p in interior_pts:
                interior_pts[p].append(tri)
    connectivity_graph = nx.Graph()
    for tris in interior_pts.values():
        if len(tris) > 0:
            for tri in tris[1:]:
                connectivity_graph.add_edge(tris[0], tri)
    polys = []
    for cluster in list(nx.connected_components(connectivity_graph)):
        shape_graph = nx.Graph()
        for tri in cluster:
            for v1, v2 in zip(res['triangles'][tri],
                              list(res['triangles'][tri][1:]) +
                              [res['triangles'][tri][0]]):
                if v1 not in interior_pts and v2 not in interior_pts:
                    shape_graph.add_edge(v1, v2)

        poly = []
        pt = shape_graph.nodes().keys()[0]
        while pt not in poly:
            poly.append(pt)
            for neighbour in shape_graph.neighbors(pt):
                if neighbour not in poly and len(shape_graph[neighbour]) != 1:
                    pt = neighbour
                    break
        polys.append(poly)
    remaining_triangles = [list(vs) for i, vs in enumerate(res['triangles'])
                           if i not in connectivity_graph]
    return remaining_triangles + polys


def _mergeShapes(cluster, TG, polys):
    combined_graph = nx.Graph()
    for shape in cluster:
        if len(polys[shape]) == 0:
            continue
        for p1, p2 in zip(polys[shape], polys[shape][1:] + [polys[shape][0]]):
            if combined_graph.has_edge(p1, p2):
                combined_graph.remove_edge(p1, p2)
                if not combined_graph[p1]:
                    combined_graph.remove_node(p1)
                if not combined_graph[p2]:
                    combined_graph.remove_node(p2)
            else:
                combined_graph.add_edge(p1, p2)
    poly = []
    pt = combined_graph.nodes().keys()[0]
    while pt not in poly:
        poly.append(pt)
        for neighbour in combined_graph.neighbors(pt):
            if neighbour not in poly:
                pt = neighbour
                break
    cluster = list(cluster)
    base = cluster[0]
    polys[base] = poly
    for shape in cluster[1:]:
        polys[shape] = []
        if shape in TG:
            for n, d in TG[shape].iteritems():
                if n != base:
                    TG.add_edge(base, n, **d)
            TG.remove_node(shape)


def _buildInitialGraph(polys):
    logger.info('Build polygon graph')
    edge_tri = {}
    TG = nx.Graph()

    def add_edge(n1, n2, tri, edges, TG):
        n1, n2 = sorted([n1, n2])
        if (n1, n2) not in edges:
            edges[n1, n2] = []
        for other in edges[n1, n2]:
            TG.add_edge(tri, other, v1=n1, v2=n2)
        edges[n1, n2].append(tri)

    for i, t in enumerate(polys):
        for t1, t2 in zip(t[:-1], t[1:]):
            add_edge(t1, t2, i, edge_tri, TG)
        add_edge(t[0], t[-1], i, edge_tri, TG)

    # Collapse internal edges
    central_shapes = [t for t in TG.nodes() if len(TG[t]) > 2]
    SG = TG.subgraph(central_shapes)
    clusters = list(nx.connected_components(SG))

    for cluster in clusters:
        _mergeShapes(cluster, TG, polys)

    logger.info('Polygon graph complete')
    return TG


def _tidyIntersections(TG, res, polys):
    logger.info('Tyding intersections')
    # 'Tyding T-intersections...'
    toMerge = []
    for node in TG.nodes():
        if TG.degree(node) == 3 and len(polys[node]) == 3:
            points = res['vertices'][polys[node]]
            A = np.array([[p[0]*p[0] + p[1]*p[1], p[0], p[1], 1]
                          for p in points])
            M11 = np.linalg.det(A[:, [1, 2, 3]])
            M12 = np.linalg.det(A[:, [0, 2, 3]])
            M13 = np.linalg.det(A[:, [0, 1, 3]])
            M14 = np.linalg.det(A[:, [0, 1, 2]])
            x = 0.5 * M12/M11
            y = -0.5 * M13/M11
            r2 = M14/M11 + x*x + y*y
            TG.node[node]['centroid'] = [x, y]
            centroid = Point(x,y)

            for neighbour, data in TG[node].iteritems():
                points = list(polys[neighbour])
                poly = Polygon([res['vertices'][p] for p in points])
                points.remove(data['v1'])
                points.remove(data['v2'])
                point = res['vertices'][points[0]]
                dx = x - point[0]
                dy = y - point[1]
                if dx*dx + dy*dy < 4*r2 or poly.contains(centroid):
                    toMerge.append([node, neighbour])

    for cluster in toMerge:
        _mergeShapes(cluster, TG, polys)

    logger.info('Tyding complete')
    # 'Cleaning up angled crossings...'
    # toMerge = []
    # for node in TG.nodes_iter():
    #     if TG.degree(node) == 2:
    #         sandwiched = True
    #         for neighbour in TG[node]:
    #             if TG.degree(neighbour) == 2:
    #                 sandwiched = False
    #         if sandwiched:
    #             toMerge.append([node] + TG[node].keys())
    #
    # for cluster in toMerge:
    #     _mergeShapes(cluster, TG, polys)


def _makeKey(t1, t2):
    t1, t2 = sorted([t1, t2])
    return int(t1 * 1e9 + t2)


def _normalVector(G, n1, n2):
    ux = G.node[n1]['x'] - G.node[n2]['x']
    uy = G.node[n1]['y'] - G.node[n2]['y']
    dist = max(np.sqrt(ux*ux + uy*uy), 1e-18)
    ux /= dist
    uy /= dist
    return ux, uy


def _insertEdge(G, n1, n2, terminal=False):
    if n1 == n2:
        return
    ux, uy = _normalVector(G, n1, n2)
    G.add_edge(n1, n2, ux=ux, uy=uy, terminal=terminal)


def _buildSkeletonGraph(TG, res, polys):
    logger.info('Building skeleton graph')
    node_idx = index.Index()
    G = nx.Graph(index=node_idx)
    for t1, t2, d in TG.edges(data=True):
        x = (res['vertices'][d['v1']][0] + res['vertices'][d['v2']][0])/2.0
        y = (res['vertices'][d['v1']][1] + res['vertices'][d['v2']][1])/2.0
        key = _makeKey(t1, t2)
        node_idx.insert(key, (x, y, x, y))
        G.add_node(key, x=x, y=y)

    for t, d in TG.nodes(data=True):
        if len(TG[t]) == 2:
            pairs = []
            for t2 in TG[t]:
                key = _makeKey(t, t2)
                if key in G:
                    pairs.append(key)
            for e1, e2 in combinations(pairs, 2):
                _insertEdge(G, e1, e2)
        else:  # if len(TG[t]) != 2:
            if 'centroid' in TG.node[t]:
                x, y = TG.node[t]['centroid']
            elif len(polys[t]) > 2:
                # calc centroid & add to graph
                poly = Polygon([list(res['vertices'][v])
                                for v in polys[t]])
                x, y = poly.centroid.coords[0]
            else:
                x, y = zip(*[list(res['vertices'][v])
                             for v in polys[t]])
                x = sum(x)/len(x)
                y = sum(y)/len(y)

            G.add_node(t, x=x, y=y)
            node_idx.insert(t, [x, y, x, y])
            # join all edges to centroid
            for t2 in TG[t]:
                key = _makeKey(t, t2)
                _insertEdge(G, t, key)
    logger.info('Skeleton graph complete')
    return G


def _insertAtTerminals(G, points):
    logger.info('Inserting terminal nodes')
    node_idx = G.graph['index']
    terminals = []
    #for lid, ls in enumerate(lineStrings):
    #    for i in [0, -1]:
    #        point = ls.coords[i]
    for i, point in enumerate(points):
            nearest = list(node_idx.nearest(point.bounds, num_results=1))[0]
            pid = -float(i) #-float(lid) + 0.1 * i
            terminals.append((pid, point, nearest))
    for pid, point, nearest in terminals:
        G.add_node(pid, x=point.x, y=point.y, terminal=True)
        _insertEdge(G, pid, nearest, terminal=True)


def _simplifyGraph(G, turnThreshold=20.0, simplifyTolerance=0):
    logger.info('Simplifying graph')
    DG = nx.MultiDiGraph()
    threshold = np.cos(turnThreshold/180.0*np.pi)
    for node in G.nodes():
        if node not in DG:
            DG.add_node(node, x=G.node[node]['x'], y=G.node[node]['y'])
        else:
            DG.node[node]['x'] = G.node[node]['x']
            DG.node[node]['y'] = G.node[node]['y']
        if len(G[node]) == 2:
            normals = []
            for neighbour in G[node]:
                n = _normalVector(G, node, neighbour)
                normals.append(n)
            dp = -(normals[0][0] * normals[1][0] +
                   normals[0][1] * normals[1][1])
            DG.node[node]['turn'] = dp < threshold
        if 'terminal' in G.node[node]:
            DG.node[node]['terminal'] = True
        for neighbour in G[node]:
            DG.add_edge(node, neighbour, nnodes=[node, neighbour],
                        terminal=G[node][neighbour]['terminal'])
    to_remove = []
    for node in DG.nodes():
        if len(DG.edges(node)) == 2 and not DG.node[node]['turn'] and node not in DG.neighbors(node):
            (x, n1), (x, n2) = DG.edges(node)
            if DG[node][n1][0]['terminal'] or DG[node][n2][0]['terminal']:
                continue
            seq = DG[n1][node][0]['nnodes'] + DG[node][n2][0]['nnodes'][1:]
            DG.add_edge(n1, n2, nnodes=seq, terminal=False)
            DG.add_edge(n2, n1, nnodes=list(reversed(seq)), terminal=False)
            to_remove.append(node)
            DG.remove_edge(n1, node)
            DG.remove_edge(node, n1)
            DG.remove_edge(n2, node)
            DG.remove_edge(node, n2)
        #if 'terminal' in DG.node[node]:
        #    to_remove.append(node)
    for node in to_remove:
        DG.remove_node(node)
    for s, t, data in DG.edges(data=True):
        coords = []
        for node in data['nnodes']:
            coords.append((G.node[node]['x'], G.node[node]['y']))
        ls = LineString(coords).simplify(simplifyTolerance)
        data['geom'] = ls
        data['length'] = ls.length
    for node, data in DG.nodes(data=True):
        data['geom'] = Point(G.node[node]['x'], G.node[node]['y'])
    logger.info('Simplificaiton complete')
    return DG


def _dumpBigShape(big_shape, debugFolder):
    zone = (int((big_shape.exterior.coords[0][0] + 180)/6) % 60) + 1
    utm17 = pyproj.Proj(proj='utm', zone=zone, ellps='WGS84')
    google = pyproj.Proj(init='epsg:4326')
    project = partial(pyproj.transform, utm17, google)
    with open(os.path.join(debugFolder, 'bigshape.geojson'), 'w') as fp:
        json.dump(mapping(transform(project, big_shape)), fp)


def _dumpTriangles(triangles, debugFolder):
    zone = (int((triangles['vertices'][0][0] + 180)/6) % 60) + 1
    utm17 = pyproj.Proj(proj='utm', zone=zone, ellps='WGS84')
    features = []
    for vs in triangles['triangles']:
        coord_list = [list(utm17(inverse=True,
                                 *triangles['vertices'][v])) for v in vs]
        features.append({"type": "Feature",
                         "properties": {'stroke-opacity': 0.25},
                         "geometry": {
                            "type": "Polygon",
                            "coordinates": [coord_list]
                         }})
    data = {"type": "FeatureCollection",
            "features": features}
    with open(os.path.join(debugFolder, 'triangles.geojson'), 'w') as fp:
        json.dump(data, fp)


def _dumpPolygons(polygons, triangles, debugFolder):
    zone = (int((triangles['vertices'][0][0] + 180)/6) % 60) + 1
    utm17 = pyproj.Proj(proj='utm', zone=zone, ellps='WGS84')
    features = []
    for vs in polygons:
        coord_list = [list(utm17(inverse=True,
                      *triangles['vertices'][v])) for v in vs]
        if not coord_list:
            continue
        features.append({"type": "Feature",
                         "properties": {'stroke-opacity': 0.25},
                         "geometry": {
                            "type": "Polygon",
                            "coordinates": [coord_list]
                         }})
    data = {"type": "FeatureCollection",
            "features": features}
    with open(os.path.join(debugFolder, 'polygons.geojson'), 'w') as fp:
        json.dump(data, fp)
