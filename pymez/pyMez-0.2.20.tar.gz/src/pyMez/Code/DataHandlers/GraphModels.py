#-----------------------------------------------------------------------------
# Name:        GraphModels
# Purpose:     To store graphs used in network translations
# Author:      Aric Sanders
# Created:     4/6/2016
# License:     MIT License
#-----------------------------------------------------------------------------
"""
Graph Models stores sub classes of graphs that define data translations. All edges
or the functions that define translations from one format to another
are found in <a href="./Translations.m.html">`pyMez.Code.DataHandlers.Translations`</a>.
Currently, the module networkx is used to display the graph.

Examples
--------
    #!python
    >>from pyMez import *
    >>image_graph=ImageGraph()
    >>image_graph.set_state('png','my_png.png')
    >>image_graph.move_to_node('EmbeddedHtml')
    >>output=image_graph.data
    >>print output


<h3><a href="../../../Examples/Html/GraphModels_Example.html">GraphModels Example</a></h3>

Requirements
------------
+ [sys](https://docs.python.org/2/library/sys.html)
+ [os](https://docs.python.org/2/library/os.html?highlight=os#module-os)
+ [networkx](http://networkx.github.io/)
+ [numpy](http://www.numpy.org/)
+ [pyMez](https://github.com/aricsanders/pyMez)

Help
---------------
<a href="./index.html">`pyMez.Code.DataHandlers`</a>
<div>
<a href="../../../pyMez_Documentation.html">Documentation Home</a> |
<a href="../../index.html">API Documentation Home</a> |
<a href="../../Examples/Html/Examples_Home.html">Examples Home</a> |
<a href="../../../Reference_Index.html">Index</a>
</div>
   """

#-----------------------------------------------------------------------------
# Standard Imports
import re
import datetime
import sys
import os

#-----------------------------------------------------------------------------
# Third Party Imports
sys.path.append(os.path.join(os.path.dirname( __file__ ), '..','..'))
try:
    from Code.Utils.Alias import *
    METHOD_ALIASES=1
except:
    print("The module pyMez.Code.Utils.Alias was not found")
    METHOD_ALIASES=0
    pass
try:
    from Code.DataHandlers.GeneralModels import *
except:
    print("The module pyMez.Code.DataHandlers.GeneralModels was not found,"
          "please put it on the python path")
    raise ImportError
try:
    from Code.DataHandlers.TouchstoneModels import *
except:
    print("The module pyMez.Code.DataHandlers.TouchstoneModels was not found,"
          "please put it on the python path")
    raise ImportError
try:
    from Code.DataHandlers.Translations import *
except:
    print("The module pyMez.Code.DataHandlers.Translations was not found or had an error,"
          "please put it on the python path or resolve the error")
    raise ImportError
try:
    import numpy as np
except:
    print("The module numpy was not found,"
          "please put it on the python path")
    raise ImportError
try:
    import networkx
except:
    print("The module networkx was not found,"
          "please put it on the python path")
    raise ImportError

#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions

# as an example these functions are left.
#todo: Change the names
def edge_1_to_2(in_string):
    "A Test function for an edge for a Graph"
    return in_string.splitlines()

def edge_2_to_1(string_list):
    """A test function for an edge in a Graph"""
    return string_list_collapse(string_list)

def visit_all_nodes(graph):
    """Visit all nodes visits each node on a graph"""
    nodes=graph.node_names
    for node in nodes:
        graph.move_to_node(node)

def visit_and_print_all_nodes(graph):
    """Visits all the nodes in graph and prints graph.data after each move"""
    nodes=graph.node_names
    for node in nodes:
        graph.move_to_node(node)
        print(graph.data)


def TableGraph_to_Links(table_graph, **options):
    """Converts a table graph to a set of download links with embedded data in them"""
    defaults = {"base_name": None,
                "nodes": ['XmlFile', 'CsvFile', 'ExcelFile', 'OdsFile', 'MatFile', 'HtmlFile', 'JsonFile'],
                "extensions": ['xml', 'csv', 'xlsx', 'ods', 'mat', 'html', 'json'],
                "mime_types": ['application/xml', 'text/plain',
                               'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                               'application/vnd.oasis.opendocument.spreadsheet',
                               'application/x-matlab-data', 'text/html', 'application/json']}
    conversion_options = {}
    for key, value in defaults.iteritems():
        conversion_options[key] = value
    for key, value in options.iteritems():
        conversion_options[key] = value
    if conversion_options["base_name"] is None:
        base_name = 'test.txt'
    else:
        base_name = conversion_options["base_name"]

    nodes = conversion_options["nodes"]
    extensions = conversion_options["extensions"]
    mime_types = conversion_options["mime_types"]

    out_links = ""
    for node_index, node in enumerate(nodes):
        table_graph.move_to_node(node)
        file_path = table_graph.data
        in_file = open(file_path, 'rb')
        content_string = in_file.read()
        link = String_to_DownloadLink(content_string,
                                      suggested_name=change_extension(base_name, extensions[node_index]),
                                      mime_type=mime_types[node_index],
                                      text=extensions[node_index])
        if node_index == len(nodes) - 1:
            out_links = out_links + link
        else:
            out_links = out_links + link + " | "
    return out_links


