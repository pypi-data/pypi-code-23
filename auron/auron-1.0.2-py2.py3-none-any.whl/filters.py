import networkx as nx
import tools

def clean_paths(g, branches):
    """  """
    
    remove = list()
    
    for n in g.nodes():
        ix_path = True 
        for key, branch in branches.items():
            if n in branch:
                ix_path = False
        if ix_path is True:
            remove.append(n)
            
    g.remove_nodes_from(remove)
    

def create_conducting_paths(g):
    """ Branch must have atleast 2 masternodes, otherwise just save 
    the masternode, master = get_master_nodes(sg) """

    sub_graphs = nx.connected_component_subgraphs(g, copy=True)
    
    branches = dict()
    
    count = 0
    for sg in sub_graphs:
        master = [n for n in sg.nodes() if sg.node[n]['type'] in tools.masternodes]
        
        masterpath = ConductingPath(sg, master)
        
        if len(master) > 1:
            masterpath.branch_master()
        elif len(master) == 1:
            masterpath.ground_master()
            
        if masterpath.subgraph_branches is not None:
            for path in masterpath.subgraph_branches:
                branches[count] = path
                count += 1

    clean_paths(g, branches)
    
    return branches


class ConductingPath:
    """  """
    
    def __init__(self, g, master):
        self.g = g
        self.master = master
        self.subgraph_branches = []
        
    def add_path_to_branch(self, path):
        ix = True
        
        """ Test if path contains masternodes. """
        for n in path[1:-1]:
            if self.g.node[n]['type'] in tools.masternodes:
                ix = False
                
        """ Test if path already exists. """
        be = [path[0], path[-1]]
        for bp in self.subgraph_branches:
            if set(be).issubset(bp):
                ix = False
                
        if len(path) == 2:
            self.subgraph_branches.append(path)
        if ix is True:
            self.subgraph_branches.append(path)
            
    def ground_master(self):
        for n in self.g.nodes():
            self.subgraph_branches.append([n])
        
    def branch_master(self):
        """ Get the branches between masternodes without
        any other masternodes inbetween. """

        for source in self.master:
            targets = filter(lambda x: x not in [source], self.master)

            for target in targets:
                for path in nx.all_simple_paths(self.g, source=source, target=target):
                    if (path[0] in self.master) or (path[-1] in self.master):
                        self.add_path_to_branch(path)
                        

                        
                        
                        
                        
                        
                        
                        
    
        
