import tools
import pyclipper
import networkx as nx


def is_hole_loop(g, loop):
    """ Test if the loop is due to a hole in polygon,
    or if it should be filtered as a descrepancy. """

    filter = False
    if (len(loop) > 2) and (len(loop) < 6):
        filter = True
    return filter

class Labels:
    """  """

    def __init__(self, mesh, configdata, gds_num):
        self.mesh = mesh
        self.configdata = configdata
        self.gds = gds_num
      
    def default_triangles(self, g):
        """ Every triangle is connected to a layer type
        in the layout. Each graph vertex represent 
        a triangle, thus we have to map the triangle
        layer properties to the specific graph vertex. """
        
        for n in g.nodes():
            cell_list = self.mesh['cell_data']['triangle']['physical'].tolist()
            layerid = cell_list[n]
            
            g.node[n]['color'] = self.configdata['Params']['LAYER']
            g.node[n]['layer'] = 'null'
            g.node[n]['type'] = 0
            
            for key, value in self.mesh['field_data'].items():
                if layerid in value:
                    layername = key.split('_')[0]
                    for key, layer in self.configdata['Layers'].items():
                        if layer['name'] == layername:
                            g.node[n]['type'] = 0
                            g.node[n]['layer'] = layername
        return g

    def terminal_triangles(self, g, n, label, poly):
        if pyclipper.PointInPolygon(label.position, poly) != 0:
            g.node[n]['type'] = 2
            g.node[n]['layer'] = label.text
            g.node[n]['color'] = self.configdata['Params']['TERM']
        return g

    def via_triangles(self, g, n, label, poly):
        if label.text in self.configdata['Atoms']['vias'].keys():
            via_config = self.configdata['Atoms']['vias'][label.text]
            if pyclipper.PointInPolygon(label.position, poly) != 0:
                if (self.gds == via_config['wire1']) or (self.gds == via_config['wire2']):
                    if g.node[n]['type'] == 1:
                        ll = g.node[n]['layer']
                        via_nodes = filter(lambda (n, d): d['layer'] == ll, g.nodes(data=True))
                        for nn in via_nodes:
                            g.node[nn[0]]['type'] = 1
                            g.node[nn[0]]['layer'] = label.text + '_' + str(label.texttype)
                            g.node[nn[0]]['color'] = self.configdata['Params']['VIA']
                    else:
                        g.node[n]['type'] = 1
                        g.node[n]['layer'] = label.text + '_' + str(label.texttype)
                        g.node[n]['color'] = self.configdata['Params']['VIA']
        return g             

    def jj_triangles(self, g, n, label, poly, jj_key):
        if pyclipper.PointInPolygon(label.position, poly) != 0:
            # if (gds == self.Layers['51']['wire1'][0]) or (gds == self.Layers['51']['wire2'][0]):
            if self.gds == self.configdata['Layers'][jj_key]['wire2'][0]:
                g.node[n]['type'] = 3
                g.node[n]['layer'] = label.text + '_' + str(label.texttype)
                g.node[n]['color'] = tools.color_tuple(self.configdata['Params']['JJ'])
        return g

    def shunt_triangles(self, g, n, label, poly):
        jj_config = self.configdata['Atoms']['jjs']['shunt']
        if pyclipper.PointInPolygon(label.position, poly) != 0:
            if (self.gds == jj_config['wire']) or (self.gds == jj_config['shunt']):
                masternodes = [1, 2, 3, 4, 5]

                if g.node[n]['type'] in masternodes:
                    nn = len(g.nodes())

                    g.add_node(nn)

                    g.node[nn]['type'] = 6
                    g.node[nn]['layer'] = label.text + '_' + str(label.texttype)
                    g.node[nn]['color'] = tools.color_tuple(self.configdata['Params']['DVALUE'])
                    g.node[nn]['pos'] = [sum(x) for x in zip(g.node[n]['pos'], [10e4, 10e4])]

                    g.add_edge(n, nn)
                else:
                    g.node[n]['type'] = 1
                    g.node[n]['layer'] = label.text + '_' + str(label.texttype)
                    g.node[n]['color'] = tools.color_tuple(self.configdata['Params']['GROUND'])
        return g

    def ground_triangles(self, g, n, label, poly):
        jj_config = self.configdata['Atoms']['jjs']['ground']
        if pyclipper.PointInPolygon(label.position, poly) != 0:
            if (self.gds == jj_config['wire']) or (self.gds == jj_config['gnd']):
                g.node[n]['type'] = 4
                g.node[n]['layer'] = label.text + '_' + str(label.texttype)
                g.node[n]['color'] = tools.color_tuple(self.configdata['Params']['GROUND'])
        return g
                        
    def user_triangles(self, g):
        """
        * Autodetect the usernodes, which are represented
          as the Green vertices on the graph.

        * Get the vertex with 3 neighbours, and the current
          vertex must be a wire vertex (COU or CTL) in this case.

        * Use the 'type' variable in the layer json object to
          see if the vertex is a layer or not.

        * Lastly, update the vertex_key property map
        """

        for n in g.nodes():
            if len([i for i in g.neighbors(n)]) > 2:
                if (g.node[n]['type'] != 11) and (g.node[n]['type'] != 1):
                    g.node[n]['type'] = 5
                    g.node[n]['layer'] = 'user_' + g.node[n]['layer'] + str(i)
                    g.node[n]['color'] = self.configdata['Params']['USER']

                    for i in g.neighbors(n): 
                        """ If there is a junction next to the usernode,
                        then make that usernode a junction node. """

                        if g.nodes[i]['type'] == 3:
                            g.node[n]['type'] = 3
                            g.node[n]['layer'] = g.node[i]['layer']
                            g.node[n]['color'] = self.configdata['Params']['USER']
        return g

    def wire_nodes(self, g, branches):
        for key, branch in branches.items():
            edgenode_1 = branch[0]
            edgenode_2 = branch[-1]
            for n in branch:
                if (g.node[n]['type'] == 0) or (g.node[n]['type'] == 10):
                    g.node[n]['type'] = g.node[edgenode_1]['type']
                    g.node[n]['layer'] = g.node[edgenode_1]['layer'] + '__' + g.node[edgenode_2]['layer']
                    g.node[n]['color'] = self.configdata['Params']['LAYER']

    def get_loops(self, g, configdata):
        H = g.to_directed()
        cycles = list(nx.simple_cycles(H))
        for i, loop in enumerate(cycles):
            if is_hole_loop(g, loop):
                masternodes = [1, 2, 3, 4, 5, 6, 8, 11]

                for n in loop:
                    if g.node[n]['type'] not in masternodes:                       
                        g.node[n]['type'] = 10
                        g.node[n]['layer'] = 'loop_' + str(i)
                        g.node[n]['color'] = configdata['Params']['JJ']
        return g

    def update_labels(self, g, configdata, layoutcell):
        gds_wires = layoutcell.get_polygons(True)
        box = gds_wires[(45, 6)]
        box2 = gds_wires[(42, 1)]

        for n in g.nodes():
            pos = g.node[n]['pos']
            for i, poly in enumerate(box):
                if pyclipper.PointInPolygon(pos, poly) != 0:
                    g.node[n]['type'] = 11
                    g.node[n]['layer'] = 'ntron_' + str(i)
                    g.node[n]['color'] = configdata['Params']['NTRON']

        for n in g.nodes():
            pos = g.node[n]['pos']
            for i, poly in enumerate(box2):
                if pyclipper.PointInPolygon(pos, poly) != 0:
                    g.node[n]['type'] = 1
                    g.node[n]['layer'] = 'via_' + str(i)
                    g.node[n]['color'] = configdata['Params']['VIA']

        return g
    
    
    
    
    