def remove_circular_paths(path):
    """Removes pieces of the path that just end on the same node"""
    # Todo: Track the error that leaves out a needed path sometimes
    # See http://localhost:8888/notebooks/Two_Port_Matrix_Parameters_Debug_20170105_001.ipynb

    edge_pattern=re.compile("edge_(?P<begin_node>\w+)_(?P<end_node>\w+)_(?P<iterator>\w+)")
    past_locations=[]

    for index,edge in enumerate(path):
        match=re.match(edge_pattern,edge)
        begin_node=match.groupdict()["begin_node"]
        end_node=match.groupdict()["end_node"]
        past_locations.append(begin_node)
        #print("{0} is {1}".format("past_locations",past_locations))
    new_path=[]
    node_index=0
    between_list=[False for item in past_locations]
    while(node_index<len(past_locations)):
        node=past_locations[node_index]
        old_path=new_path
        new_path=[]
        # if you visit a location more than one
        number_of_visits=past_locations.count(node)
        if number_of_visits>1:
            #print("{0} is {1}".format("node",node))
            #print("{0} is {1}".format("past_locations",past_locations))
            # Now find all the visits to that location
            equality_list=map(lambda x:x==node,past_locations)
            print("{0} is {1}".format("equality_list",equality_list))
            # You are intially not between visits
            between=False

            # every time you cross that node you flip between, as long as there are
            visit_number=0
            for index,equality in enumerate(equality_list):
                if equality:
                    # add one to the visit number
                    visit_number+=1
                    # Flip the between truth value if it is the first or last
                    # visits only
                    if visit_number==1 or visit_number==number_of_visits:
                        between=not between
                        between_list[index]=between or between_list[index]
                    else:
                        between_list[index]=between or between_list[index]
                else:
                    between_list[index]=between or between_list[index]
        #print("{0} is {1}".format("between_list",between_list))
        for index,item in enumerate(between_list):
            if not item:
                new_path.append(path[index])
        node_index+=1
    if new_path in [[]]:
        new_path=path
    return new_path
#-----------------------------------------------------------------------------
# Module Classes

