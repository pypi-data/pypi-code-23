from collections import defaultdict
from itertools import count

import pygmsh as pg
import numpy as np
import networkx as nx
import pyclipper
import matplotlib.pyplot as plt

import os
import labels
import tools
import meshio
from yuna import tools as yt


def check_terminal_duplicates(edgelabels):
    duplicates = defaultdict(list)
    
    for i, item in enumerate(edgelabels):
        duplicates[item].append(i)
    
    duplicates = {k:v for k, v in duplicates.items() if len(v) > 1}
                    
    for key, value in duplicates.items():
        if key is not None:
            if len(value) > 1:
                raise('Terminal duplicates!')


def update_adjacent_matrix(g, t1, adj_mat, v1, v2):
    if (adj_mat[v1][v2] != 0):
        t2 = adj_mat[v1][v2] - 1
        g.add_edge(t1, t2, key='none')
    else:
        adj_mat[v1][v2] = t1 + 1
        adj_mat[v2][v1] = t1 + 1

    
class LayerGraph:
    """  """

    def __init__(self, g, gds_labels=None):
        self.g = g
        self.mesh = dict()
        self.gds_labels = gds_labels

    def generate_mesh(self, name, wires, gds):
        tools.green_print('Generating Mesh')
        geom = pg.built_in.Geometry()

        count = 0
        wirenormal = tools.convert_node_to_3d(wires[(gds, 0)])

        for i, poly in enumerate(wirenormal):
            polyname = name + '_' + str(i)
            
            layer = geom.add_polygon(poly, lcar=100, make_surface=True)
            geom.add_physical_surface(layer.surface, label=polyname)
            count += 1

        num = 0
        if (99+gds, 0) in wires:
            for key, value in wires.items():
                if key[0] == 99+gds:
                    wirehole = tools.convert_node_to_3d(wires[(99+gds, num)])
                    hole = tools.convert_node_to_3d(wires[(100+gds, num)])
                    num += 1

                    for i in range(len(wirehole)):
                        polyname = name + '_' + str(count)
                        count += 1

                        mhole = geom.add_polygon(hole[i], lcar=100, make_surface=False)
                        layer = geom.add_polygon(wirehole[i], lcar=100, holes=[mhole.line_loop], make_surface=True)
                        geom.add_physical_surface(layer.surface, label=polyname)

        geom.add_raw_code('Mesh.Algorithm = 100;')
        geom.add_raw_code('Coherence Mesh;')
        geom.add_raw_code('Mesh 2;')
        geom.add_raw_code('Coherence Mesh;')

        meshdata = pg.generate_mesh(geom, verbose=False, num_lloyd_steps=0, prune_vertices=False)

        self.mesh['points'] = meshdata[0]
        self.mesh['cells'] = meshdata[1]
        self.mesh['point_data'] = meshdata[2]
        self.mesh['cell_data'] = meshdata[3]
        self.mesh['field_data'] = meshdata[4]

        directory = os.getcwd() + '/mesh/'
        filename = directory + name + '.msh'

        if not os.path.exists(directory):
            os.makedirs(directory)

        meshio.write(filename, self.mesh['points'], self.mesh['cells'])
        tools.cyan_print('Finished generating Mesh...')
        
    def add_network_edge(self):
        """
            Parameters
            ----------
            adjacent_matrix : nparray
                See which edges are connected through
                triangles. Save triangle id to which the
                edge exists.

            triangles : nparray
                Array containing the node ids of the 3
                vertices of the triangle.

            Notes
            -----
            * From triangles:
                tri --> [v1, v2, v3]
                edge --> 1-2, 2-3, 1-3

            Algorithm
            ---------
            * Loop through every triangle and its edges.
            * Save the triangle id in the adjacent_matrix
            with index of (v1, v2).
        """

        G = self.g.copy()

        ll = len(self.mesh['points'])
        A = np.zeros((ll, ll), dtype=np.int64)
        
        for i, tri in enumerate(self.mesh['cells']['triangle']):
            v1, v2, v3 = tri[0], tri[1], tri[2]
            
            update_adjacent_matrix(G, i, A, v1, v2)
            update_adjacent_matrix(G, i, A, v1, v3)
            update_adjacent_matrix(G, i, A, v2, v3)

        self.g = G
                    
    def add_network_nodes(self):
        """ Gets the center nodes of each triangle. """

        for n, tri in enumerate(self.mesh['cells']['triangle']):
            pp = self.mesh['points']
            n1, n2, n3 = pp[tri[0]], pp[tri[1]], pp[tri[2]]

            sum_x = 100e6*(n1[0] + n2[0] + n3[0]) / 3.0
            sum_y = 100e6*(n1[1] + n2[1] + n3[1]) / 3.0

            self.g.nodes[n]['vertex'] = tri
            self.g.nodes[n]['pos'] = [sum_x, sum_y]

    def add_network_labels(self, configdata, gds_num, layoutcell):
        """  """

        mlabels = labels.Labels(self.mesh, configdata, gds_num)

        G = self.g.copy()

        G = mlabels.default_triangles(G)
        G = mlabels.update_labels(G, configdata, layoutcell)

        jj_key = None
        for key, layer in configdata['Layers'].items():
            if layer['type'] == 'junction':
                jj_key = str(key)

        for n, tri in enumerate(self.mesh['cells']['triangle']):
            pp = self.mesh['points']
            n1, n2, n3 = pp[tri[0]], pp[tri[1]], pp[tri[2]]

            n1 = tools.convert_node_to_2d(n1)
            n2 = tools.convert_node_to_2d(n2)
            n3 = tools.convert_node_to_2d(n3)

            poly = [n1, n2, n3]

            for gl in self.gds_labels:
                if gl.text[0] == 'P':
                    G = mlabels.terminal_triangles(G, n, gl, poly)
                elif gl.text[:3] == 'via':
                    G = mlabels.via_triangles(G, n, gl, poly)
                elif gl.text[:2] == 'jj':
                    G = mlabels.jj_triangles(G, n, gl, poly, jj_key)
                elif gl.text[:5] == 'shunt':
                    G = mlabels.shunt_triangles(G, n, gl, poly)
                elif gl.text[:3] == 'gnd':
                    G = mlabels.ground_triangles(G, n, gl, poly)
                # elif gl.text[:5] == 'ntron':
                #     G = mlabels.ntron_triangles(G, n, gl, poly)

        self.g = G

        return mlabels
    
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
