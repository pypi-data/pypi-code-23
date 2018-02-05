# Imports
import logging

import copy
import networkx as nx

from ..utilities.general import format_string_for_vistoms
from ..utilities.testing import check
from ..utilities.xmls import Element

from graph_kadmos import KadmosGraph
from mixin_mdao import MdaoMixin


# Settings for the logger
logger = logging.getLogger(__name__)


class ProcessGraph(KadmosGraph, MdaoMixin):

    def __init__(self, *args, **kwargs):
        super(ProcessGraph, self).__init__(*args, **kwargs)


class MdaoProcessGraph(ProcessGraph):

    ARCHITECTURE_CATS = {'all iterative blocks': ['optimizer', 'converger', 'doe'],
                         'all design variables': ['initial guess design variable', 'final design variable'],
                         'all pre-iter analyses': ['pre-coupling analysis', 'pre-iterator analysis']}

    def __init__(self, *args, **kwargs):
        super(MdaoProcessGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #
    def _create_cmdows_workflow_process_graph(self):
        """
        Method to add the processGraph element to a CMDOWS file.

        :return: CMDOWS processGraph element
        :rtype: Element
        """

        # Create workflow/processGraph
        cmdows_process_graph = Element('processGraph')
        cmdows_process_graph.add('name', self.graph.get('name'))

        # Create workflow/processGraph/edges
        cmdows_edges = cmdows_process_graph.add('edges')
        for u, v, w in self.edges(data=True):
            # Create workflow/dataGraph/edges/edge
            cmdows_edge = cmdows_edges.add('edge')
            cmdows_edge.add('fromExecutableBlockUID', u)
            cmdows_edge.add('toExecutableBlockUID', v)
            cmdows_edge.add('processStepNumber', w.get('process_step'))

        # Create workflow/processGraph/nodes
        cmdows_nodes = cmdows_process_graph.add('nodes')
        for n, data in self.nodes(data=True):
            # Create workflow/dataGraph/nodes/node
            cmdows_node = cmdows_nodes.add('node')
            cmdows_node.add('referenceUID', n)
            cmdows_node.add('processStepNumber', data.get('process_step'))
            cmdows_node.add('convergerStepNumber', data.get('converger_step'))
            cmdows_node.add('diagonalPosition', data.get('diagonal_position'))

        # Create workflow/processGraph/metadata
        cmdows_meta = cmdows_process_graph.add('metadata')
        cmdows_loop_nesting = cmdows_meta.add('loopNesting')
        cmdows_loop_nesting.add_process_hierarchy(self.graph['process_hierarchy'], self)

        return cmdows_process_graph

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             LOAD METHODS                                                         #
    # ---------------------------------------------------------------------------------------------------------------- #
    def _load_cmdows_workflow_process_graph(self, cmdows, nodes):
        """
        Method to load a MPG stored in a CMDOWS workflow/processGraph element

        :param cmdows: CMDOWS file
        :type cmdows: ElementTree
        :param nodes: nodes from data graph
        :type nodes: list
        :return: enriched MPG
        :rtype: MdaoProcessGraph
        """

        cmdows_process_graph = cmdows.find('workflow/processGraph')
        cmdows_nodes = cmdows_process_graph.find('nodes')
        if cmdows_nodes is not None:
            for node in list(cmdows_nodes):
                # Get new node info
                new_attr_dict = {'process_step': node.findasttext('processStepNumber'),
                                 'diagonal_position': node.findasttext('diagonalPosition')}
                if node.findasttext('convergerStepNumber') is not None:
                    new_attr_dict['converger_step'] = node.findasttext('convergerStepNumber')
                # Copy other node info
                attr_dict = nodes[node.findtext('referenceUID')]
                attr_dict.update(new_attr_dict)
                self.add_node(node.findtext('referenceUID'), attr_dict=attr_dict)
        cmdows_edges = cmdows_process_graph.find('edges')
        if cmdows_edges is not None:
            for edge in list(cmdows_edges):
                self.add_edge(edge.findtext('fromExecutableBlockUID'), edge.findtext('toExecutableBlockUID'),
                              attr_dict={'process_step': int(edge.findtext('processStepNumber'))})
            self.graph['process_hierarchy'] = self.get_process_hierarchy()

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CHECKING METHODS                                                      #
    # ---------------------------------------------------------------------------------------------------------------- #
    def _check_category_a(self):
        """Extended method to perform a category A check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(MdaoProcessGraph, self)._check_category_a()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')
        var_nodes = self.find_all_nodes(category='variable')

        # Get information
        n_nodes = self.number_of_nodes()
        n_functions = len(func_nodes)
        n_variables = len(var_nodes)

        # Checks on nodes
        category_check, i = check(n_variables != 0,
                                  'There are variable nodes present in the graph, namely: %s.' % str(var_nodes),
                                  status=category_check,
                                  category='A',
                                  i=i)
        category_check, i = check(n_nodes != n_functions,
                                  'The number of total nodes does not match number of function nodes.',
                                  status=category_check,
                                  category='A',
                                  i=i)
        for node in func_nodes:
            category_check, i_not = check('process_step' not in self.nodes[node],
                                          'The process_step attribute is missing on the node %s.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i)
            category_check, i_not = check('architecture_role' not in self.nodes[node],
                                          'The architecture_role attribute is missing on the node %s.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i+1)
            category_check, i_not = check(not self.has_node(self.COORDINATOR_STRING),
                                          'The %s node is missing in the graph.' % self.COORDINATOR_STRING,
                                          status=category_check,
                                          category='A',
                                          i=i+2)
        i += 3

        # Check on edges
        for u, v, d in self.edges(data=True):
            category_check, i_not = check('process_step' not in d,
                                          'The process_step attribute missing for the edge %s --> %s.' % (u, v),
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1

        # Return
        return category_check, i

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                              PRINTING METHODS                                                    #
    # ---------------------------------------------------------------------------------------------------------------- #
    def inspect_process(self):
        """Method to print the MPG."""

        print '\n- - - - - - - - - - -'
        print ' PROCESS INSPECTION  '
        print '- - - - - - - - - - -\n'
        print '\nNODES\n'
        for idx in range(0, self.number_of_nodes()):
            nodes = self.find_all_nodes(attr_cond=['diagonal_position', '==', idx])
            for node in nodes:
                print '- - - - -'
                print node
                print 'process step: ' + str(self.nodes[node]['process_step'])
                print 'diagonal pos: ' + str(self.nodes[node]['diagonal_position'])
                if 'converger_step' in self.nodes[node]:
                    print 'converger step: ' + str(self.nodes[node]['converger_step'])
        print '\nEDGES\n'
        for idx in range(0, self.number_of_edges() + 1):
            for u, v, d in self.edges(data=True):
                if d['process_step'] == idx:
                    print '- - - - -'
                    print u + ' ---> ' + v
                    print d['process_step']
        print '- - - - - - - - - - -\n'

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #
    def _add_diagonal_positions(self):
        """
        Method to add the diagonal positions of function blocks based on the monolithic architectures

        :return: function nodes with diagonal positions
        :rtype: None
        """

        # Get function ordering of MDAO graph and establish diagonal order list
        mg_function_ordering = self.graph['mg_function_ordering']
        diagonal_order = self.find_all_nodes(attr_cond=['architecture_role', '==',
                                                        self.ARCHITECTURE_ROLES_FUNS[0]])  # coordinator

        # Append pre-coupling functions
        if self.FUNCTION_ROLES[0] in mg_function_ordering:
            diagonal_order.extend(mg_function_ordering[self.FUNCTION_ROLES[0]])

        # Append pre-desvars functions
        if self.FUNCTION_ROLES[3] in mg_function_ordering:
            diagonal_order.extend(mg_function_ordering[self.FUNCTION_ROLES[3]])

        # Append optimizer or DOE block
        diagonal_order.extend(self.find_all_nodes(attr_cond=['architecture_role', '==',
                                                             self.ARCHITECTURE_ROLES_FUNS[1]]))  # optimizer
        diagonal_order.extend(self.find_all_nodes(attr_cond=['architecture_role', '==',
                                                             self.ARCHITECTURE_ROLES_FUNS[3]]))  # doe

        # Append post-desvars functions
        if self.FUNCTION_ROLES[4] in mg_function_ordering:
            diagonal_order.extend(mg_function_ordering[self.FUNCTION_ROLES[4]])

        # Append converger block
        diagonal_order.extend(self.find_all_nodes(attr_cond=['architecture_role', '==',
                                                             self.ARCHITECTURE_ROLES_FUNS[2]]))  # converger

        # Append coupled functions
        if self.FUNCTION_ROLES[1] in mg_function_ordering:
            diagonal_order.extend(mg_function_ordering[self.FUNCTION_ROLES[1]])

        # Append post-coupling functions
        if self.FUNCTION_ROLES[2] in mg_function_ordering:
            diagonal_order.extend(mg_function_ordering[self.FUNCTION_ROLES[2]])

        for diag_pos, node in enumerate(diagonal_order):
            self.nodes[node]['diagonal_position'] = diag_pos

        return

    def add_process(self, sequence, start_step, mdg, end_in_iterative_node=None):
        """Method to add a process to a list of functions.

        The sequence is assumed to be the order of the functions in the input list. The sequence is considered simple,
        since it is not analyzed for the possibility to run functions in parallel.

        :param sequence: list of functions in the required sequence
        :type sequence: list
        :param start_step: process step number for the first element in the sequence
        :type start_step: int
        :param mdg: data graph to be used for execution dependencies
        :type mdg: MdaoDataGraph
        :param end_in_iterative_node: (optional) iterative node to which the last function should go
        :type end_in_iterative_node: basestring
        """

        # Input assertions and checks
        assert isinstance(sequence, list)
        assert len(sequence) > 0, 'Sequence cannot be an empty list.'
        assert len(sequence) == len(set(sequence))
        assert isinstance(start_step, int) and start_step >= 0, 'Start step should be a positive integer.'
        if end_in_iterative_node:
            assert self.has_node(end_in_iterative_node), 'Node %s is not present in the graph' % end_in_iterative_node

        # Get initial coupling matrix of the nodes in the sequence
        coupling_matrix_1 = mdg.get_coupling_matrix(node_selection=sequence)
        process_step = start_step+1

        # Deepcopy sequence
        sequence = copy.deepcopy(sequence)

        while sequence:
            # Determine first and second group of nodes
            nodes_1, coupling_matrix_2 = get_executable_functions(coupling_matrix_1, sequence)
            [sequence.remove(node_1) for node_1 in nodes_1]
            nodes_2, _ = get_executable_functions(coupling_matrix_2, sequence)

            # If nodes_1 contains an iterator as first element + other nodes, then split into nodes_1 and nodes_2
            if len(nodes_1) > 1 and self.nodes[nodes_1[0]]['architecture_role'] in self.ARCHITECTURE_ROLES_FUNS[:4]:
                nodes_2 = nodes_1[1:]
                nodes_1 = [nodes_1[0]]
                sequence = nodes_2 + sequence
                coupling_matrix_2 = coupling_matrix_1[1:, 1:]
            # Else if iterator as last element
            elif len(nodes_1) > 1 and self.nodes[nodes_1[-1]]['architecture_role'] in self.ARCHITECTURE_ROLES_FUNS[:4]:
                nodes_2 = [nodes_1[-1]]
                nodes_1 = nodes_1[:-1]
                sequence = nodes_2 + sequence
                coupling_matrix_2 = coupling_matrix_1[len(nodes_1):, len(nodes_1):]

            # If nodes_2 contains an iterator as last element, then remove that one
            if len(nodes_2) > 1 and self.nodes[nodes_2[-1]]['architecture_role'] in self.ARCHITECTURE_ROLES_FUNS[:4]:
                nodes_2 = nodes_2[:-1]

            # Coupling first and second nodes based on data links
            if nodes_2:
                for i_1, node_1 in enumerate(nodes_1):
                    if 'process_step' not in self.nodes[node_1]:
                        self.nodes[node_1]['process_step'] = process_step-1
                    for i_2, node_2 in enumerate(nodes_2):
                        if 'process_step' not in self.nodes[node_2]:
                            self.nodes[node_2]['process_step'] = process_step
                        if coupling_matrix_1[i_1, i_2+len(nodes_1)] > 0:
                            self.add_edge(node_1, node_2, process_step=process_step)

                # If first node does not have a second node link, then connect to all (and give warning!)...
                for node_1 in nodes_1:
                    if not set(self.get_targets(node_1)).intersection(set(nodes_2)):
                        # Give out a warning if it seems appropriate
                        if self.nodes[node_1]['architecture_role'] not in self.ARCHITECTURE_ROLES_FUNS[:4] and \
                                self.nodes[nodes_2[0]]['architecture_role'] not in self.ARCHITECTURE_ROLES_FUNS[:4]:
                            logger.warning('In the process graph determination node {} does not have proper data '
                                           'connections with following node group {}. Execution sequence of functions '
                                           'might be optimized.'.format(node_1, nodes_2))
                        [self.add_edge(node_1, node_2, process_step=process_step) for node_2 in nodes_2]

                # If second node does not have a first node link, then connect to all (and give warning!)...
                for node_2 in nodes_2:
                    if not set(self.get_sources(node_2)).intersection(set(nodes_1)):
                        # Give out a warning if it seems appropriate
                        if self.nodes[node_2]['architecture_role'] not in self.ARCHITECTURE_ROLES_FUNS[:4] and \
                                self.nodes[nodes_1[0]]['architecture_role'] not in self.ARCHITECTURE_ROLES_FUNS[:4]:
                            logger.warning('In the process graph determination node {} does not have proper data '
                                           'connections with following node group {}. Execution sequence of functions '
                                           'might be optimized.'.format(node_2, nodes_1))
                        [self.add_edge(node_1, node_2, process_step=process_step) for node_1 in nodes_1]
            else:
                # End in iterative node or simply end function
                if end_in_iterative_node:
                    [self.add_edge(node_1, end_in_iterative_node, process_step=process_step) for node_1 in nodes_1]
                    self.nodes[end_in_iterative_node]['converger_step'] = process_step
            # Increment process step
            process_step += 1
            coupling_matrix_1 = coupling_matrix_2

        return

    def connect_nested_iterators(self, master, slave):
        """Method to connect a slave iterator to a master iterator in a nested configuration.

        An example is if a converger inside an optimizer in MDF needs to be linked back.

        :param master: upper iterator node in the nested configuration
        :type master: basestring
        :param slave: lower iterator node in the nested configuration
        :type slave: basestring
        """

        assert self.has_node(master), 'Node %s not present in the graph.' % master
        assert self.has_node(slave), 'Node %s not present in the graph.' % slave
        assert 'converger_step' in self.nodes[slave], 'Slave node %s needs to have a converger_step.' % slave
        self.add_edge(slave, master, process_step=self.nodes[slave]['converger_step'] + 1)
        self.nodes[master]['converger_step'] = self.nodes[slave]['converger_step'] + 1

        return

    def get_node_text(self, node):
        """Method to determine the text of a function node (for use in a XDSM diagram).

        :param node: node
        :type node: basestring
        :return: node text for in the XDSM function box
        :rtype: basestring
        """

        # Measure to make sure a label is written
        node_label = self.nodes[node].get('label', str(node))
        assert node_label, 'Node label seems to be empty for node: %s' % node

        if 'converger_step' in self.nodes[node] and node != self.COORDINATOR_STRING:
            node_text = ('$' + str(self.nodes[node]['process_step']) + ',' + str(self.nodes[node]['converger_step']) +
                         r'\to' + str(self.nodes[node]['process_step'] + 1) +
                         r'$:\\[1pt]' + node_label)
        elif 'converger_step' in self.nodes[node] and node == self.COORDINATOR_STRING:
            node_text = ('$' + str(self.nodes[node]['process_step']) + ',' + str(self.nodes[node]['converger_step']) +
                         r'$:\\[1pt]' + node_label)
        elif 'process_step' in self.nodes[node]:
            node_text = ('$' + str(self.nodes[node]['process_step']) + r'$:\\[1pt]' + node_label)
        else:
            node_text = node_label

        return node_text

    def get_process_list(self, use_d3js_node_ids=True):
        """Method to get the xdsm workflow process list (for use in dynamic visualizations).

        :param use_d3js_node_ids: setting whether node names should be changed into node ids according to D3js notation.
        :type use_d3js_node_ids: bool
        :return: process list
        :rtype: list
        """

        # Input assertions
        assert isinstance(use_d3js_node_ids, bool)

        # Find first diagonal node
        first_nodes = self.find_all_nodes(attr_cond=['diagonal_position', '==', 0])
        assert len(first_nodes) == 1, 'Only one node per diagonal position is allowed.'
        first_node = first_nodes[0]
        assert 'converger_step' in self.nodes[first_node], 'First diagonal node should have a converger_step attribute.'
        max_step = self.nodes[first_node]['converger_step']
        process_list = []
        for step in range(0, max_step+1):
            process_list.append({'step_number': step,
                                 'process_step_blocks': [],
                                 'converger_step_blocks': [],
                                 'edges': []})
            process_step_nodes = self.find_all_nodes(attr_cond=['process_step', '==', step])
            converger_step_nodes = self.find_all_nodes(attr_cond=['converger_step', '==', step])
            if not process_step_nodes and not converger_step_nodes:
                raise IOError('Process block data missing for step %d.' % step)
            elif process_step_nodes and converger_step_nodes:
                raise IOError('Invalid process block data for step %d.' % step)
            # In case of regular process steps, determine their list positions
            for step_node in process_step_nodes:
                if use_d3js_node_ids:
                    node_name = format_string_for_vistoms(step_node, prefix='id_')
                else:
                    node_name = step_node
                process_list[step]['process_step_blocks'].append(node_name)
            for step_node in converger_step_nodes:
                if use_d3js_node_ids:
                    node_name = format_string_for_vistoms(step_node, prefix='id_')
                else:
                    node_name = step_node
                process_list[step]['converger_step_blocks'].append(node_name)
            for edge in self.edges(data=True):
                if edge[2]['process_step'] == step:
                    if use_d3js_node_ids:
                        edge0_name = format_string_for_vistoms(edge[0], prefix='id_')
                        edge1_name = format_string_for_vistoms(edge[1], prefix='id_')
                    else:
                        edge0_name = edge[0]
                        edge1_name = edge[1]
                    process_list[step]['edges'].append((edge0_name, edge1_name))

        return process_list

    def get_process_hierarchy(self):
        """
        Method to assess the hierarchy of the process based on the process lines in a ProcessGraph.

        :return: nested list with process hierarchy, e.g. [COOR, A, [OPT, [CONV, D1, D2], F1, G1, G2]]
        :rtype: list
        """
        # Find the step 0 node
        start_nodes = self.find_all_nodes(attr_cond=['process_step', '==', 0])
        assert len(start_nodes) == 1, 'There can only be one start node with process step number 0.'
        start_node = start_nodes[0]

        # Get the simple cycles in a set/list
        cycles = self.get_ordered_cycles()

        # Start process hierarchy object
        process_hierarchy = get_process_list_iteratively(start_node, cycles)
        return process_hierarchy

    def get_ordered_cycles(self):
        """Method to get the cycles of a process graph ordered according to process step number.

        :return: list with the cycles of a graph ordered based on PSN
        :rtype: list
        """
        cycles = list(nx.simple_cycles(self))
        min_process_steps = []
        neat_cycles = []
        for cycle in cycles:
            min_process_steps.append(self.get_lowest_psn(cycle)[0])
            neat_cycles.append(self.get_ordered_cycle(cycle))
        ordered_cycles = [x for _, x in sorted(zip(min_process_steps, neat_cycles))]
        return ordered_cycles

    def get_lowest_psn(self, cycle):
        """Method to retrieve the lowest process step number (PSN) of a list of nodes in a cycle.

        :param cycle: list with nodes on a cycle
        :type cycle: list
        :return: the minimal PSN and the index of the first element having this PSN
        :rtype: tuple
        """
        process_steps = [self.nodes[node]['process_step'] for node in cycle]
        min_process_step = min(process_steps)
        min_process_step_idx = process_steps.index(min_process_step)
        return min_process_step, min_process_step_idx

    def get_ordered_cycle(self, cycle):

        _, idx = self.get_lowest_psn(cycle)
        return cycle[idx:] + cycle[:idx]


def get_process_list_iteratively(cycle_node, cycles):
    """Method to obtain the process list of a collection of cycles given an iterative cycle_node. The process is
    iterative, since for every subcycle found the method is called again.

    :param cycle_node: the node that is starting and closing the cycle (e.g. coordinator, optimizer, etc.)
    :type cycle_node: str
    :param cycles: collection of cycles found in the graph
    :type cycles: list
    :return: the process list, e.g. [COOR, A, [OPT, [CONV, D1, D2], F1, G1, G2]]
    :rtype: list
    """
    sub_list = [cycle_node, []]
    current_cycles = [cycle for cycle in cycles if cycle_node in cycle]
    other_cycles = [cycle for cycle in cycles if cycle_node not in cycle]
    subcycle_nodes = []
    for current_cycle in current_cycles:
        cycle_nodes = [node for node in current_cycle if node != cycle_node]
        for node in cycle_nodes:
            node_in_other_subcycles = False
            for other_cycle in other_cycles:
                if node in other_cycle and cycle_node not in other_cycle:
                    node_in_other_subcycles = True
            # If node is in other subcycles, perform function iteratively
            # First filter out all cycles that contain the cycle_node -> filtered_cycles
            # sublist[1].append(get_process_list_iteratively(node, filtered_cycles)
            if node_in_other_subcycles:
                if node not in subcycle_nodes:
                    filtered_cycles = list(cycles)
                    for cycle in list(filtered_cycles):
                        if cycle_node in cycle:
                            filtered_cycles.remove(cycle)
                    subcycle_nodes.append(node)
                    sub_list[1].append(get_process_list_iteratively(node, filtered_cycles))
            # If node is not in any other cycles, simply add to this one
            else:
                if node not in sub_list[1]:
                    sub_list[1].append(node)
    return sub_list


def get_executable_functions(coupling_matrix, sequence):
    """
    Method to determine which of the functions in the process graph are executable based on data dependencies from the
    MDG.

    :param coupling_matrix: coupling matrix of the MDG
    :type coupling_matrix: array.py
    :param sequence: sequence of functions to be analyzed
    :type sequence: list
    :return: executable functions and updated coupling matrix with removed rows and columns
    :rtype: tuple
    """

    assert len(coupling_matrix) == len(sequence), "Coupling matrix size and sequence length should match."

    # Return empty lists if the sequence is empty
    if not sequence:
        return [], []

    # Perform analysis for non-empty sequence
    upper_columns_empty = True
    functions = [sequence[0]]
    updated_coupling_matrix = coupling_matrix[1:, 1:]

    col = 1
    while upper_columns_empty and col < len(coupling_matrix):
        if sum(coupling_matrix[:col, col]) == 0:
            functions.append(sequence[col])
            updated_coupling_matrix = updated_coupling_matrix[1:, 1:]
        else:
            upper_columns_empty = False
        col += 1

    return functions, updated_coupling_matrix