class Graph(object):
    """The Graph class creates a content graph that has as nodes different formats. As
    a format is added via graph.add_node() by specifying a node name and a function from an
    existing node into the new one, and one exiting the node. Once a series of nodes exists
    to enter the graph at a node use graph.set_state() the current data representing the
    state is in the attribute graph.data. To move among the formats use graph.move_to_node('NodeName')
    need to recode the find_path method using a shortest path alogrithm like
    [Dijkstra](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm).
    """
    def __init__(self,**options):
        """Initializes the graph. The first 2 nodes and two edges forming a bijection between them are required"""
        defaults={"graph_name":"Graph",
                  "node_names":['n1','n2'],
                  "node_descriptions":["A plain string",
                                       "A list of strings with no \\n, created with string.splitlines()"],
                  "current_node":'n1',
                  "state":[1,0],
                  "data":"This is a test string\n it has to have multiple lines \n and many characters 34%6\n^",
                  "edge_2_to_1":edge_2_to_1,
                  "edge_1_to_2":edge_1_to_2
                 }
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        self.elements=['graph_name','node_names','node_descriptions','current_node','state','data']
        for element in self.elements:
            self.__dict__[element]=self.options[element]
        self.edges=[]
        self.edge_matrices=[]
        self.state_matrix=np.matrix(self.state).T
        # Add the first 2 edges, required to intialize the graph properly
        self.display_graph=networkx.DiGraph()

        self.add_edge(self.node_names[0],self.node_names[1],self.options["edge_1_to_2"])
        self.add_edge(self.node_names[1],self.node_names[0],self.options["edge_2_to_1"])
        self.jumps=[]
        self.external_node_names=[]
        self.external_node_descriptions=[]
        self.display_layout=networkx.spring_layout(self.display_graph)

    def get_description_dictionary(self):
        "returns a dictionary of the form {NodeName:Node Description for all of the current nodes"
        dictionary={node_name:self.node_descriptions[index] for index,node_name in enumerate(self.node_names)}
        return dictionary

    def set_state(self,node_name,node_data):
        """Sets the graph state to be the state specified by node_name, and node_data"""
        try:
            current_node_state_position=self.node_names.index(node_name)
            self.current_node=node_name
            self.data=node_data
            self.state=[0 for i in range(len(self.node_names))]
            self.state[current_node_state_position]=1
            self.state_matrix=np.matrix(self.state).T
        except:
            print("Could not set the state of graph: {0}".format(self.graph_name))
            raise

    def add_edge(self,begin_node=None,end_node=None,edge_function=None):
        """Adds an edge mapping one node to another, required input is begin_node (it's name)
        end_node, and the edge function"""
        # check to see if edge is defined if it is increment a number
        edge_match=re.compile("edge_{0}_{1}".format(begin_node,end_node))
        keys=self.__dict__.keys()
        #print keys
        iterator=0
        for key in keys:
            if re.match(edge_match,key):
                iterator+=1
        edge_name="edge_{0}_{1}_{2:0>3d}".format(begin_node,end_node,iterator)
        self.__dict__[edge_name]=edge_function
        self.edges.append(edge_name)
        edge_matrix=np.zeros((len(self.state),len(self.state)))
        begin_position=self.node_names.index(begin_node)
        end_position=self.node_names.index(end_node)
        edge_matrix[end_position][begin_position]=1
        edge_matrix=np.matrix(edge_matrix)
        self.edge_matrices.append(edge_matrix)
        self.display_graph.add_edge(begin_node,end_node)
        self.display_layout=networkx.spring_layout(self.display_graph)

    def add_jump(self,begin_node=None,end_node=None,jump_function=None):
        """Adds a jump mapping one internal node to an external node, required input is begin_node (it's name)
        end_node, and the edge function"""
        # check to see if edge is defined if it is increment a number
        jump_match=re.compile("jump_{0}_{1}".format(begin_node,end_node))
        keys=self.__dict__.keys()
        #print keys
        iterator=0
        for key in keys:
            if re.match(jump_match,key):
                iterator+=1
        jump_name="jump_{0}_{1}_{2:0>3d}".format(begin_node,end_node,iterator)
        self.__dict__[jump_name]=jump_function
        self.jumps.append(jump_name)
        self.display_graph.add_edge(begin_node,end_node)
        self.display_layout=networkx.spring_layout(self.display_graph)
    def move_to(self,path):
        """Changes the state of the graph by moving along the path specified"""
        print path
        for index,edge in enumerate(path):
            #print edge
            edge_pattern='edge_(?P<begin_node>\w+)_(?P<end_node>\w+)_(?P<iterator>\w+)'
            match=re.match(edge_pattern,edge)
            begin_node=match.groupdict()['begin_node']
            end_node=match.groupdict()['end_node']
            print("moving {0} -> {1}".format(begin_node,end_node))
            #print self.data
            self.data=self.__dict__[edge](self.data)
            #print self.data
            self.current_node=match.groupdict()['end_node']
            self.state=[0 for i in range(len(self.node_names))]
            position=self.node_names.index(self.current_node)
            self.state[position]=1
            self.state_matrix=np.matrix(self.state).T
            #print self.state
            #print self.current_node

    def virtual_move_to(self,path):
        """virtual_move_to simulates moving but does not change the state of the graph"""
        #print path
        temp_state=self.state
        temp_data=self.data
        temp_current_node=self.current_node
        temp_node_names=self.node_names
        for index,edge in enumerate(path):
            #print edge
            edge_pattern='edge_(?P<begin_node>\w+)_(?P<end_node>\w+)_(?P<iterator>\w+)'
            match=re.match(edge_pattern,edge)
            begin_node=match.groupdict()['begin_node']
            end_node=match.groupdict()['end_node']
            #print("moving {0} -> {1}".format(begin_node,end_node))
            #print self.data
            temp_data=self.__dict__[edge](temp_data)
            #print self.data
            temp_current_node=match.groupdict()['end_node']
            temp_state=[0 for i in range(len(temp_node_names))]
            position=temp_node_names.index(temp_current_node)
            temp_state[position]=1
            #print temp_state
            #print self.state
            #print self.current_node

    def __str__(self):
        return str(self.data)

    def add_node(self,node_name,edge_into_node_begin,edge_into_node_function,edge_out_node_end,
                 edge_out_node_function,node_description=None):
        """Adds a node to the graph. Required input is node_name (a string with no spaces),
        a reference to an entering node,the function mapping the entering node to the new node,
        a reference to an exiting node and the function mapping the
        new node to the exiting node."""
        # first check if node into and out of node is good
        self.node_names.append(node_name)
        self.state.append(0)
        self.state_matrix=np.matrix(self.state).T
        for index,matrix in enumerate(self.edge_matrices):
            pad_row=np.zeros((1,len(matrix)))
            new_matrix=np.concatenate((matrix, pad_row), axis=0)
            pad_column=np.zeros((1,len(self.node_names)))
            new_matrix=np.concatenate((new_matrix, pad_column.T), axis=1)
            #print("New matrix is :\n{0}".format(new_matrix))
            self.edge_matrices[index]=new_matrix
        self.add_edge(begin_node=node_name,end_node=edge_out_node_end,edge_function=edge_out_node_function)
        self.add_edge(begin_node=edge_into_node_begin,end_node=node_name,edge_function=edge_into_node_function)
        if node_description:
            self.node_descriptions.append(node_description)
        self.display_graph.add_node(node_name)
        self.display_graph.add_edge(node_name,edge_out_node_end)
        self.display_graph.add_edge(edge_into_node_begin,node_name)
        self.display_layout=networkx.spring_layout(self.display_graph)

    def add_external_node(self,external_node_name,jump_into_node_begin,
                          jump_into_node_function,external_node_description=None):
        """Adds an external node to the graph. Required input is node_name (a string with no spaces),
        a reference to an entering node,the function mapping the entering node to the new external node"""
        # first check if node into and out of node is good
        self.external_node_names.append(external_node_name)
        self.add_jump(begin_node=jump_into_node_begin,end_node=external_node_name,jump_function=jump_into_node_function)
        if external_node_description:
            self.external_node_descriptions.append(external_node_description)
        self.display_graph.add_node(external_node_name)
        self.display_graph.add_edge(jump_into_node_begin,external_node_name)
        self.display_layout=networkx.spring_layout(self.display_graph)

    def jump_to_external_node(self,external_node_name,**options):
        """Returns the result of the jump, the graph is left in the node that is the begining of the jump"""
        end_node=external_node_name
        jump_pattern='jump_(?P<begin_node>\w+)_{0}_(?P<iterator>\w+)'.format(end_node)
        for jump in self.jumps[:]:
            jump_match=re.match(jump_pattern,jump,re.IGNORECASE)
            if jump_match:
                jump_to_use=jump
                begin_node=jump_match.groupdict()["begin_node"]

        self.move_to_node(begin_node)
        return self.__dict__[jump_to_use](self.data,**options)



    def path_length(self,path,num_repeats=10):
        """Determines the length of a given path, currently the metric is based on the time to move to."""
        begin_time=datetime.datetime.now()
        #num_repeats=100
        for i in range(num_repeats):
            self.virtual_move_to(path)
        end_time=datetime.datetime.now()
        delta_t=end_time-begin_time
        path_length=delta_t.total_seconds()/float(num_repeats)
        if path_length ==0.0:
            print("Warning the path length is less than 1 microsecond,"
                  "make sure num_repeats is high enough to measure it.")
        return path_length

    def is_path_valid(self,path):
        """Returns True if the path is valid from the current node position or False otherwise"""
        null_state=[0 for i in range(len(self.node_names))]
        null_state_matrix=np.matrix(null_state).T
        new_state=np.matrix(self.state).T
        for index,edge in enumerate(path):
            #print index
            #print edge
            edge_position=self.edges.index(edge)
            move_matrix=self.edge_matrices[edge_position]
            #print move_matrix
            new_state=move_matrix*new_state
            if new_state.any()==null_state_matrix.any():
                #print new_state
                #print null_state_matrix
                return False
        return True


    def get_entering_nodes(self,node):
        """Returns all nodes that have an edge that enter the specificed node"""
        enter_edge_pattern=re.compile('edge_(?P<begin_node>\w+)_{0}_(?P<iterator>\w+)'.format(node))
        enter_nodes=[]
        for index,edge in enumerate(self.edges):
            enter_match=re.match(enter_edge_pattern,edge)
            if enter_match:
                enter_node=enter_match.groupdict()['begin_node']
                enter_nodes.append(enter_node)
        return enter_nodes

    def get_entering_edges(self,node):
        """Returns all edges that enter the specificed node"""
        enter_edge_pattern=re.compile('edge_(?P<begin_node>\w+)_{0}_(?P<iterator>\w+)'.format(node))
        enter_edges=[]
        for index,edge in enumerate(self.edges):
            if re.match(enter_edge_pattern,edge):
                enter_edges.append(edge)
        return enter_edges

    def get_exiting_edges(self,node):
        """Returns all edges that exit the specificed node"""
        exit_edge_pattern=re.compile('edge_{0}_(?P<end_node>\w+)_(?P<iterator>\w+)'.format(node))
        exit_edges=[]
        for index,edge in enumerate(self.edges):
            if re.match(exit_edge_pattern,edge):
                exit_edges.append(edge)
        return exit_edges

    def get_exiting_nodes(self,node):
        """Returns all nodes that have an edge leaving the specificed node"""
        exit_edge_pattern=re.compile('edge_{0}_(?P<end_node>\w+)_(?P<iterator>\w+)'.format(node))
        exit_nodes=[]
        for index,edge in enumerate(self.edges):
            exit_match=re.match(exit_edge_pattern,edge)
            if exit_match:
                exit_node=exit_match.groupdict()['end_node']
                exit_nodes.append(exit_node)
        return exit_nodes

    def get_path(self,first_node,last_node):
        """Returns the first path found between first node and last node, five step paths are broken"""
        #todo: long paths are not found have to add a follow right hand side algorithm
        #Remove circular paths added 12/2016
        edge_pattern=re.compile('edge_(?P<begin_node>\w+)_(?P<end_node>\w+)_(?P<iterator>\w+)')
        exit_paths=self.get_exiting_edges(first_node)
        next_nodes=self.get_exiting_nodes(first_node)
        #be careful here using the wrong assignment statement breaks this function
        possible_paths=[]
        for exit_path in exit_paths:
            possible_paths.append([exit_path])
        #print("{0} is {1}".format('possible_paths',possible_paths))
        for i in range(len(self.node_names)**3):
            #print("{0} is {1}".format('i',i))
            #print("{0} is {1}".format('possible_paths',possible_paths))
            for index,path in enumerate(possible_paths):
                #print("{0} is {1}".format('index',index))
                last_edge=path[-1]
                #print("{0} is {1}".format('last_edge',last_edge))
                match=re.match(edge_pattern,last_edge)
                begin_node=match.groupdict()['begin_node']
                end_node=match.groupdict()['end_node']
                #print("{0} is {1}".format('end_node',end_node))
                if end_node==last_node:
                    #print("The path found is {0}".format(path))
                    return remove_circular_paths(path)
                next_possible_paths=[]
                next_edges=self.get_exiting_edges(end_node)
                next_nodes=self.get_exiting_nodes(end_node)
                #print("{0} is {1}".format('next_edges',next_edges))
                for next_edge_index,next_edge in enumerate(next_edges):
                    #print("{0} is {1}".format('next_edge_index',next_edge_index))
                    #be careful here using the wrong assignment statement breaks this function
                    #next_path=path is a deal breaker!!
                    next_path=[]
                    for edge in path:
                        next_path.append(edge)
                    #print("{0} is {1}".format('next_path',next_path))
                    #print("{0} is {1}".format('next_edge',next_edge))
                    #next_node=next_nodes[index]
                    #print next_node
                    next_match=re.match(edge_pattern,next_edge)
                    next_node=next_match.groupdict()["end_node"]
                    begin_node_next_edge=next_match.groupdict()["begin_node"]
                    #print("{0} is {1}".format('next_node',next_node))
                    #print("{0} is {1}".format('begin_node_next_edge',begin_node_next_edge))
                    if next_node==last_node and begin_node_next_edge==end_node:
                        next_path.append(next_edge)
                        #print("The path found is {0}".format(next_path))
                        return remove_circular_paths(next_path)
                    elif begin_node_next_edge==end_node:
                        next_path.append(next_edge)
                        # This keeps it from getting stuck on circular paths
                        if next_edge in path:
                        #ossible_paths=possible_paths
                            #print("next_edge was already in path")
                            continue
                        next_possible_paths.append(next_path)

                        #print("{0} is {1}".format('next_possible_paths',next_possible_paths))
                    else:
                        print("Path is not found")
                        pass

                    #print("{0} is {1}".format('next_possible_paths',next_possible_paths))
                if next_possible_paths:
                    possible_paths=next_possible_paths
                #print("{0} is {1}".format('possible_paths',possible_paths))

    def move_to_node(self,node):
        """Moves from current_node to the specified node"""
        path=self.get_path(self.current_node,node)
        self.move_to(path)

    def check_closed_path(self):
        """Checks that data is not changed for the first closed path found. Returns True if data==data after
        moving around the closed path, False otherwise. Starting point is current_node """
        temp_data=self.data
        path=self.get_path(self.current_node,self.current_node)
        if self.is_path_valid(path):
            pass
        else:
            print("Path is not valid, graph definition is broken")
            raise
        out=temp_data==self.data
        out_list=[self.current_node,path,out]
        print("The assertion that the data remains unchanged,\n"
              "for node {0} following path {1} is {2}".format(*out_list))
        return out

    def is_graph_isomorphic(self):
        """Returns True if all nodes have closed paths that preserve the data, False otherwise"""
        out=True
        for node in self.node_names:
            self.move_to_node(node)
            if not self.check_closed_path:
                out=False
        return out

    def show(self,**options):
        """Shows the graph using matplotlib and networkx"""
        # Should be seperated to allow for fixed presentation?
        defaults={"descriptions":False,"edge_descriptions":False,"save_plot":False,
                 "path":None,"active_node":True,"directory":None,"specific_descriptor":self.graph_name.replace(" ","_"),
                  "general_descriptor":"plot","file_name":None,
                 "arrows":True,"node_size":1000,"font_size":10,"fix_layout":True}
        show_options={}
        for key,value in defaults.iteritems():
            show_options[key]=value
        for key,value in options.iteritems():
            show_options[key]=value
        if show_options["directory"] is None:
            show_options["directory"]=os.getcwd()
        if show_options["active_node"]:
            node_colors=[]
            for node in self.display_graph.nodes():
                if node==self.current_node:
                    node_colors.append('b')
                else:
                    if node in self.node_names:
                        node_colors.append('r')
                    elif node in self.external_node_names:
                        node_colors.append('g')
        else:
            node_colors=['r' for node in self.node_names]+['g' for node in self.node_names]
        #print("{0} is {1}".format('node_colors',node_colors))
        if show_options["descriptions"]:
            node_labels={node:self.node_descriptions[index] for index,
                               node in enumerate(self.node_names)}
            if self.external_node_names:
                for index,node in enumerate(self.external_node_names):
                    node_labels[node]=self.external_node_descriptions[index]
            networkx.draw_networkx(self.display_graph,arrows=show_options["arrows"],
                       labels=node_labels,node_color=node_colors,
                                   node_size=show_options["node_size"],font_size=show_options["font_size"],
                                   pos=self.display_layout)
            #print("{0} is {1}".format('node_labels',node_labels))
        else:
            networkx.draw_networkx(self.display_graph,arrows=show_options["arrows"],node_color=node_colors,
                                  node_size=show_options["node_size"],font_size=show_options["font_size"],
                                   pos=self.display_layout)

        plt.suptitle(self.options["graph_name"])
        if show_options["file_name"] is None:
            file_name=auto_name(specific_descriptor=show_options["specific_descriptor"],
                                general_descriptor=show_options["general_descriptor"],
                                directory=show_options["directory"],extension='png',padding=3)
        else:
            file_name=show_options["file_name"]
        if show_options["save_plot"]:
            #print file_name
            if show_options["path"]:
                plt.savefig(show_options["path"])
            else:
                plt.savefig(os.path.join(show_options["directory"],file_name))
        else:
            plt.show()
            fig=plt.gcf()
            return fig



class StringGraph(Graph):
    """String Graph is  a graph relating different string forms"""
    def __init__(self,**options):
        """Intializes the StringGraph Class by defining nodes and edges"""
        defaults={"graph_name":"StringGraph",
                  "node_names":['String','StringList'],
                  "node_descriptions":["A plain string",
                                       "A list of strings with no \\n, created with string.splitlines()"],
                  "current_node":'String',
                  "state":[1,0],
                  "data":"This is a test string\n it has to have multiple lines \n and many characters 34%6\n^",
                  "edge_2_to_1":edge_2_to_1,
                  "edge_1_to_2":edge_1_to_2
                 }
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        Graph.__init__(self,**self.options)
        self.add_node("File","String",String_to_File,"String",File_to_String,node_description="Plain File")
        self.add_node("CStringIo","String",String_to_CStringIo,"String",CStringIo_to_String,node_description="C File Like Object")
        self.add_node("StringIo","String",String_to_StringIo,"String",StringIo_to_String,node_description="File Like Object")
        self.add_edge(begin_node="StringList",end_node="File",edge_function=StringList_to_File)


# Changed from ColumnModeledGraph to TableGraph 12/14/2016 by AWS
class TableGraph(Graph):
    """Class that transforms column modeled data (table) from one format to another, use set_state to initialize to
    your data.
        #!python
        defaults={"graph_name":"Table Graph",
                  "node_names":['DataFrame','AsciiDataTable'],
                  "node_descriptions":["Pandas Data Frame","AsciiDataTable"],
                  "current_node":'DataFrame',
                  "state":[1,0],
                  "data":pandas.DataFrame([[1,2,3],[3,4,5]],columns=["a","b","c"]),
                  "edge_2_to_1":AsciiDataTable_to_DataFrame,
                  "edge_1_to_2":DataFrame_to_AsciiDataTable}
        """
    def __init__(self,**options):
        defaults={"graph_name":"Table Graph",
                  "node_names":['DataFrame','AsciiDataTable'],
                  "node_descriptions":["Pandas Data Frame","AsciiDataTable"],
                  "current_node":'DataFrame',
                  "state":[1,0],
                  "data":pandas.DataFrame([[1,2,3],[3,4,5]],columns=["a","b","c"]),
                  "edge_2_to_1":AsciiDataTable_to_DataFrame,
                  "edge_1_to_2":DataFrame_to_AsciiDataTable}
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        Graph.__init__(self,**self.options)
        self.add_node("HdfFile","DataFrame",DataFrame_to_HdfFile,
                      "DataFrame",HdfFile_to_DataFrame,
                      node_description="HDF File")
        self.add_node("XmlDataTable","AsciiDataTable",AsciiDataTable_to_XmlDataTable,
                      "AsciiDataTable",XmlDataTable_to_AsciiDataTable,
                      node_description="XML Data Table")
        # Need to add XML File and Html File using save and save_HTML()
        self.add_node("ExcelFile","DataFrame",DataFrame_to_ExcelFile,
                      "DataFrame",ExcelFile_to_DataFrame,
                      node_description="Excel File")

        self.add_node("OdsFile","ExcelFile",ExcelFile_to_OdsFile,
                      "ExcelFile",OdsFile_to_ExcelFile,"Open Office Spreadsheet")

        self.add_node("HtmlString","DataFrame",DataFrame_to_HtmlString,
                      "DataFrame",HtmlString_to_DataFrame,
                      node_description="HTML String")
        # Note a lot of the pandas reading and writing cause float64 round off errors
        # applymap(lambda x: np.around(x,10) any all float fields will fix this
        # also the column names move about in order
        self.add_node("JsonFile","DataFrame",DataFrame_to_JsonFile,
                      "DataFrame",JsonFile_to_DataFrame,
                      node_description="JSON File")
        self.add_node("JsonString","DataFrame",DataFrame_to_JsonString,
                      "DataFrame",JsonString_to_DataFrame,
                      node_description="JSON String")
        self.add_node("CsvFile","DataFrame",DataFrame_to_CsvFile,
                      "DataFrame",CsvFile_to_DataFrame,
                      node_description="CSV File")
        self.add_node("MatFile","AsciiDataTable",AsciiTable_to_MatFile,
                      "AsciiDataTable",MatFile_to_AsciiTable,
                      node_description="Matlab File")
        self.add_node("XmlFile","XmlDataTable",XmlDataTable_to_XmlFile,
                      "XmlDataTable",XmlFile_to_XmlDataTable,
                      node_description="XML DataTable Saved As a File")
        self.add_node("HtmlFile","HtmlString",HtmlString_to_HtmlFile,
                      "HtmlString",HtmlFile_to_HtmlString,
                      node_description="HTML File")
        self.add_edge("DataFrame","HtmlFile",DataFrame_to_HtmlFile)
        self.add_edge("JsonFile","XmlDataTable",JsonFile_to_XmlDataTable)
        self.add_external_node("XsltResultString","XmlDataTable",XmlBase_to_XsltResultString,
                               external_node_description="XSLT Results String")
        self.add_external_node("XsltResultFile","XmlDataTable",XmlBase_to_XsltResultFile,
                               external_node_description="XSLT Results File")
class ImageGraph(Graph):
    """A transformation graph for images node types are image formats and external nodes are
    common image processing functions
        #!python
        defaults={"graph_name":"Image Graph",
                  "node_names":['Image','png'],
                  "node_descriptions":["PIL Image","png"],
                  "current_node":'Image',
                  "state":[1,0],
                  "data":PIL.Image.open(os.path.join(TESTS_DIRECTORY,'test.png')),
                  "edge_2_to_1":File_to_Image,
                  "edge_1_to_2":lambda x: Image_to_FileType(x,file_path="test",extension="png")}
        """
    def __init__(self,**options):
        defaults={"graph_name":"Image Graph",
                  "node_names":['Image','png'],
                  "node_descriptions":["PIL Image","png"],
                  "current_node":'Image',
                  "state":[1,0],
                  "data":PIL.Image.open(os.path.join(TESTS_DIRECTORY,'test.png')),
                  "edge_2_to_1":File_to_Image,
                  "edge_1_to_2":lambda x: Image_to_FileType(x,file_path="test",extension="png")}
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        Graph.__init__(self,**self.options)
        self.add_node("jpg","Image",lambda x: Image_to_FileType(x,file_path="test",extension="jpg"),
                             "Image",File_to_Image,node_description="Jpg File")
        self.add_node("tiff","Image",lambda x: Image_to_FileType(x,file_path="test",extension="tiff"),
                             "Image",File_to_Image,node_description="Tif File")
        self.add_node("gif","Image",lambda x: Image_to_FileType(x,file_path="test",extension="gif"),
                             "Image",File_to_Image,node_description="Gif File")
        self.add_node("bmp","Image",lambda x: Image_to_FileType(x,file_path="test",extension="bmp"),
                             "Image",File_to_Image,node_description="BMP File")
        self.add_node("base64","png",PngFile_to_Base64,
                             "png",Base64_to_PngFile,node_description="Base 64 PNG")
        self.add_node("embeddedHTML","base64",Base64Png_to_EmbeddedHtmlString,
                             "base64",EmbeddedHtmlString_to_Base64Png,node_description="Embedded HTML of PNG")
        self.add_node("ndarray","png",PngFile_to_Ndarray,
                             "png",Ndarray_to_PngFile,node_description="Numpy Array")
        self.add_node("MatplotlibFigure","ndarray",Ndarray_to_MatplotlibFigure,
                             "png",MatplotlibFigure_to_PngFile,node_description="MatplotlibFigure")
        self.add_external_node("thumbnail","Image",Image_to_ThumbnailFile,external_node_description="JPEG Thumbnail")
        self.add_external_node("matplotlib","ndarray",Ndarray_to_Matplotlib,
                                      external_node_description="Matplotlib Plot")

class MetadataGraph(Graph):
    """Metadata Graph is a graph representing the content of key,value metadata"""
    def __init__(self,**options):
        """Intializes the metadata graph class"""
        defaults={"graph_name":"Metadata Graph",
                  "node_names":['Dictionary','JsonString'],
                  "node_descriptions":["Python Dictionary","Json string"],
                  "current_node":'Dictionary',
                  "state":[1,0],
                  "data":{"a":"First","b":"Second"},
                  "edge_2_to_1":JsonString_to_Dictionary,
                  "edge_1_to_2":Dictionary_to_JsonString}
        self.options={}
        for key,value in defaults.iteritems():
            self.options[key]=value
        for key,value in options.iteritems():
            self.options[key]=value
        Graph.__init__(self,**self.options)
        self.add_node("JsonFile","JsonString",JsonString_to_JsonFile,
                             "JsonString",JsonFile_to_JsonString,node_description="JSON File")
        self.add_node("XmlString","Dictionary",Dictionary_to_XmlString,
                             "Dictionary",XmlString_to_Dictionary,node_description="XML string")
        self.add_node("HtmlMetaString","Dictionary",Dictionary_to_HtmlMetaString,
                             "Dictionary",HtmlMetaString_to_Dictionary,node_description="HTML meta tags")
        self.add_node("XmlTupleString","Dictionary",Dictionary_to_XmlTupleString,
                             "Dictionary",XmlTupleString_to_Dictionary,node_description="Tuple Line")
        self.add_node("PickleFile","Dictionary",Dictionary_to_PickleFile,
                             "Dictionary",PickleFile_to_Dictionary,node_description="Pickled File")
        self.add_node("ListList","Dictionary",Dictionary_to_ListList,
                             "Dictionary",ListList_to_Dictionary,node_description="List of lists")
        self.add_node("HeaderList","Dictionary",Dictionary_to_HeaderList,
                             "Dictionary",HeaderList_to_Dictionary,node_description="Header List")
        self.add_node("DataFrame","Dictionary",Dictionary_to_DataFrame,
                             "Dictionary",DataFrame_to_Dictionary,node_description="Pandas DataFrame")
        self.add_node("AsciiDataTable","DataFrame",DataFrame_to_AsciiDataTable,
                             "DataFrame",AsciiDataTable_to_DataFrame,node_description="AsciiDataTable")
        self.add_node("MatFile","AsciiDataTable",AsciiTable_to_MatFile,
                             "AsciiDataTable",MatFile_to_AsciiDataTableKeyValue,node_description="Matlab")
        self.add_node("ExcelFile","DataFrame",DataFrame_to_ExcelFile,
                             "DataFrame",ExcelFile_to_DataFrame,node_description="excel")
        self.add_node("HdfFile","DataFrame",DataFrame_to_HdfFile,
                             "DataFrame",HdfFile_to_DataFrame,node_description="hdf file")
        self.add_node("CsvFile","DataFrame",DataFrame_to_CsvFile,
                             "DataFrame",CsvFile_to_DataFrame,node_description="CSV File")
        self.add_node("HtmlFile","DataFrame",DataFrame_to_HtmlFile,
                             "DataFrame",HtmlFile_to_DataFrame,node_description="HTML Table File")
        self.add_node("HtmlTableString","HtmlFile",HtmlFile_to_HtmlString,
                             "HtmlFile",HtmlString_to_HtmlFile,node_description="HTML Table String")
class TwoPortParameterGraph(Graph):
    """TwoPortParamterGraph is a content graph for two-port parameters,
    it transforms between S,T,Y,Z,ABCD and H parameters and matrix versions.
        #!python
        defaults={"graph_name":"Two Port Parameter Graph",
                          "node_names":["SFrequencyList",'SFrequencyMatrixList'],
                          "node_descriptions":["S Parameters","S Parameters in a Matrix"],
                          "current_node":'SFrequencyList',
                          "state":[1,0],
                          "data":[[1.0,.9,.436,.436,.9]],
                          "edge_2_to_1":FrequencyMatrixList_to_FrequencyList,
                          "edge_1_to_2":FrequencyList_to_FrequencyMatrixList,
                          "frequency_units":"GHz",
                          "Z01":50,
                          "Z02":50 }
"""
    def __init__(self,**options):

        defaults={"graph_name":"Two Port Parameter Graph",
                          "node_names":["SFrequencyList",'SFrequencyMatrixList'],
                          "node_descriptions":["S Parameters","S Parameters in a Matrix"],
                          "current_node":'SFrequencyList',
                          "state":[1,0],
                          "data":[[1.0,.9,.436,.436,.9]],
                          "edge_2_to_1":FrequencyMatrixList_to_FrequencyList,
                          "edge_1_to_2":FrequencyList_to_FrequencyMatrixList,
                          "frequency_units":"GHz",
                          "Z01":50,
                          "Z02":50 }
        graph_options={}
        for key,value in defaults.iteritems():
            graph_options[key]=value
        for key,value in options.iteritems():
            graph_options[key]=value
        Graph.__init__(self,**graph_options)

        self.add_node("TFrequencyMatrixList",
                        "SFrequencyMatrixList",SFrequencyMatrixList_to_TFrequencyMatrixList,
                        "SFrequencyMatrixList",TFrequencyMatrixList_to_SFrequencyMatrixList,
                        "T Parameters in a Matrix")

        self.add_node("TFrequencyList",
                        "TFrequencyMatrixList",FrequencyMatrixList_to_FrequencyList,
                        "TFrequencyMatrixList",FrequencyList_to_FrequencyMatrixList,
                        "T Parameters")

        self.add_node("ZFrequencyList",
                        "SFrequencyList",SFrequencyList_to_ZFrequencyList,
                        "TFrequencyList",ZFrequencyList_to_TFrequencyList,
                        "Z Parameters")

        self.add_node("ZFrequencyMatrixList",
                        "ZFrequencyList",FrequencyList_to_FrequencyMatrixList,
                        "ZFrequencyList",FrequencyMatrixList_to_FrequencyList,
                        "Z Parameters in a matrix")

        self.add_node("ABCDFrequencyList",
                        "ZFrequencyList",ZFrequencyList_to_ABCDFrequencyList,
                        "ZFrequencyList",ABCDFrequencyList_to_ZFrequencyList,
                        "ABCD Parameters")

        self.add_node("ABCDFrequencyMatrixList",
                        "ABCDFrequencyList",FrequencyList_to_FrequencyMatrixList,
                        "ABCDFrequencyList",FrequencyMatrixList_to_FrequencyList,
                        "ABCD Parameters in a matrix")

        self.add_node("HFrequencyList",
                        "ABCDFrequencyList",ABCDFrequencyList_to_HFrequencyList,
                        "ZFrequencyList",HFrequencyList_to_ZFrequencyList,
                        "h Parameters")

        self.add_node("HFrequencyMatrixList",
                        "HFrequencyList",FrequencyList_to_FrequencyMatrixList,
                        "HFrequencyList",FrequencyMatrixList_to_FrequencyList,
                        "H Parameters in a matrix")
        self.add_node("YFrequencyList",
                        "ABCDFrequencyList",ABCDFrequencyList_to_YFrequencyList,
                        "HFrequencyList",YFrequencyList_to_HFrequencyList,
                        "Y Parameters")

        self.add_node("YFrequencyMatrixList",
                        "YFrequencyList",FrequencyList_to_FrequencyMatrixList,
                        "YFrequencyList",FrequencyMatrixList_to_FrequencyList,
                        "Y Parameters in a matrix")

        self.add_edge(begin_node="ZFrequencyMatrixList",
                        end_node="YFrequencyMatrixList",
                        edge_function=ZFrequencyMatrixList_to_YFrequencyMatrixList)

        self.add_edge(begin_node="SFrequencyMatrixList",
                        end_node="ZFrequencyMatrixList",
                        edge_function=SFrequencyMatrixList_to_ZFrequencyMatrixList)

        self.add_edge(begin_node="ZFrequencyMatrixList",
                        end_node="TFrequencyMatrixList",
                        edge_function=ZFrequencyMatrixList_to_TFrequencyMatrixList)

        self.add_edge(begin_node="ABCDFrequencyList",
                        end_node="SFrequencyList",
                        edge_function=ABCDFrequencyList_to_SFrequencyList)

#-----------------------------------------------------------------------------
# Module Scripts
#TODO: Add test_Graph script currently lives in jupyter-notebooks
#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':
    pass