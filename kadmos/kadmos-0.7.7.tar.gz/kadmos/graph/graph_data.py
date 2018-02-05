# Imports
import itertools
import copy
import logging
import distutils.util
import numbers
import re
import random

import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from types import NoneType
from ..utilities import prompting
from ..utilities import printing
from ..utilities.general import make_camel_case, unmake_camel_case, make_plural, get_list_entries, translate_dict_keys, \
    get_mdao_setup
from ..utilities.testing import check
from ..utilities.plotting import AnnoteFinder
from ..utilities.xmls import Element

from graph_kadmos import KadmosGraph

from mixin_mdao import MdaoMixin
from mixin_kechain import KeChainMixin


# Settings for the logger
logger = logging.getLogger(__name__)


class DataGraph(KadmosGraph):

    OPTIONS_FUNCTION_ORDER_METHOD = ['manual', 'minimum feedback']

    def __init__(self, *args, **kwargs):
        super(DataGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _create_cmdows_problem_def(self):

        # Create problemDefinition
        cmdows_problem_definition = Element('problemDefinition')
        graph_problem_formulation = self.graph.get('problem_formulation')
        cmdows_problem_definition.set('uID', str(graph_problem_formulation.get('mdao_architecture')) +
                                      str(graph_problem_formulation.get('convergence_type')))

        # Create problemDefinition/problemFormulation
        cmdows_problem_formulation = cmdows_problem_definition.add('problemFormulation')
        graph_problem_formulation = self.graph.get('problem_formulation')
        cmdows_problem_formulation.add('mdaoArchitecture', graph_problem_formulation.get('mdao_architecture'))
        cmdows_problem_formulation.add('convergerType', graph_problem_formulation.get('convergence_type'))
        cmdows_executable_blocks_order = cmdows_problem_formulation.add('executableBlocksOrder')
        for index, item in enumerate(graph_problem_formulation.get('function_order')):
            # Create problemDefinition/problemFormulation/executableBlocksOrder/executableBlock
            cmdows_executable_blocks_order.add('executableBlock', item, attrib={'position': str(index + 1)})
        cmdows_problem_formulation.add('allowUnconvergedCouplings',
                                       str(graph_problem_formulation.get('allow_unconverged_couplings')).lower())

        # Create problemDefinition/problemFormulation/doeSettings
        graph_settings = graph_problem_formulation.get('doe_settings')
        if graph_settings is not None:
            cmdows_settings = cmdows_problem_formulation.add('doeSettings')
            cmdows_settings.add('doeMethod', graph_settings.get('doe_method'))
            cmdows_settings.add('doeSeeds', graph_settings.get('doe_seeds'))
            cmdows_settings.add('doeRuns', graph_settings.get('doe_runs'))

        # Create problemDefinition/problemRoles
        cmdows_problem_roles = cmdows_problem_definition.add('problemRoles')
        # Create problemDefinition/problemRoles/parameters
        cmdows_parameters = cmdows_problem_roles.add('parameters')
        # Create problemDefinition/problemRoles/parameters/...
        for cmdows_parameterIndex, cmdows_parameterDef in enumerate(self.CMDOWS_ROLES_DEF):
            cmdows_parameter = cmdows_parameters.add(cmdows_parameterDef[0] + 's')
            graph_attr_cond = ['problem_role', '==', self.PROBLEM_ROLES_VARS[cmdows_parameterIndex]]
            graph_parameter = self.find_all_nodes(category='variable', attr_cond=graph_attr_cond)
            for graph_problem_role in graph_parameter:
                cmdows_problem_role = cmdows_parameter.add(cmdows_parameterDef[0])
                cmdows_problem_role.set('uID',
                                        self.PROBLEM_ROLES_VAR_SUFFIXES[cmdows_parameterIndex] +
                                        str(graph_problem_role))
                cmdows_problem_role.add('parameterUID', graph_problem_role)
                for cmdows_problem_role_attr in cmdows_parameterDef[1]:
                    if cmdows_problem_role_attr == 'samples':
                        # Create problemDefinition/problemRoles/parameters/designVariables/designVariable/samples
                        cmdows_samples = cmdows_problem_role.add('samples')
                        if self.node[graph_problem_role].get(cmdows_problem_role_attr) is not None:
                            for idx, itm in enumerate(self.node[graph_problem_role].get(cmdows_problem_role_attr)):
                                cmdows_samples.add('sample', itm, attrib={'position': str(idx + 1)})
                    else:
                        cmdows_problem_role.add(self.CMDOWS_ATTRIBUTE_DICT[cmdows_problem_role_attr],
                                                self.node[graph_problem_role].get(cmdows_problem_role_attr),
                                                camel_case_conversion=True)

        # Create problemDefinition/problemRoles/executableBlocks
        cmdows_executable_blocks = cmdows_problem_roles.add('executableBlocks')
        graph_executable_blocks = self.graph['problem_formulation']['function_ordering']
        # Create problemDefinition/problemRoles/executableBlocks/...
        for executable_block in self.FUNCTION_ROLES:
            if graph_executable_blocks.get(executable_block) is not None:
                if len(graph_executable_blocks.get(executable_block)) != 0:
                    cmdows_key = cmdows_executable_blocks.add(make_camel_case(executable_block) + 'Blocks')
                    for graph_block in graph_executable_blocks.get(executable_block):
                        cmdows_key.add(make_camel_case(executable_block) + 'Block', graph_block)

        return cmdows_problem_definition

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             LOAD METHODS                                                         #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _load_cmdows_problem_def(self, cmdows):

        graph_problem_form = {}

        cmdows_problem_formulation = cmdows.find('problemDefinition/problemFormulation')
        if cmdows_problem_formulation is not None:
            graph_problem_form['mdao_architecture'] = cmdows_problem_formulation.findtext('mdaoArchitecture')
            graph_problem_form['convergence_type'] = cmdows_problem_formulation.findtext('convergerType')
            cmdows_executable_blocks = cmdows_problem_formulation.find('executableBlocksOrder').findall(
                'executableBlock')
            cmdows_executable_blocks_order = [None] * len(list(cmdows_executable_blocks))
            for cmdows_executable_block in cmdows_executable_blocks:
                cmdows_executable_blocks_order[int(cmdows_executable_block.get('position')
                                                   ) - 1] = cmdows_executable_block.text
            graph_problem_form['function_order'] = cmdows_executable_blocks_order
            graph_problem_form['allow_unconverged_couplings'] = bool(distutils.util.strtobool(
                cmdows_problem_formulation.findtext('allowUnconvergedCouplings')))
            graph_problem_form['doe_settings'] = {}
            cmdows_doe_settings = cmdows_problem_formulation.find('doeSettings')
            if cmdows_doe_settings is not None:
                for cmdows_doe_setting in list(cmdows_doe_settings):
                    graph_problem_form['doe_settings'][unmake_camel_case(cmdows_doe_setting.tag
                                                                         )] = cmdows_doe_setting.text

        cmdows_problem_roles = cmdows.find('problemDefinition/problemRoles')
        if cmdows_problem_roles is not None:
            graph_problem_form['function_ordering'] = {}
            cmdows_executable_blocks = cmdows_problem_roles.find('executableBlocks')
            for role in self.FUNCTION_ROLES:
                cmdows_blocks = cmdows_executable_blocks.find(make_camel_case(role) + 'Blocks')
                if cmdows_blocks is None:
                    arr = list()
                else:
                    arr = list()
                    for cmdows_block in list(cmdows_blocks):
                        if self.node.get(cmdows_block.text) is None:
                            # Add node if it does not exist yet
                            self.add_node(cmdows_block.text, category='function')
                        self.node[cmdows_block.text]['problem_role'] = role
                        arr.append(cmdows_block.text)
                graph_problem_form['function_ordering'][role] = arr

            variable_types = [make_plural(role[0]) for role in self.CMDOWS_ROLES_DEF]
            for variable_type in variable_types:
                cmdows_variables = cmdows_problem_roles.find('parameters/' + variable_type)
                if cmdows_variables is not None:
                    for cmdows_variable in list(cmdows_variables):
                        cmdows_parameter_uid = cmdows_variable.findtext('parameterUID')
                        cmdows_suffix = '__' + re.findall(r'(?<=__).*?(?=__)', cmdows_variable.get('uID'))[0] + '__'
                        # Add problem role
                        try:
                            self.node[cmdows_parameter_uid]['problem_role'] = self.CMDOWS_ROLES_DICT_INV[cmdows_suffix]
                            # TODO: Find a more elegant way to handle samples and parameterUID
                            for attribute in cmdows_variable.getchildren():
                                if attribute.tag == 'samples':
                                    cmdows_samples = attribute.findall('sample')
                                    cmdows_sample_data = [None] * len(list(cmdows_samples))
                                    for cmdows_sample in cmdows_samples:
                                        cmdows_sample_data[int(cmdows_sample.get('position')) - 1] = float(cmdows_sample.text)
                                    self.node[cmdows_parameter_uid]['samples'] = cmdows_sample_data
                                    cmdows_variable.remove(attribute)
                            self.node[cmdows_parameter_uid].update(cmdows.finddict(cmdows_variable, camel_case_conversion=True))
                            del self.node[cmdows_parameter_uid]['parameter_u_i_d']
                        except KeyError:
                            logger.error('Could not find the node "{}" for some reason when loading the CMDOWS'
                                         .format(cmdows_parameter_uid))
                            pass

        self.graph['problem_formulation'] = graph_problem_form

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                         GRAPH-SPECIFIC METHODS                                                   #
    # ---------------------------------------------------------------------------------------------------------------- #

    def mark_as_design_variable(self, node, lower_bound=None, upper_bound=None, samples=None, nominal_value=0.0):
        """Method to mark a single node as a design variable and add the required metadata for its definition.

        :param node:
        :param lower_bound:
        :param upper_bound:
        :param samples:
        :return:
        """
        # Input assertions
        assert self.has_node(node), 'Node %s is not present in the graph.' % node
        assert isinstance(lower_bound, (numbers.Number, list, NoneType)), \
            'Lower bound should be a number or list of numbers.'
        assert isinstance(upper_bound, (numbers.Number, list, NoneType)), \
            'Upper bound should be a number or list of numbers.'
        assert isinstance(samples, (list, NoneType)), 'Samples should be a list.'

        # Mark nodes
        self.node[node]['problem_role'] = self.PROBLEM_ROLES_VARS[0]
        if lower_bound is not None:
            self.node[node]['valid_ranges'] = {'limit_range':{'minimum': lower_bound}}
        if upper_bound is not None:
            if 'valid_ranges' in self.node[node]:
                if 'limit_range' in self.node[node]['valid_ranges']:
                    self.node[node]['valid_ranges']['limit_range']['maximum'] = upper_bound
                else:
                    self.node[node]['valid_ranges']['limit_range'] = {'maximum': upper_bound}
            else:
                self.node[node]['valid_ranges'] = {'limit_range': {'maximum': upper_bound}}
        if samples is not None:
            self.node[node]['samples'] = samples
        self.node[node]['nominal_value'] = nominal_value

        return

    def mark_as_design_variables(self, nodes, lower_bounds=None, upper_bounds=None, samples=None, nominal_values=None):
        """Method to mark a list of nodes as design variable and add metadata.

        :param nodes: list of nodes present in the graph
        :type nodes: list or str
        :param lower_bounds: list of lower bound values
        :type lower_bounds: list or numbers.Number
        :param upper_bounds: list of upper bounds
        :type upper_bounds: list or numbers.Number
        :param samples: nested list of kadmos values
        :type samples: list
        :param nominal_values: list of nominal values
        :type nominal_values: list or numbers.Number
        """

        # Input assertions
        assert isinstance(nodes, list), 'Input nodes should be a list of graph nodes. Use mark_as_design_variable for single node.'
        if isinstance(lower_bounds, numbers.Number) or lower_bounds is None:
            lower_bounds = [lower_bounds]*len(nodes)
        else:
            assert isinstance(lower_bounds, list), 'Lower bounds should be a list.'
            assert len(lower_bounds) == len(nodes), 'Number of lower bounds is not equal to the number of nodes.'
        if isinstance(upper_bounds, numbers.Number) or upper_bounds is None:
            upper_bounds = [upper_bounds]*len(nodes)
        else:
            assert isinstance(upper_bounds, list), 'Upper bounds should be a list.'
            assert len(upper_bounds) == len(nodes), 'Number of upper bounds is not equal to the number of nodes.'
        if isinstance(nominal_values, numbers.Number) or nominal_values is None:
            nominal_values = [nominal_values]*len(nodes)
        else:
            assert isinstance(nominal_values, list), 'Nominal values should be a list.'
            assert len(nominal_values) == len(nodes), 'Number of nominal values is not equal to the number of nodes.'
        if isinstance(samples, numbers.Number) or samples is None:
            samples = [samples]*len(nodes)
        else:
            assert isinstance(samples, list), 'Nominal values should be a list.'
            assert len(samples) == len(nodes), 'Number of nominal values is not equal to the number of nodes.'

        # Mark nodes
        for node,lb,ub,sm,nv in zip(nodes, lower_bounds, upper_bounds, samples, nominal_values):
            self.mark_as_design_variable(node, lower_bound=lb, upper_bound=ub, samples=sm, nominal_value=nv)

        return

    def mark_as_objective(self, node, remove_unused_outputs=False):
        """Method to mark a single node as objective.

        :param node: variable node
        :type node: basestring
        """

        # Input assertions
        assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Mark node
        self.node[node]['problem_role'] = self.PROBLEM_ROLES_VARS[1]

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def mark_as_constraint(self, node, operator, reference_value, remove_unused_outputs=False):
        """Method to mark a node as a constraint.

        :param node: node to be marked (on the left side of the operator
        :type nodes: str
        :param operator: constraint operator
        :type operator: str
        :param reference_value: value on the right side of the operator
        :type reference_value: numbers.Number
        """

        # Input assertions
        possible_operators = ['==', '>', '<', '>=', '<=']
        assert self.has_node(node), 'Node %s not present in the graph.' % node
        assert operator in possible_operators, 'Operator has to be one of the following: %s' % possible_operators
        assert isinstance(reference_value, (numbers.Number, list)), 'Reference value is not a number or list.'
        # Mark nodes
        self.node[node]['problem_role'] = self.PROBLEM_ROLES_VARS[2]
        self.node[node]['constraint_operator'] = operator
        self.node[node]['reference_value'] = reference_value
        if operator == '==':
            self.node[node]['constraint_type'] = 'equality'
        else:
            self.node[node]['constraint_type'] = 'inequality'

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def mark_as_constraints(self, nodes, operators, reference_values, remove_unused_outputs=False):
        """Method to mark multiple nodes as constraints.

        :param nodes: list of nodes to be marked.
        :param operators: operators to be implemented (as list per node or as single operator for all)
        :param reference_values: reference values to be used (as list of values per node or as single value for all)
        :return: graph with enriched constraint nodes
        """

        # Input assertions
        poss_ops = ['==', '>', '<', '>=', '<=']
        assert isinstance(nodes, list), 'Input nodes should be a list of graph nodes. Use mark_as_constraint for single node.'
        if isinstance(operators, str):
            operators = [operators]*len(nodes)
        else:
            assert isinstance(operators, list), 'Operators should be a list.'
            assert len(operators) == len(nodes), 'Number of operators is not equal to the number of nodes.'
        if isinstance(reference_values, numbers.Number):
            reference_values = [reference_values]*len(nodes)
        else:
            assert isinstance(reference_values, list), 'Reference values should be a list.'
            assert len(reference_values) == len(nodes), 'Number of reference values is not equal to the number of nodes.'
        for node,op,ref in zip(nodes,operators,reference_values):
            self.mark_as_constraint(node,op,ref)

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def mark_as_qois(self, nodes, remove_unused_outputs=False):
        """Function to mark a list of nodes as quantity of interest.

        :param nodes: list of nodes present in the graph
        :type nodes: list
        """

        # Input assertions
        assert isinstance(nodes, list)
        for node in nodes:
            assert self.has_node(node), 'Node %s is not present in the graph.' % node

        # Mark nodes
        for node in nodes:
            self.node[node]['problem_role'] = self.PROBLEM_ROLES_VARS[3]

        if remove_unused_outputs:
            self.remove_unused_outputs()

        return

    def remove_unused_outputs(self):
        """ Function to remove output nodes from an FPG which do not have a problem role.

        :return: the nodes that were removed
        :rtype: list
        """
        # TODO: Reposition this and other functions to the FPG class.
        output_nodes = self.find_all_nodes(subcategory='all outputs')
        removed_nodes = []
        for output_node in output_nodes:
            if 'problem_role' not in self.node[output_node]:
                self.remove_node(output_node)
                removed_nodes.append(output_node)
        return removed_nodes

    def get_coupling_matrix(self, function_order_method='manual', node_selection=None):
        """Function to determine the role of the different functions in the FPG.

        :param function_order_method: algorithm to be used for the order in which the functions are executed.
        :type function_order_method: basestring
        :param node_selection: selection of nodes for which the coupling matrix will be calculated only
        :type node_selection: list
        :return: graph with enriched function node attributes and function problem role dictionary
        :rtype: FundamentalProblemGraph
        """

        # Make a copy of the graph, check it and remove all inputs and outputs
        if node_selection:
            graph = self.get_subgraph_by_function_nodes(node_selection)
        else:
            graph = self.deepcopy()
        nodes_to_remove = list()
        # TODO: Consider using the check function
        nodes_to_remove.extend(graph.find_all_nodes(subcategory='all inputs'))
        nodes_to_remove.extend(graph.find_all_nodes(subcategory='all outputs'))
        graph.remove_nodes_from(nodes_to_remove)

        # Determine and check function ordering method
        assert function_order_method in self.OPTIONS_FUNCTION_ORDER_METHOD
        if function_order_method == 'manual':
            if node_selection:
                function_order = node_selection
            else:
                assert 'function_order' in graph.graph['problem_formulation'], 'function_order must be given as attribute.'
                function_order = graph.graph['problem_formulation']['function_order']
        elif function_order_method == 'random':
            function_order = graph.find_all_nodes(category='function')

        # First store all the out- and in-edge variables per function
        function_var_data = dict()
        # noinspection PyUnboundLocalVariable
        for function in function_order:
            function_var_data[function] = dict(in_vars=set(), out_vars=set())
            function_var_data[function]['in_vars'] = [edge[0] for edge in graph.in_edges(function)]
            function_var_data[function]['out_vars'] = [edge[1] for edge in graph.out_edges(function)]
        # Create an empty matrix
        coupling_matrix = np.zeros((len(function_order), len(function_order)), dtype=np.int)
        # Create the coupling matrix (including circular dependencies)
        for idx1, function1 in enumerate(function_order):
            for idx2, function2 in enumerate(function_order):
                n_coupling_vars = len(set(function_var_data[function1]['out_vars']).
                                      intersection(set(function_var_data[function2]['in_vars'])))
                coupling_matrix[idx1, idx2] = n_coupling_vars

        return coupling_matrix

    def get_possible_function_order(self, method, multi_start=None, check_graph=False):
        """ Method to find a possible function order, in the order: pre-coupled, coupled, post-coupled functions

        :param method: algorithm which will be used to minimize the feedback loops
        :type method: str
        :param multi_start: start the algorithm from multiple starting points
        :type multi_start: int
        :param check_graph: check whether graph has problematic variables
        :type check_graph: bool
        :return Possible function order
        :rtype list
        """

        # Input assertions
        if check_graph:
            assert not self.find_all_nodes(subcategory='all problematic variables'), \
                'Graph still has problematic variables.'

        # Get function graph
        function_graph = self.get_function_graph()
        function_graph.remove_edges_from(function_graph.selfloop_edges())

        # Add a super node in which the coupled functions will be merged
        function_graph.add_node('super_node', category='function')
        coupled_functions = []

        # As long as not all coupled functions are merged into the super node:
        while not nx.is_directed_acyclic_graph(function_graph):
            # Find a cycle
            # Issue: some cycles are only found when the edge orientation is reversed and others only when the
            # orientation is in the original direction
            try:
                cycle = nx.find_cycle(function_graph, orientation='reverse')
            except:
                cycle = nx.find_cycle(function_graph, orientation='original')

            # Find the functions in the cycle
            functions_in_cycle = set()
            functions_in_cycle.update(function_id for edges in cycle for function_id in edges)
            functions_in_cycle = list(functions_in_cycle)

            # Merge the coupled functions in the super node
            for function_id in functions_in_cycle:
                if function_id != 'reverse' and function_id != 'super_node':
                    coupled_functions.append(function_id)
                    function_graph = nx.contracted_nodes(function_graph, 'super_node', function_id)
                    function_graph.remove_edges_from(function_graph.selfloop_edges())

        # Find a topological function order
        function_order = list(nx.topological_sort(function_graph))

        # Get pre-coupling functions and sort
        pre_coupling_functions = function_order[:function_order.index('super_node')]
        pre_coupling_functions_order = self.sort_non_coupled_nodes(pre_coupling_functions)

        # Sort coupled functions to minimize feedback
        coupled_functions_order = self.minimize_feedback(coupled_functions, method, multi_start=multi_start)

        # Get post-coupling functions and sort
        post_coupling_functions = function_order[function_order.index('super_node') + 1:]
        post_coupling_functions_order = self.sort_non_coupled_nodes(post_coupling_functions)

        # Get function_order
        function_order = pre_coupling_functions_order + coupled_functions_order + post_coupling_functions_order

        return function_order

    def sort_non_coupled_nodes(self, nodes):
        """ Function to sort the pre and post coupling nodes

        :param nodes: nodes that need to be sorted
        :type nodes: list
        :return nodes in sorted order
        :rtype list
        """

        # Check if all nodes are in graph and no feedback loops exists
        for func in nodes:
            assert func in self, "Function node {} must be present in graph.".format(func)
        subgraph = self.get_subgraph_by_function_nodes(nodes)
        subgraph = subgraph.get_function_graph()
        assert nx.is_directed_acyclic_graph(subgraph)

        # Make sure the nodes are in a topological sort
        nodes = nx.topological_sort(subgraph)

        nodes_to_sort = list(nodes)
        sorted_nodes = []
        while len(nodes_to_sort) != 0:
            # Get the coupling matrix of the nodes that need to be sorted
            coupling_matrix = self.get_coupling_matrix(node_selection=nodes_to_sort)
            # Find the columns that are zero
            idxs = np.where(~coupling_matrix.any(axis=0))[0]
            # Add sorted node to sorted list, and delete from to be sorted list
            for idx in sorted(idxs, reverse=True):
                sorted_nodes.append(nodes_to_sort[idx])
                del nodes_to_sort[idx]

        return sorted_nodes

    def minimize_feedback(self, nodes, method, multi_start=None):
        """Function to find the function order with minimum feedback

        :param nodes: nodes for which the feedback needs to be minimized
        :type nodes: list
        :param method: algorithm used to find optimal function order
        :type method: str
        :param multi_start: start the algorithm from multiple starting points
        :type multi_start: int
        :return function order
        :rtype list
        """

        # Get random starting points for a multi-start
        if isinstance(multi_start, (int, long)):
            start_points = [[] for _ in range(multi_start)]
            for i in range(multi_start):
                random.shuffle(nodes)
                start_points[i][:] = nodes
            multi_start = start_points

        if multi_start is not None:
            best_order = list(nodes)
            min_feedback = float("inf")
            min_size = float("inf")

            # Start algorithm for each starting point
            for start_point in range(len(multi_start)):
                if method == 'brute-force' or method == 'branch-and-bound':
                    raise IOError('No multi start possible for an exact algorithm')
                elif method == 'single-swap':
                    function_order = self._single_swap(multi_start[start_point])
                elif method == 'two-swap':
                    function_order = self._two_swap(multi_start[start_point])
                elif method == 'hybrid-swap':
                    function_order = self._two_swap(multi_start[start_point])
                    function_order = self._single_swap(function_order)
                else:
                    raise IOError('Selected method (' + method + ') is not a valid method for sequencing, supported ' +
                                  'methods are: brute-force, single-swap, two-swap, hybrid-swap, branch-and-bound')

                # Get feedback info
                feedback, size = self.get_feedback_info(function_order)

                # Remember best order found
                if feedback < min_feedback or (feedback == min_feedback and size < min_size):
                    best_order = list(function_order)
                    min_feedback = feedback
                    min_size = size

            function_order = list(best_order)

        else:
            if method == 'brute-force':
                function_order = self._brute_force(nodes)
            elif method == 'branch-and-bound':
                function_order = self._branch_and_bound(nodes)
            elif method == 'single-swap':
                function_order = self._single_swap(nodes)
            elif method == 'two-swap':
                function_order = self._two_swap(nodes)
            elif method == 'hybrid-swap':
                function_order = self._two_swap(nodes)
                function_order = self._single_swap(function_order)
            else:
                raise IOError('Selected method (' + method + ') is not a valid method for sequencing, supported ' +
                              'methods are: brute-force, single-swap, two-swap, hybrid-swap, branch-and-bound')

        return function_order

    def _brute_force(self, nodes):
        """Function to find the minimum number of feedback loops using the brute-force method: try all possible
        combinations and select the best one

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :return function order
        :rtype list
        """

        # Calculate the number of runs that are needed and give a warning when it exceeds a threshold
        n_runs = np.math.factorial(len(nodes))
        if n_runs > 3e5:
            logger.warning(str(n_runs) + ' tool combinations need to be evaluated for the brute-force method. Be ' +
                           'aware that this can take up a considerable amount of time and resources')

        function_order = list(nodes)
        min_feedback = float("inf")
        min_size = float("inf")

        # Get all possible combinations
        for current_order in itertools.permutations(nodes):
            feedback, size = self.get_feedback_info(current_order)

            # Evaluate whether current solution is better than the one found so far
            if feedback < min_feedback or (feedback == min_feedback and size < min_size):
                min_feedback = feedback
                min_size = size
                function_order = list(current_order)

        return function_order

    def _single_swap(self, nodes):
        """Function to find the minimum number of feedback loops using the single-swap method: improve the solution
         by searching for a better position for each node

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :return function order
        :rtype list
        """

        converged = False

        # Take the input order as start point
        best_order = list(nodes)
        min_feedback, min_size = self.get_feedback_info(nodes)

        while not converged:
            new_iteration = False

            # Move each node until a better solution is found
            for idx in range(len(best_order)):
                node = best_order[idx]

                # Get feedback information for each node placement
                for position in range(len(best_order)):

                    # Skip current solution
                    if idx == len(best_order) - position - 1:
                        continue
                    # Copy current solution
                    new_order = list(best_order)
                    # Delete current node
                    new_order.pop(idx)
                    # Insert node at new position (starting from the back)
                    new_order.insert(len(best_order) - position - 1, node)
                    feedback, size = self.get_feedback_info(new_order)
                    # Check whether new order is an improvement
                    if feedback < min_feedback or (feedback == min_feedback and size < min_size):
                        best_order = list(new_order)
                        min_feedback = feedback
                        min_size = size
                        new_iteration = True

                    # When a better solution is found, the current iteration is stopped and a new iteration is
                    # started with the improved solution as start point
                    if new_iteration:
                        break
                if new_iteration:
                    break

            # When no improvement is found, the algorithm is terminated
            if not new_iteration:
                converged = True

        function_order = list(best_order)

        return function_order

    def _two_swap(self, nodes):
        """Function to find the minimum number of feedback loops using the two-swap method: improve the solution
        by swapping two nodes

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :return function order
        :rtype list
        """

        converged = False

        # Take the input order as start point
        best_order = list(nodes)
        min_feedback, min_size = self.get_feedback_info(best_order)

        while not converged:
            new_iteration = False

            # Swap two nodes until a better solution is found
            for i in range(len(nodes)):
                for j in range(len(nodes) - (i+1)):

                    # Copy current solution
                    neighbor_solution = list(best_order)
                    # Swap two nodes to get a neighbor solution
                    neighbor_solution[i], neighbor_solution[-j-1] = best_order[-j-1], best_order[i]
                    # Get feedback information of the neighbor solution
                    feedback, size = self.get_feedback_info(neighbor_solution)
                    # Check whether the neighbor solution is a better than the current solution
                    if feedback < min_feedback or (feedback == min_feedback and size < min_size):
                        best_order = list(neighbor_solution)
                        min_feedback = feedback
                        min_size = size
                        new_iteration = True

                    # When a better solution is found, the current iteration is stopped and a new iteration is
                    # started with the improved solution as start point
                    if new_iteration:
                        break
                if new_iteration:
                    break

            # When no improvement is found, the algorithm is terminated
            if not new_iteration:
                converged = True

        function_order = best_order

        return function_order

    def _branch_and_bound(self, nodes):
        """Function to find the minimum number of feedback loops using the branch-and-bound method: search the solution
        space in a systematic way to find the exact solution

        :param nodes: nodes that need to be ordered
        :type nodes: list
        :return function order
        :rtype list
        """

        active_branches = []

        # Calculate lower bound for each initial branch
        for node in nodes:
            node = [node]
            lower_bound_feedback, lower_bound_size = self._get_lower_bound_branch_and_bound(node, nodes)
            active_branches.append([node, lower_bound_feedback, lower_bound_size])

        while True:
            # Sort branches starting from low feedback and low size
            sorted_branches = sorted(active_branches, key=lambda x: (x[1], x[2]))
            # Find all branches with the least feedback and size
            best_branches = [sorted_branches[idx][0] for idx in range(len(sorted_branches)) if sorted_branches[idx][1] == sorted_branches[0][1] and sorted_branches[idx][2] == sorted_branches[0][2]]
            # Select the longest branch to further explore
            selected_branch = max(best_branches, key=len)

            # Check whether the branch is a complete solution. If so, the best solution is found and iteration stopped
            if len(selected_branch) == len(nodes):
                break

            # If branch is not a complete solution:
            # Explore branch and add children of selected branch to the list with active nodes
            for node in nodes:
                if node not in selected_branch:
                    node = [node]
                    current_order = selected_branch + node
                    lower_bound_feedback, lower_bound_size = self._get_lower_bound_branch_and_bound(current_order,
                                                                                                    nodes)
                    active_branches.append([current_order, lower_bound_feedback, lower_bound_size])

            # Find index of explored branch in active branches and delete explored branch
            idx_selected_branch = active_branches.index([selected_branch, sorted_branches[0][1], sorted_branches[0][2]])
            del active_branches[idx_selected_branch]

        function_order = selected_branch

        return function_order

    def _get_lower_bound_branch_and_bound(self, branch, nodes):
        """Function to calculate the lower bound of a branch in the branch and bound algorithm.
        The lower bound is defined as the amount of feedback loops that are guaranteed to occur if the
        selected nodes are placed at the beginning of the order

        :param branch: the nodes in the branch
        :type branch: list
        :param nodes: the nodes that are considered in the sequencing problem
        :type nodes: list
        :return lower bound
        :rtype int
        """

        # Get a random function order with the nodes of the branch at the start
        function_order = list(branch)
        for node in nodes:
            if node not in function_order:
                function_order.append(node)

        coupling_matrix = self.get_coupling_matrix(node_selection=function_order)

        # Calculate lower bound for both feedback and size
        feedback = 0
        size = 0
        for idx1 in range(len(nodes)):
            for idx2 in range(len(branch)):
                if idx1 > idx2 and coupling_matrix[idx1, idx2] != 0:
                    feedback += coupling_matrix[idx1][idx2]
                    if idx1 < len(branch):
                        size += (idx1-idx2+1)*coupling_matrix[idx1][idx2]
                    else:
                        size += (len(branch)-idx2+1)*coupling_matrix[idx1][idx2]

        return feedback, size

    def get_feedback_info(self, function_order):
        """Function to determine the number of feedback loops for a given function order

        :param function_order: function order of the nodes
        :type function_order: list
        :return number of feedback loops
        :rtype int
        """

        coupling_matrix = self.get_coupling_matrix(node_selection=function_order)

        # Determine number of feedback loops
        n_feedback_loops = 0
        n_disciplines_in_feedback = 0
        for idx1 in range(coupling_matrix.shape[0]):
            for idx2 in range(coupling_matrix.shape[0]):
                if idx1 > idx2 and coupling_matrix[idx1, idx2] != 0:
                    n_feedback_loops += coupling_matrix[idx1][idx2]
                    n_disciplines_in_feedback += (idx1-idx2+1)*coupling_matrix[idx1][idx2]

        return n_feedback_loops, n_disciplines_in_feedback


class RepositoryConnectivityGraph(DataGraph):

    PATHS_LIMIT = 1e4    # limit check for select_function_combination_from method
    WARNING_LIMIT = 3e6  # limit for _get_path_combinations method

    def __init__(self, *args, **kwargs):
        super(RepositoryConnectivityGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _create_cmdows_problem_def(self):

        # Create problemDefinition
        cmdows_problem_definition = Element('problemDefinition')

        return cmdows_problem_definition

    # noinspection PyPep8Naming
    def create_mathematical_problem(self, n_disciplines, coupling_strength=None, n_global_var=None, n_local_var=None,
                                    n_coupling_var=None, n_local_constraints=None, n_global_constraints=None, B=None,
                                    C=None, D=None, E=None, F=None, G=None, H=None, I=None, J=None, r=None, s=None,
                                    write_problem_to_textfile=False):
        """Function to get a mathematical problem according to the variable complexity problem as described in:
        Zhang D., Song B., Wang P. and He Y. 'Performance Evaluation of MDO Architectures within a Variable
        Complexity Problem', Mathematical Problems in Engineering, 2017.

        :param n_disciplines: Number of disciplines
        :param coupling_strength: percentage of couplings, 0 no couplings, 1 all possible couplings
        :param n_global_var: Number of global design variables
        :param n_local_var: Number of local design variables for each discipline
        :param n_coupling_var: Number of output variables for each discipline
        :param n_local_constraints: Number of local constraints
        :param n_global_constraints: Number of global constraints
        :param B: relation between the coupling variables
        :param C: relation between the global design variables and coupling variables
        :param D: relation between the local design variables and coupling variables
        :param E: relation between the global design variables and local constraints
        :param F: relation between the local design variables and local constraints
        :param G: relation between the coupling variables and local constraints
        :param H: relation between the global design variables and global constraints
        :param I: relation between the local design variables and global constraints
        :param J: relation between the coupling variables and global constraints
        :param r: positive scalars to be used for the local constraints
        :param s: positive scalars to be used for the global constraints
        :param write_problem_to_textfile: option to write generated problem to a textfile
        """

        # Input assertions
        assert not B if coupling_strength else B is not None, 'Either the coupling strength or the B-matrix must be ' \
                                                              'given'

        mathematical_problem = dict()
        mathematical_problem['n_disciplines'] = n_disciplines

        # Create values for the random elements
        # Number of global design variables
        if n_global_var is None:
            n_global_var = random.randint(1, 3)
        mathematical_problem['n_global_var'] = n_global_var

        # Number of local design variables per discipline
        if n_local_var is None:
            n_local_var = [random.randint(1, 3) for _ in range(n_disciplines)]
        mathematical_problem['n_local_var'] = n_local_var

        # Number of coupling variables per discipline
        if n_coupling_var is None:
            n_coupling_var = [random.randint(1, 5) for _ in range(n_disciplines)]
        mathematical_problem['n_coupling_var'] = n_coupling_var

        # Number of local constraints
        if n_local_constraints is None:
            n_local_constraints = [random.randint(1, 5) for _ in range(n_disciplines)]
        mathematical_problem['n_local_constraints'] = n_local_constraints

        # Number of global constraints
        if n_global_constraints is None:
            n_global_constraints = random.randint(1, 3)
        mathematical_problem['n_global_constraints'] = n_global_constraints

        # Create B-matrix: relation between the coupling variables
        if B is None:
            while True:
                # Initiate matrix
                B = np.zeros((sum(n_coupling_var), sum(n_coupling_var)))

                # Calculate the number of couplings based on the coupling strength
                n_couplings = int(np.ceil(((sum(n_coupling_var)*n_disciplines) - sum(n_coupling_var)) *
                                          coupling_strength))

                # Get a list with all possible couplings between variables and disciplines
                possible_couplings = []
                for discipline in range(n_disciplines):
                    for coupling_var in range(sum(n_coupling_var)):
                        # An output variable of a discipline cannot be an input to the same discipline
                        if sum(n_coupling_var[:discipline]) <= coupling_var < sum(n_coupling_var[:discipline + 1]):
                            continue
                        possible_couplings.append([coupling_var, discipline])

                # Choose random couplings from all possible couplings
                couplings = random.sample(range(len(possible_couplings)), n_couplings)

                # Fill the B-matrix with the chosen couplings
                for coupling in couplings:
                    discipline = possible_couplings[coupling][1]
                    for variable in range(n_coupling_var[discipline]):
                        B[sum(n_coupling_var[:discipline]) + variable][possible_couplings[coupling][0]] = random.choice(
                            range(-5, 0)+range(1, 6))  # Zero is not allowed

                # To ensure convergence the B-matrix must be diagonally dominant
                B_diag = np.sum(np.abs(B), axis=1)
                B_diag = [entry + random.randint(1, 10) for entry in B_diag]
                i, j = np.indices(B.shape)
                B[i == j] = B_diag

                # Test if the matrix is singular by calculating its rank
                rank = np.linalg.matrix_rank(B)
                singular = True if rank < min(B.shape) else False
                if not singular:
                    break
                print 'B matrix is singular, new matrix is generated...'

        else:
            # Test if B matrix is singular by calculating its rank
            rank = np.linalg.matrix_rank(B)
            singular = True if rank < min(B.shape) else False
            assert not singular, 'B matrix is singular'

        mathematical_problem['B-matrix'] = B

        # Create C-matrix: relation between global design variables and coupling variables
        if C is None:
            C = np.array([[float(random.randint(-5, 5)) for _ in range(n_global_var)] for _ in
                          range(sum(n_coupling_var))])
        mathematical_problem['C-matrix'] = C

        # Create D-matrix: relation between local design variables and coupling variables
        if D is None:
            D = np.zeros((sum(n_coupling_var), sum(n_local_var)))
            for discipline in range(n_disciplines):
                for local_var in range(n_local_var[discipline]):
                    for coupling_var in range(n_coupling_var[discipline]):
                        D[sum(n_coupling_var[:discipline]) + coupling_var][sum(n_local_var[:discipline]) + local_var] =\
                            random.choice(range(-5, 0)+range(1, 6))  # Zero is not allowed
        mathematical_problem['D-matrix'] = D

        # Create E-matrix: relation between global design variables and local constraints
        if E is None:
            E = np.array([[float(random.randint(-5, 5)) for _ in range(n_global_var)] for _ in
                          range(sum(n_local_constraints))])
        mathematical_problem['E-matrix'] = E

        # Create F-matrix: relation between local design variables and local constraints
        if F is None:
            F = np.zeros((sum(n_local_constraints), sum(n_local_var)))
            for discipline in range(n_disciplines):
                for local_var in range(n_local_var[discipline]):
                    for local_constraint in range(n_local_constraints[discipline]):
                        F[sum(n_local_constraints[:discipline]) +
                          local_constraint][sum(n_local_var[:discipline]) + local_var] = random.randint(-5, 5)
        mathematical_problem['F-matrix'] = F

        # Create G-matrix: relation between coupling variables and local constraints
        if G is None:
            G = np.zeros((sum(n_local_constraints), sum(n_coupling_var)))
            for discipline in range(n_disciplines):
                for coupling_var in range(n_coupling_var[discipline]):
                    for local_constraint in range(n_local_constraints[discipline]):
                        G[sum(n_local_constraints[:discipline]) +
                          local_constraint][sum(n_coupling_var[:discipline]) + coupling_var] = \
                            random.choice(range(-5, 0)+range(1, 6))  # Zero is not allowed
        mathematical_problem['G-matrix'] = G

        # Create r-matrix: positive scalars used to calculate local constraint values
        if r is None:
            r = [float(random.randint(1, 5)) for _ in range(sum(n_local_constraints))]
        mathematical_problem['r-matrix'] = r

        # Create H-matrix: relation between global design variables and global constraints
        if H is None:
            H = np.array([[float(random.randint(-5, 5)) for _ in range(n_global_var)] for _ in
                          range(n_global_constraints)])
        mathematical_problem['H-matrix'] = H

        # Create I-matrix: relation between local design variables and global constraints
        if I is None:
            I = np.array([[float(random.randint(-5, 5)) for _ in range(sum(n_local_var))] for _ in
                          range(n_global_constraints)])
        mathematical_problem['I-matrix'] = I

        # Create J-matrix: relation between coupling variables and global constraints
        if J is None:
            J = np.array([[float(random.randint(-5, 5)) for _ in range(sum(n_coupling_var))] for _ in
                          range(n_global_constraints)])
        mathematical_problem['J-matrix'] = J

        # Create s-matrix: positive scalars used to calculate global constraint values
        if s is None:
            s = [float(random.randint(1, 5)) for _ in range(n_global_constraints)]
        mathematical_problem['s-matrix'] = s

        # Check whether problem is well-formulated
        # Check whether all coupling variables are defined
        for coupling_var in range(sum(n_coupling_var)):
            assert B[coupling_var][coupling_var] != 0, 'Diagonal of B cannot be zero'

        # Check whether output variable is not also an input variable to the same discipline
        for discipline in range(n_disciplines):
            for coupling_var in range(n_coupling_var[discipline]):
                values = B[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                           sum(n_coupling_var[:discipline]) + coupling_var]
                for index, v in enumerate(values):
                    if index != coupling_var:
                        assert v == 0, 'Output variable y{0}_{1} cannot be an input to discipline ' \
                                       'D{0}'.format(discipline + 1, coupling_var + 1)

        # Check whether local variables are not used by other disciplines
        for local_var_disc in range(n_disciplines):
            for local_var in range(n_local_var[local_var_disc]):
                for discipline in range(n_disciplines):
                    if local_var_disc != discipline:
                        values = D[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                                   sum(n_local_var[:local_var_disc]) + local_var]
                        assert all(
                            v == 0 for v in values), 'Local variable x{0}_{1} cannot be an input to discipline ' \
                                                     'D{2}, only to discipline D{0}'.format(local_var_disc + 1,
                                                                                            local_var + 1,
                                                                                            discipline + 1)
                for local_con_disc in range(n_disciplines):
                    for local_constraint in range(n_local_constraints[local_con_disc]):
                        if local_var_disc != local_con_disc:
                            assert F[sum(n_local_constraints[:local_con_disc]) + local_constraint,
                                     sum(n_local_var[:local_var_disc]) + local_var] == 0, \
                                'Local variable x{0}_{1} cannot be an input to local constraint ' \
                                'g{2}_{3}'.format(local_var_disc + 1, local_var + 1, local_con_disc + 1,
                                                  local_constraint + 1)

        # Check whether coupling variables are not used for different local constraints
        for coupling_var_disc in range(n_disciplines):
            for coupling_var in range(n_coupling_var[coupling_var_disc]):
                for local_con_disc in range(n_disciplines):
                    for local_constraint in range(n_local_constraints[local_con_disc]):
                        if coupling_var_disc != local_con_disc:
                            assert G[sum(n_local_constraints[:local_con_disc]) + local_constraint,
                                     sum(n_coupling_var[:coupling_var_disc]) + coupling_var] == 0, \
                                'Coupling variable y{0}_{1} cannot be an input to local constraint ' \
                                'g{2}_{3}'.format(coupling_var_disc + 1, coupling_var + 1, local_con_disc + 1,
                                                  local_constraint + 1)

        # All function nodes are defined
        for discipline in range(n_disciplines):  # Disciplines
            self.add_node('D{0}'.format(discipline + 1), category='function')
            for local_constraint in range(n_local_constraints[discipline]):  # Local constraints
                self.add_node('G{0}_{1}'.format(discipline+1, local_constraint+1), category='function')
        self.add_node('F', category='function')  # Objective
        for constraint in range(n_global_constraints):  # Global constraints
            self.add_node('G0{0}'.format(constraint + 1), category='function')

        # All variable nodes are defined
        for global_var in range(n_global_var):  # Global design variables
            self.add_node('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                          category='variable',
                          label='x0{0}'.format(global_var + 1))
        for constraint in range(n_global_constraints):  # Global constraints
            self.add_node('/data_schema/global_constraints/g0{0}'.format(constraint + 1),
                          category='variable',
                          label='g0{0}'.format(constraint + 1))
        self.add_node('/data_schema/objective/f',  # Objective
                      category='variable',
                      label='f')
        for discipline in range(n_disciplines):
            for local_var in range(n_local_var[discipline]):  # Local design variables
                self.add_node('/data_schema/local_design_variables/x{0}_{1}'.format(discipline + 1, local_var + 1),
                              category='variable',
                              label='x{0}_{1}'.format(discipline + 1, local_var + 1))
            for coupling_var in range(n_coupling_var[discipline]):  # Coupling variables
                self.add_node('/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, coupling_var + 1),
                              category='variable',
                              label='y{0}_{1}'.format(discipline + 1, coupling_var + 1))
            for local_constraint in range(n_local_constraints[discipline]):  # Local constraints
                self.add_node('/data_schema/local_constraints/g{0}_{1}'.format(discipline+1, local_constraint+1),
                              category='variable',
                              label='g{0}_{1}'.format(discipline+1, local_constraint+1))

        # Edges between global variables and function nodes are defined
        for global_var in range(n_global_var):
            for discipline in range(n_disciplines):
                values = C[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]), global_var]
                if not all(v == 0 for v in values):
                    self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                                  'D{0}'.format(discipline + 1))
                for local_constraint in range(n_local_constraints[discipline]):
                    self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                                  'G{0}_{1}'.format(discipline + 1, local_constraint + 1))
            self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1), 'F')
            for constraint in range(n_global_constraints):
                self.add_edge('/data_schema/global_design_variables/x0{0}'.format(global_var + 1),
                              'G0{0}'.format(constraint + 1))

        # Edges between local variables and function nodes are defined
        for local_var_disc in range(n_disciplines):
            for local_var in range(n_local_var[local_var_disc]):
                for discipline in range(n_disciplines):
                    values = D[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                               sum(n_local_var[:local_var_disc]) + local_var]
                    if not all(v == 0 for v in values):
                        self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1,
                                      local_var + 1), 'D{0}'.format(local_var_disc + 1))
                for local_constraint in range(n_local_constraints[local_var_disc]):
                    self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1,
                                                                                        local_var + 1),
                                  'G{0}_{1}'.format(local_var_disc + 1, local_constraint + 1))
                self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1, local_var + 1),
                              'F')
                for constraint in range(n_global_constraints):
                    self.add_edge('/data_schema/local_design_variables/x{0}_{1}'.format(local_var_disc + 1,
                                  local_var + 1), 'G0{0}'.format(constraint + 1))

        # Edges between coupling variables and function nodes are defined
        for coupling_var_disc in range(n_disciplines):
            for coupling_var in range(n_coupling_var[coupling_var_disc]):
                for discipline in range(n_disciplines):
                    values = B[sum(n_coupling_var[:discipline]):sum(n_coupling_var[:discipline + 1]),
                               sum(n_coupling_var[:coupling_var_disc]) + coupling_var]
                    if not discipline == coupling_var_disc and not all(v == 0 for v in values):
                        self.add_edge(
                            '/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1, coupling_var + 1),
                            'D{0}'.format(discipline + 1))
                    for local_constraint in range(n_local_constraints[discipline]):
                        value = G[sum(n_local_constraints[:discipline]) + local_constraint,
                                  sum(n_coupling_var[:coupling_var_disc]) + coupling_var]
                        if value != 0:
                            self.add_edge('/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1,
                                                                                            coupling_var + 1),
                                          'G{0}_{1}'.format(discipline + 1, local_constraint + 1))
                self.add_edge('/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1, coupling_var +
                                                                                1), 'F')
                for constraint in range(n_global_constraints):
                    if J[constraint][sum(n_coupling_var[:coupling_var_disc]) + coupling_var] != 0:
                        self.add_edge(
                            '/data_schema/coupling_variables/y{0}_{1}'.format(coupling_var_disc + 1, coupling_var + 1),
                            'G0{0}'.format(constraint + 1))

        # Edges between function nodes and coupling variables are defined
        for discipline in range(n_disciplines):
            for coupling_var in range(n_coupling_var[discipline]):  # Disciplines
                self.add_edge('D{0}'.format(discipline + 1),
                              '/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, coupling_var + 1))
            for local_constraint in range(n_local_constraints[discipline]):  # Local constraints
                self.add_edge('G{0}_{1}'.format(discipline + 1, local_constraint + 1),
                              '/data_schema/local_constraints/g{0}_{1}'.format(discipline + 1, local_constraint + 1))
        self.add_edge('F', '/data_schema/objective/f')  # Objective
        for constraint in range(n_global_constraints):  # Global constraints
            self.add_edge('G0{0}'.format(constraint + 1), '/data_schema/global_constraints/g0{0}'.format(constraint +
                                                                                                         1))

        # Add equations
        self.add_equation_labels(self.get_function_nodes(), labeling_method='node_id')

        # Add discipline analysis equations
        for discipline in range(n_disciplines):
            for output_var in range(n_coupling_var[discipline]):
                equation = ""
                for global_var in range(n_global_var):
                    if C[sum(n_coupling_var[:discipline]) + output_var][global_var] != 0:
                        equation += '-{0}*x0{1}'.format(C[sum(n_coupling_var[:discipline]) + output_var][global_var],
                                                        global_var + 1)
                for local_var_disc in range(n_disciplines):
                    for local_var in range(n_local_var[local_var_disc]):
                        if D[sum(n_coupling_var[:discipline]) + output_var][
                                    sum(n_local_var[:local_var_disc]) + local_var] != 0:
                            equation += '-{0}*x{1}_{2}'.format(D[sum(n_coupling_var[:discipline]) + output_var][
                                                                sum(n_local_var[:local_var_disc]) + local_var],
                                                               local_var_disc + 1, local_var + 1)
                for coupling_var_disc in range(n_disciplines):
                    for coupling_var in range(n_coupling_var[coupling_var_disc]):
                        if B[sum(n_coupling_var[:discipline]) + output_var][sum(n_coupling_var[:coupling_var_disc]) +
                           coupling_var] != 0 and (discipline, output_var) != (coupling_var_disc, coupling_var):
                            equation += '-{0}*y{1}_{2}'.format(B[sum(n_coupling_var[:discipline]) + output_var][sum(
                                n_coupling_var[:coupling_var_disc]) + coupling_var], coupling_var_disc + 1,
                                                              coupling_var + 1)
                if B[sum(n_coupling_var[:discipline]) + output_var][sum(n_coupling_var[:discipline]) + output_var] != 1:
                    equation = '({0})/{1}'.format(equation, B[sum(n_coupling_var[:discipline]) + output_var][
                        sum(n_coupling_var[:discipline]) + output_var])
                self.add_equation(['D{0}'.format(discipline + 1),
                                  '/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, output_var + 1)],
                                  equation, 'Python')
                self.add_equation(['D{0}'.format(discipline + 1),
                                  '/data_schema/coupling_variables/y{0}_{1}'.format(discipline + 1, output_var + 1)],
                                  equation, 'LaTeX')

        # Add objective function equation
        objective = ""
        for global_var in range(n_global_var):
            objective += '+x0{0}'.format(global_var + 1)
        for discipline in range(n_disciplines):
            for local_var in range(n_local_var[discipline]):
                objective += '+x{0}_{1}'.format(discipline + 1, local_var + 1)
        for discipline in range(n_disciplines):
            for coupling_var in range(n_coupling_var[discipline]):
                objective += '+y{0}_{1}'.format(discipline + 1, coupling_var + 1)
        self.add_equation('F', '({0})**3'.format(objective), 'Python')
        self.add_equation('F', '({0})^3'.format(objective), 'LaTeX')

        # Add global constraint function equations
        for constraint in range(n_global_constraints):
            constraint_eq = ""
            for global_var in range(n_global_var):
                constraint_eq += '+x0{0}*x0{0}'.format(global_var + 1)
                if H[constraint][global_var] != 0:
                    constraint_eq += '+{0}*x0{1}'.format(H[constraint][global_var], global_var + 1)
            for discipline in range(n_disciplines):
                for local_var in range(n_local_var[discipline]):
                    constraint_eq += '+x{0}_{1}*x{0}_{1}'.format(discipline + 1, local_var + 1)
                    if I[constraint][sum(n_local_var[:discipline]) + local_var] != 0:
                        constraint_eq += '+{0}*x{1}_{2}'.format(I[constraint][sum(n_local_var[:discipline]) +
                                                                              local_var], discipline + 1, local_var + 1)
            for discipline in range(n_disciplines):
                for coupling_var in range(n_coupling_var[discipline]):
                    if J[constraint][sum(n_coupling_var[:discipline]) + coupling_var] != 0:
                        constraint_eq += '+{0}*y{1}_{2}'.format(
                            J[constraint][sum(n_coupling_var[:discipline]) + coupling_var], discipline + 1,
                            coupling_var + 1)
            constraint_eq += '-{0}'.format(s[constraint])
            self.add_equation('G0{0}'.format(constraint + 1), constraint_eq, 'Python')
            self.add_equation('G0{0}'.format(constraint + 1), constraint_eq, 'LaTeX')

        # Add local constraint function equations
        for local_con_disc in range(n_disciplines):
            for local_constraint in range(n_local_constraints[local_con_disc]):
                constraint_eq = ""
                for global_var in range(n_global_var):
                    constraint_eq += '+x0{0}*x0{0}'.format(global_var + 1)
                    if E[sum(n_local_constraints[:local_con_disc]) + local_constraint, global_var] != 0:
                        constraint_eq += '+{0}*x0{1}'.format(E[sum(n_local_constraints[:local_con_disc]) +
                                                               local_constraint][global_var], global_var + 1)
                for local_var in range(n_local_var[local_con_disc]):
                    constraint_eq += '+x{0}_{1}*x{0}_{1}'.format(local_con_disc + 1, local_var + 1)
                    if F[sum(n_local_constraints[:local_con_disc]) + local_constraint][
                                sum(n_local_var[:local_con_disc]) + local_var] != 0:
                        constraint_eq += '+{0}*x{1}_{2}'.format(
                            F[sum(n_local_constraints[:local_con_disc]) + local_constraint][
                                sum(n_local_var[:local_con_disc]) + local_var], local_con_disc + 1, local_var + 1)
                for discipline in range(n_disciplines):
                    for coupling_var in range(n_coupling_var[discipline]):
                        if G[sum(n_local_constraints[:local_con_disc]) + local_constraint][
                                    sum(n_coupling_var[:discipline]) + coupling_var] != 0:
                            constraint_eq += '+{0}*y{1}_{2}'.format(G[sum(n_local_constraints[:local_con_disc]) +
                                                                      local_constraint][sum(n_coupling_var[:discipline])
                                                                                        + coupling_var], discipline + 1,
                                                                    coupling_var + 1)
                constraint_eq += '-{}'.format(r[sum(n_local_constraints[:local_con_disc]) + local_constraint])
                self.add_equation('G{0}_{1}'.format(local_con_disc + 1, local_constraint + 1), constraint_eq, 'Python')
                self.add_equation('G{0}_{1}'.format(local_con_disc + 1, local_constraint + 1), constraint_eq, 'LaTeX')
                print 'local constraint', local_con_disc + 1, local_constraint + 1
                print 'equation', constraint_eq

        # Get function order
        function_order = []
        for discipline in range(n_disciplines):
            function_order += ['D{0}'.format(discipline + 1)]
        for discipline in range(n_disciplines):
            for local_constraint in range(n_local_constraints[discipline]):
                function_order += ['G{0}_{1}'.format(discipline + 1, local_constraint + 1)]
        for constraint in range(n_global_constraints):
            function_order += ['G0{0}'.format(constraint + 1)]
        function_order += ['F']
        mathematical_problem['function_order'] = function_order

        # Write problem to text file
        if write_problem_to_textfile:
            f = open("Problem_formulation.txt", "w")
            f.write('Number of disciplines: ' + str(n_disciplines) + '\n')
            f.write('Number of global variables: ' + str(n_global_var) + '\n')
            f.write('Number of local variables: ' + str(n_local_var) + '\n')
            f.write('Number of coupling variables: ' + str(n_coupling_var) + '\n')
            f.write('Number of global constraints: ' + str(n_global_constraints) + '\n')
            f.write('B-matrix: ' + str(B) + '\n')
            f.write('C-matrix: ' + str(C) + '\n')
            f.write('D-matrix: ' + str(D) + '\n')
            f.write('H-matrix: ' + str(H) + '\n')
            f.write('I-matrix: ' + str(I) + '\n')
            f.write('J-matrix: ' + str(J) + '\n')
            f.write('s-matrix: ' + str(s) + '\n')
            f.close()

        return mathematical_problem

    # -----------------------------------------------------------------------------------------------------------------#
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # -----------------------------------------------------------------------------------------------------------------#

    def get_function_paths_by_objective(self, *args, **kwargs):
        """This function takes an arbitrary amount of objective nodes as graph sinks and returns all path combinations
        of tools.

        If no arguments are given, user is prompted to select objectives from the graph.

        The tool combinations are found using the function itertools.product() and can lead to significant computation
        times for large graphs. If this is the case, the user is prompted whether to continue or not.

        A variety of filters can be applied to the search of possible tools combinations, some of which reduce the
        computation time.

        kwargs:
        obj_vars_covered - ensures that all objective variables are used in tool configurations
        ignore_funcs - ignores functions for the config
        source - source node; if provided, must be in config

        :param args: arbitrary amount of objective nodes
        :param kwargs: filter options to limit possible path combinations
        :return: all possible FPG path combinations for the provided objective nodes
        """

        # TODO: Add filters
        # Filters:
        # include_functions - returned path combinations must include the indicated functions
        # exclude_functions - returned path combinations must exclude the indicated functions
        # min_funcs - only returns paths that have a minimum amount if functions
        # max_funcs - only returns paths that have a maximum amount of functions
        # obj_vars_covered - only returns paths where ALL objective variables are covered

        # make copy of self
        graph = copy.deepcopy(self)

        # get and check keyword arguments
        obj_vars_covered = kwargs.get('objective_variables_covered', False)  # TODO: Implement this option
        assert isinstance(obj_vars_covered, bool)

        ignore_funcs = None
        if "ignore_funcs" in kwargs:
            ignore_funcs = kwargs["ignore_funcs"]
            for func in ignore_funcs:
                assert func in self, "Function node {} must be present in graph.".format(func)

        # source = None
        # if "source" in kwargs:
        #    source = kwargs["source"]
        #    assert graph.node_is_function(source), "Source node must be a function."

        min_funcs = None
        if "min_funcs" in kwargs:
            min_funcs = kwargs["min_funcs"]
            assert isinstance(min_funcs, int)

        max_funcs = float("inf")
        if "max_funcs" in kwargs:
            max_funcs = kwargs["max_funcs"]
            assert isinstance(max_funcs, int)

        # get all function nodes in graph
        # func_nodes = graph.get_function_nodes()

        # [step 1] check if function nodes provided
        if args:
            objs = list(args)
            for arg in objs:
                assert graph.node_is_function(arg), "Provided Objective must be function."

        else:  # if not provided, ask user to select
            objs = graph.select_objectives_from_graph()

        # intermediate check that OBJ function node given
        assert objs, "No valid Objective Functions provided."
        logger.info('Function configurations are considered for objective(s): [{}]'.format(
            ', '.join(str(x) for x in objs)))

        # [Step 2]: Get OBJ function variables in graph
        obj_variables = []
        for objFunc in objs:
            for u, v in graph.in_edges(objFunc):
                obj_variables.append(u)

        # [Step 3]: Get function graph (remove all variable nodes and replace them with corresponding edges)
        if obj_vars_covered:
            # if obj_vars_covered, objective vars will be present in paths; easy to check their presence
            function_graph = graph.get_function_graph(keep_objective_variables=True)
        else:
            function_graph = graph.get_function_graph()

        # [Step 4]: get all (simple) paths to sinks
        all_simple_paths = set()  # making sure that no duplicate paths in list
        for sink in objs:
            anc_nodes = nx.ancestors(function_graph, sink)
            for anc in anc_nodes:
                if function_graph.node_is_function(anc):  # do not take objVars into account

                    # add every path to sink as frozenset
                    for path in nx.all_simple_paths(function_graph, anc, sink):  # TODO: Test for multiple sinks!
                        all_simple_paths.add(frozenset(path))

        # [Step 5]: Apply (some) filters
        # TODO: Apply some filters here

        # [Step 6]: group paths according into subsets
        path_subsets = self._group_elements_by_subset(*all_simple_paths)

        # [Step 7]: Get all combinations between all feedback tool combinations
        subsets_list = [subset for _, subset in path_subsets.iteritems()]

        # remove all paths that have ignore-functions
        if ignore_funcs:
            for subset in subsets_list:
                remove = []
                for path in subset:
                    if not ignore_funcs.isdisjoint(path):
                        remove.append(path)
                for p in remove:
                    subset.remove(p)

        all_fpg_paths = function_graph.get_path_combinations(*subsets_list, min_funcs=min_funcs, max_funcs=max_funcs)

        return all_fpg_paths

    def get_path_combinations(self, *args, **kwargs):
        """This function takes lists of subsets and generates all possible combinations between them.

        This is done by using the itertools.product() function. If the amount of expected evaluations exceeds a pre-set
        minimum, the user will be asked if to continue or not; because the process can take a long time and use up many
        resources.

        Optional arguments:
        min_func: minimum amount of functions in each configuration
        max_func: maximum amount of functions in each configuration

        :param args: lists of subsets that will be used to find configurations
        :type args: list
        :return: set of all unique path combinations
        """

        # get list of subsets
        subsets = list(args)

        # kwargs check
        # min_funcs = None
        # if "min_funcs" in kwargs:
        #     min_funcs = kwargs["min_funcs"]
        #     assert isinstance(min_funcs, int)

        max_funcs = kwargs.get('max_funcs', float("inf"))

        # append empty string to each list (to get ALL combinations; check itertools.product()) and count evaluations
        count = 1
        for subset in subsets:
            subset.append('')
            count *= len(subset)
        count -= 1

        # If many combinations are evaluated, warn user and ask if to continue
        if count > self.WARNING_LIMIT:
            logger.warning('Only ' + str(self.WARNING_LIMIT) + ' tool combinations can be evaluated with the current ' +
                           ' settings. However, ' + str(count) + ' evaluations are now selected. You can decrease ' +
                           'this number by applying filters. You could also increase the WARNING_LIMIT but be aware ' +
                           'that the process can take a considerable amount of time and resources then.')
            return list()

        # get all tool combinations using subsets
        all_path_combinations = set()

        for comb in itertools.product(*subsets):
            # combine separate lists into one for each combo
            # clean_comb = frozenset(itertools.chain.from_iterable(comb))
            clean_comb = frozenset().union(*comb)
            if len(clean_comb) > max_funcs or len(clean_comb) > max_funcs:
                continue
            # add to list if combo is not empty and does not yet exist in list
            if clean_comb and clean_comb not in all_path_combinations:
                all_path_combinations.add(clean_comb)

        return all_path_combinations

    def _get_feedback_paths(self, path, functions_only=True):
        # TODO: Add docstring

        # functions_only only passes on argument, not used in this function
        assert isinstance(functions_only, bool)

        # get feedback nodes if exist in path
        # empty strings in tpls are necessary for proper functioning
        feedback = self._get_feedback_nodes(path, functions_only=functions_only)

        # get path combinations in case feedback loops exist in path
        feedback_combis = []
        for prod in itertools.product([tuple(path)], *feedback):
            # remove all empty products
            removed_empty = (x for x in prod if x)  # remove empty strings
            # remove brackets created by product; create frozenset to make object immutable
            removed_brackets = frozenset(itertools.chain.from_iterable(removed_empty))

            # if combination is not empty and does not already exist in list, add to list
            if removed_brackets not in feedback_combis and removed_brackets:
                feedback_combis.append(removed_brackets)

        return feedback_combis

    def _get_feedback_nodes(self, main_path, functions_only=True):
        # TODO: Add docstring

        assert isinstance(functions_only, bool)
        feed_back = []  # contains feed_back nodes; each feed_back loop is in a separate list

        for main_path_idx, main_path_node in enumerate(main_path):
            search_loop = []
            start_index = -1

            if functions_only:
                if not self.node_is_function(main_path_node):
                    continue

            # iterate through edges recursively and add feed_back loops if they exist
            self._iter_out_edges(main_path_idx, main_path, main_path_node, start_index, search_loop, feed_back,
                                 functions_only)

        return feed_back

    def _iter_out_edges(self, main_path_idx, main_path, node, search_index, search_loop, feed_back,
                        functions_only=True):
        # TODO: Add docstring

        search_index += 1

        for edge in self.out_edges(node):
            if functions_only:
                if not self.node_is_function(edge[1]):
                    continue
            if edge[1] in search_loop:
                continue
            search_loop.insert(search_index, edge[1])
            if edge[1] in main_path and main_path.index(edge[1]) <= main_path_idx:
                feed_back.append(("", search_loop[:search_index]))
            elif edge[1] not in main_path:
                self._iter_out_edges(main_path_idx, main_path, edge[1], search_index, search_loop, feed_back,
                                     functions_only)

        return

    # noinspection PyMethodMayBeStatic
    def _group_elements_by_subset(self, *args):
        """This function takes arguments of type set/frozenset and groups them by subset.

        All elements that are subsets of another element are grouped together and returned in a dict with the longest
        superset as keywords.

        Example:
        >> list = [set([1]),set([1,2]),set([3]),set([0,1,2])]
        >> sub_sets = graph._group_elements_by_subset(*list)
        >> sub_sets
        >> {set([0,1,2]): [set([1]), set([1,2]),set([0,1,2])], set([3]):[set([3])]}

        :param args: arbitrary argument
        :type args: set, frozenset
        :return: dict with grouped arguments by longest subset in group
        :rtype: dict
        """

        for arg in args:
            assert isinstance(arg, (set, frozenset))
        set_list = list(args)

        sub_sets = {}
        skip = []
        for i, path in enumerate(set_list):
            if path in skip:
                continue

            set_found = False
            for comp in set_list[i + 1:]:
                if comp in skip:
                    continue

                if path == comp:
                    skip.append(comp)
                    continue

                if path.issubset(comp):
                    set_found = True

                    if comp not in sub_sets:
                        sub_sets[comp] = [comp]

                    if path in sub_sets:
                        sub_sets[comp] += sub_sets[path]
                        sub_sets.pop(path, None)
                    else:
                        sub_sets[comp].append(path)

                    skip.append(path)
                    break

                elif path.issuperset(comp):
                    set_found = True
                    skip.append(comp)

                    if path not in sub_sets:
                        sub_sets[path] = [path]
                    sub_sets[path].append(comp)

                    if comp in sub_sets:
                        sub_sets[path] += sub_sets[comp]
                        sub_sets.pop(comp, None)
                    continue

            if not set_found and path not in sub_sets:
                sub_sets[path] = []
                sub_sets[path].append(path)

        return sub_sets

    def select_function_combination_from(self, *args, **kwargs):
        """This function takes all provided workflow configurations and lists them according to their characteristics.

        The user can then choose the workflow configuration from the list.
        A warning is given to the user if the amount of total configurations exceeds n = 1e4.
        Print limit is set to [0-20] by default.
        sort_by must be one of ["couplings", "system_inputs", "edges", "nodes"].
        """

        # make sure arguments provided
        assert args, "At least one argument must be provided."

        # check number of arguments; prompt user to continue or not
        if len(args) > self.PATHS_LIMIT:
            msg = "More than {} workflow configurations provided; this could take a lot of time to analyze. Continue?"
            usr_sel = prompting.user_prompt_yes_no(message=msg)
            if not usr_sel:
                print "Combination selection cancelled."
                return

        # check if all arguments are non-string iterables (list, tuple, set, frozenset,...)
        assert all([hasattr(arg, '__iter__') for arg in args]), "All arguments must be non-string iterables."

        # check KWARGS HERE
        print_combos = True
        if "print_combos" in kwargs:
            print_combos = kwargs["print_combos"]
            assert isinstance(print_combos, bool)

        # if no limit given, limit for displaying combos is set to 10
        n_limit = 21
        if "n_limit" in kwargs:
            n_limit = kwargs["n_limit"]
            assert isinstance(n_limit, int)
            assert n_limit > 0, "Argument must be positive."

        # if no sort_by argument given, it sorts combos by "holes"
        sort_by = "functions"
        if "sort_by" in kwargs:
            sort_by = kwargs["sort_by"]
            assert isinstance(sort_by, basestring)
            assert sort_by in self.GRAPH_PROPERTIES, "Argument must be in self.GRAPH_PROPERTIES."

        sort_by_ascending = False
        if "sort_by_ascending" in kwargs:
            sort_by_ascending = kwargs["sort_by_ascending"]
            assert isinstance(sort_by_ascending, bool)

        plot_combos = True
        if "plot_combos" in kwargs:
            plot_combos = kwargs["plot_combos"]
            # TODO: Add assert for type of plot, plot variables etc

        # ------------------------------------------------------------- #

        # iterate through arguments and analyze their graphs
        graph_analysis = {}
        for arg in args:
            # TODO: Implement an option to get graph data from a db instead of analyzing each subgraph (if available)
            # TODO: This saves time in large graphs!

            # initiate dict to save subgraph data to
            graph_analysis[arg] = {}

            # get subgraph in order to get fast analysis
            sub_graph = self.get_subgraph_by_function_nodes(*arg)

            # subgraph analysis
            graph_analysis[arg] = sub_graph.get_graph_properties()

        # sort configuration list
        combo_list = list(graph_analysis.items())
        sorted_combos = sorted(combo_list, key=lambda x: x[1][sort_by], reverse=not sort_by_ascending)

        if plot_combos:

            # plot
            plt_x, plt_y, annotes = [], [], []
            for k, v in graph_analysis.iteritems():
                plt_y.append(v["system_inputs"])
                plt_x.append(v["functions"])
                annotes.append(str(list(k)))

            # TODO: Automate the plotting of graphs (data, labels, etc)!
            fig, ax = plt.subplots()
            ax.scatter(plt_x, plt_y)
            af = AnnoteFinder(plt_x, plt_y, annotes, ax=ax)
            fig.canvas.mpl_connect('button_press_event', af)
            plt.xlabel('Tools')
            plt.ylabel('System Inputs')
            plt.show()

        # print configs
        if print_combos:
            print_list = []
            for combo, properties in sorted_combos:
                prop_list = [properties[prop] for prop in self.GRAPH_PROPERTIES]
                prop_list.append(list(combo))
                print_list.append(prop_list)

            hdr = self.GRAPH_PROPERTIES + ["Configuration"]
            msg = "The following tool configurations were found in the graph:"
            printing.print_in_table(print_list[:n_limit], message=msg, headers=hdr, print_indeces=True)

        # select combo for FPG
        # TODO: finish!
        # sel_mssg = "Please select a tool combination from the list above:"
        sel_list = [sorted_combo[0] for sorted_combo in sorted_combos[:n_limit]]
        # user_sel= PRO.user_prompt_select_options(*sel_list, message=sel_mssg, allow_multi=False, allow_empty=False)
        user_sel = [sel_list[0]]

        return next(iter(user_sel))

    def get_fpg_by_function_nodes(self, *args):
        """This function creates a new (FPG)-graph based on the selected function nodes.

        :return: new fpg graph
        :rtype: FundamentalProblemGraph
        """

        # TODO: Assert that nodes are function nodes

        # get subgraph from function nodes
        sub_graph = self.get_subgraph_by_function_nodes(*args)

        # create FPG from sub-graph
        fpg = nx.compose(FundamentalProblemGraph(), sub_graph)
        # TODO: Make sure that the name of the graph is changed!

        return fpg

    def get_fpg_based_on_sinks(self, list_of_sinks, name='FPG'):
        """Function to get the a Fundamental Problem Graph based on a list of sinks/required output variables.

        :param list_of_sinks: list with strings that specify the desired output
        :type list_of_sinks: list
        :param name: name of the graph to be generated
        :type name: str
        :return: Fundamental Problem Graph object
        :rtype: FundamentalProblemGraph
        """

        fpg = FundamentalProblemGraph(sinks=list_of_sinks, name=name)
        for sink in list_of_sinks:
            ancestors = nx.ancestors(self, sink)
            ancestors.add(sink)
            fpg_sink = self.subgraph(ancestors)
            fpg = nx.compose(fpg, fpg_sink)

        return fpg

    def get_fpg_based_on_list_functions(self, list_of_functions, name='FPG'):
        """Function to get a Fundamental Problem Graph based on a list of functions.

        :param list_of_functions: list with strings that specify the desired functions
        :type list_of_functions: list
        :param name: name of the graph to be generated
        :type name: str
        :return: Fundamental Problem Graph object
        :rtype: FundamentalProblemGraph
        """

        # make empty copy
        fpg = FundamentalProblemGraph(self, based_on_functions=list_of_functions, kb_path=self.graph['kb_path'],
                                      name=name)

        # build fpg by first determining the required nodes
        required_nodes = set(list_of_functions)
        for function in list_of_functions:
            for edge in fpg.out_edges(function):
                required_nodes.add(edge[1])
            for edge in fpg.in_edges(function):
                required_nodes.add(edge[0])

        for node, data in fpg.nodes(data=True):
            if node not in required_nodes:
                fpg.remove_node(node)

        return fpg

    def get_fpg_based_on_function_nodes(self, *args, **kwargs):
        """Function to get the Fundamental Problem Graph based on a list of (or a single) function.

        :param args: node names of functions of interest
        :type args: str
        :param kwargs: name: name of the graph to be generated
        :type kwargs: name: str
        :return: Fundamental Problem Graph object
        :rtype: FundamentalProblemGraph
        """

        # Input assertions
        name = kwargs.get('name', 'FPG')
        assert isinstance('name', str)
        list_of_functions = list(args)
        for function in list_of_functions:
            assert function in self.nodes, 'Defined function node ' + str(function) + ' does not exist in the graph.'

        # make empty copy
        fpg = FundamentalProblemGraph(self, based_on_functions=list_of_functions, name=name)

        # build FPG by first determining the required nodes
        required_nodes = set(list_of_functions)
        for function in list_of_functions:
            for edge in fpg.out_edges(function):
                required_nodes.add(edge[1])
            for edge in fpg.in_edges(function):
                required_nodes.add(edge[0])

        for node, data in fpg.nodes(data=True):
            if node not in required_nodes:
                fpg.remove_node(node)

        return fpg


class FundamentalProblemGraph(DataGraph, KeChainMixin):

    def __init__(self, *args, **kwargs):
        super(FundamentalProblemGraph, self).__init__(*args, **kwargs)

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CHECKING METHODS                                                      #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _check_category_a(self):
        """Extended method to perform a category A check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(FundamentalProblemGraph, self)._check_category_a()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')
        var_nodes = self.find_all_nodes(category='variable')
        out_nodes = self.find_all_nodes(subcategory='all outputs')

        # Get information
        n_nodes = self.number_of_nodes()
        n_functions = len(func_nodes)
        n_variables = len(var_nodes)

        # Checks on nodes
        category_check, i = check(n_nodes != (n_functions+n_variables),
                                  'The number of total nodes does not match number of function and variable nodes.',
                                  status=category_check,
                                  category='A',
                                  i=i)
        for out_node in out_nodes:
            category_check, i_not = check('problem_role' not in self.node[out_node],
                                          'The attribute problem_role is missing on the output node %s.'
                                          % str(out_node),
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1
        for func_node in func_nodes:
            category_check, i_not = check('problem_role' not in self.node[func_node],
                                          'The attribute problem_role is missing on the function node %s.'
                                          % str(func_node),
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1

        # Return
        return category_check, i

    def _check_category_b(self):
        """Extended method to perform a category B check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(FundamentalProblemGraph, self)._check_category_b()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')

        # Checks
        category_check, i = check('problem_formulation' not in self.graph,
                                  'The problem formulation attribute is missing on the graph.',
                                  status=category_check,
                                  category='B',
                                  i=i)
        if category_check:
            category_check, i = check('mdao_architecture' not in self.graph['problem_formulation'],
                                      'The mdao_architecture attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if category_check:
                category_check, i = check(self.graph['problem_formulation']['mdao_architecture'] not in
                                          self.OPTIONS_ARCHITECTURES,
                                          'Invalid mdao_architecture attribute in the problem formulation.',
                                          status=category_check,
                                          category='B',
                                          i=i)
            category_check, i = check('convergence_type' not in self.graph['problem_formulation'],
                                      'The convergence_type attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if category_check:
                category_check, i = check(self.graph['problem_formulation']['convergence_type'] not in
                                          self.OPTIONS_CONVERGERS,
                                          'Invalid convergence_type %s in the problem formulation.'
                                          % self.graph['problem_formulation']['convergence_type'],
                                          status=category_check,
                                          category='B',
                                          i=i)
            category_check, i = check('function_order' not in self.graph['problem_formulation'],
                                      'The function_order attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if category_check:
                func_order = self.graph['problem_formulation']['function_order']
                category_check, i = check(len(func_order) != len(func_nodes),
                                          'There is a mismatch between the FPG functions and the given function_order, '
                                          + 'namely: %s.' % set(func_nodes).symmetric_difference(set(func_order)),
                                          status=category_check,
                                          category='B',
                                          i=i)
            category_check, i = check('function_ordering' not in self.graph['problem_formulation'],
                                      'The function_ordering attribute is missing in the problem formulation.',
                                      status=category_check,
                                      category='B',
                                      i=i)
            if 'allow_unconverged_couplings' in self.graph['problem_formulation']:
                allow_unconverged_couplings = self.graph['problem_formulation']['allow_unconverged_couplings']
                category_check, i = check(not isinstance(allow_unconverged_couplings, bool),
                                          'The setting allow_unconverged_couplings should be of type boolean.',
                                          status=category_check,
                                          category='B',
                                          i=i)
            if self.graph['problem_formulation']['mdao_architecture'] in get_list_entries(self.OPTIONS_ARCHITECTURES, 5,
                                                                                          6):  # DOE
                category_check, i = check('doe_settings' not in self.graph['problem_formulation'],
                                          'The doe_settings attribute is missing in the problem formulation.',
                                          status=category_check,
                                          category='B',
                                          i=i)
                if category_check:
                    category_check, i = check('doe_method' not in self.graph['problem_formulation']['doe_settings'],
                                              'The doe_method attribute is missing in the doe_settings.',
                                              status=category_check,
                                              category='B',
                                              i=i)
                    if category_check:
                        doe_method = self.graph['problem_formulation']['doe_settings']['doe_method']
                        category_check, i = check(self.graph['problem_formulation']['doe_settings']['doe_method'] not
                                                  in self.OPTIONS_DOE_METHODS,
                                                  'Invalid doe_method (%s) specified in the doe_settings.' % doe_method,
                                                  status=category_check,
                                                  category='B',
                                                  i=i)
                        if doe_method in get_list_entries(self.OPTIONS_DOE_METHODS, 0, 1, 2):  # FF, LHC, Monte Carlo
                            category_check, i = check('doe_runs' not in
                                                      self.graph['problem_formulation']['doe_settings'],
                                                      'The doe_runs attribute is missing in the doe_settings.',
                                                      status=category_check,
                                                      category='B',
                                                      i=i)
                            if category_check:
                                test = not isinstance(self.graph['problem_formulation']['doe_settings']['doe_runs'],
                                                      int) or \
                                       self.graph['problem_formulation']['doe_settings']['doe_runs'] < 0
                                category_check, i = check(test,
                                                          'Invalid doe_runs (%s) specified in the doe_settings.' %
                                                          self.graph['problem_formulation']['doe_settings']['doe_runs'],
                                                          status=category_check,
                                                          category='B',
                                                          i=i)
                        if doe_method in get_list_entries(self.OPTIONS_DOE_METHODS, 1, 2):  # LHC, Monte Carlo
                            category_check, i = check('doe_seed' not in
                                                      self.graph['problem_formulation']['doe_settings'],
                                                      'The doe_seed attribute is missing in the doe_settings.',
                                                      status=category_check,
                                                      category='B',
                                                      i=i)
                            if category_check:
                                test = not isinstance(self.graph['problem_formulation']['doe_settings']['doe_seed'],
                                                      int) or \
                                       self.graph['problem_formulation']['doe_settings']['doe_seed'] < 0
                                category_check, i = check(test,
                                                          'Invalid doe_seed (%s) specified in the doe_settings.' %
                                                          self.graph['problem_formulation']['doe_settings']['doe_seed'],
                                                          status=category_check,
                                                          category='B',
                                                          i=i)

        # Return
        return category_check, i

    def _check_category_c(self):
        """Extended method to perform a category C check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(FundamentalProblemGraph, self)._check_category_c()

        # Get information
        mdao_arch = self.graph['problem_formulation']['mdao_architecture']
        conv_type = self.graph['problem_formulation']['convergence_type']
        allow_unconverged_couplings = self.graph['problem_formulation']['allow_unconverged_couplings']

        # Check if architecture and convergence_type match
        # -> match for converged-MDA, MDF, converged-DOE
        if mdao_arch in [self.OPTIONS_ARCHITECTURES[1], self.OPTIONS_ARCHITECTURES[3], self.OPTIONS_ARCHITECTURES[6]]:
            category_check, i = check(conv_type not in self.OPTIONS_CONVERGERS[:2],
                                      'Convergence type %s does not match with architecture %s.'
                                      % (conv_type, mdao_arch),
                                      status=category_check,
                                      category='C',
                                      i=i)
        # -> match IDF
        if mdao_arch in [self.OPTIONS_ARCHITECTURES[2]]:
            category_check, i = check(conv_type is not self.OPTIONS_CONVERGERS[2],
                                      'Convergence type %s does not match with architecture %s.'
                                      % (conv_type, mdao_arch),
                                      status=category_check,
                                      category='C',
                                      i=i)
        # -> match for unconverged-MDA, IDF, unconverged-OPT, unconverged-DOE
        # TODO: Sort out unconverged coupling mess
        # if mdao_arch in [self.OPTIONS_ARCHITECTURES[0], self.OPTIONS_ARCHITECTURES[4], self.OPTIONS_ARCHITECTURES[5]]:
        #     if allow_unconverged_couplings:
        #         category_check, i = check(conv_type is not self.OPTIONS_CONVERGERS[2],
        #                                   'Convergence type %s does not match with architecture %s. As unconverged '
        #                                   'couplings are allowed, the convergence method None has to be selected.'
        #                                   % (conv_type, mdao_arch),
        #                                   status=category_check,
        #                                   category='C',
        #                                   i=i)
        #     else:
        #         category_check, i = check(conv_type not in self.OPTIONS_CONVERGERS[:2],
        #                                   'Convergence type %s does not match with architecture %s. As unconverged '
        #                                   'couplings are not allowed, a convergence method has to be selected.'
        #                                   % (conv_type, mdao_arch),
        #                                   status=category_check,
        #                                   category='C',
        #                                   i=i)

        # For architectures using convergence, check whether this is necessary
        if category_check:
            coup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
            if mdao_arch == self.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                          conv_type == self.OPTIONS_CONVERGERS[1] else 0),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-MDA".',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch == self.OPTIONS_ARCHITECTURES[3]:  # MDF
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                          conv_type == self.OPTIONS_CONVERGERS[1] else 0),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-OPT".',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch == self.OPTIONS_ARCHITECTURES[2]:  # IDF
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=False),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-OPT".',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch == self.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
                category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                          conv_type == self.OPTIONS_CONVERGERS[1] else 0),
                                          'Inconsistent problem formulation, expected coupling missing. Architecture '
                                          'should be set to "unconverged-DOE".',
                                          status=category_check,
                                          category='C',
                                          i=i)

        # For architectures not using convergence, check whether this is allowed
        if category_check:
            coup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[1]]
            # unconverged-MDA, unconverged-OPT, unconverged-DOE
            if mdao_arch in get_list_entries(self.OPTIONS_ARCHITECTURES, 0, 4, 5):
                if not allow_unconverged_couplings:
                    category_check, i = check(self.check_for_coupling(coup_funcs, only_feedback=True),
                                              'Inconsistent problem formulation, no feedback coupling was expected. '
                                              'Architecture should be set to something using convergence (e.g. MDF). '
                                              'Or setting allow_unconverged_couplings should be set to True.',
                                              status=category_check,
                                              category='C',
                                              i=i)
                if category_check and conv_type is not self.OPTIONS_CONVERGERS[2]:
                    category_check, i = check(not self.check_for_coupling(coup_funcs, only_feedback=True if
                                              conv_type == self.OPTIONS_CONVERGERS[1] else False),
                                              'Inconsistent problem formulation, expected coupling missing. '
                                              'Architecture should be unconverged variant with convergence type None.',
                                              status=category_check,
                                              category='C',
                                              i=i)

        # Check the feedforwardness of the pre-coupling functions
        if category_check:
            precoup_funcs = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[0]]
            category_check, i = check(self.check_for_coupling(precoup_funcs, only_feedback=True),
                                      'Pre-coupling functions contain feedback variables. '
                                      'Pre-coupling functions should be adjusted.',
                                      status=category_check,
                                      category='C',
                                      i=i)

        # Check whether the necessary variables have been marked with the problem_role attribute
        if category_check:
            if mdao_arch in self.OPTIONS_ARCHITECTURES[2:5]:  # IDF, MDF, unconverged-OPT
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                category_check, i = check(len(des_var_nodes) == 0,
                                          'No design variables are specified. Use the problem_role attribute for this.',
                                          status=category_check,
                                          category='C',
                                          i=i)
                # Check the design variables connections
                for des_var_node in des_var_nodes:
                    des_var_sources = self.get_sources(des_var_node)
                    # noinspection PyUnboundLocalVariable
                    category_check, i_not = check(not set(des_var_sources).issubset(precoup_funcs),
                                                  'Design variable %s has a source after the pre-coupling functions. '
                                                  'Adjust design variables or function order to solve this.'
                                                  % des_var_node,
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
                    category_check, i_not = check(self.out_degree(des_var_node) == 0,
                                                  'Design variable %s does not have any targets. Reconsider design '
                                                  'variable selection.' % des_var_node,
                                                  status=category_check,
                                                  category='C',
                                                  i=i+1)
                i += 2
                constraint_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[2]])
                objective_node = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[1]])
                category_check, i = check(len(objective_node) != 1,
                                          '%d objective variables are specified. Only one objective node is allowed. '
                                          'Use the problem_role attribute for this.' % len(objective_node),
                                          status=category_check,
                                          category='C',
                                          i=i)
                constraint_functions = list()
                for idx, node in enumerate(objective_node + constraint_nodes):
                    category_check, i_not = check(self.in_degree(node) != 1,
                                                  'Invalid in-degree of ' + str(self.in_degree(node)) +
                                                  ', while it should be 1 of node: ' + str(node),
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
                    category_check, i_not = check(self.out_degree(node) != 0,
                                                  'Invalid out-degree of '+ str(self.out_degree(node))
                                                  + ', while it should be 0 of node: ' + str(node),
                                                  status=category_check,
                                                  category='C',
                                                  i=i+1)
                    if idx == 0:
                        objective_function = list(self.in_edges(node))[0][0]
                    elif not (list(self.in_edges(node))[0][0] in set(constraint_functions)):
                        constraint_functions.append(list(self.in_edges(node))[0][0])
                i += 2
                if category_check:
                    # Check that the objective function is unique (not also a constraint function)
                    # noinspection PyUnboundLocalVariable
                    category_check, i = check(objective_function in constraint_functions,
                                              'Objective function should be a separate function.',
                                              status=category_check,
                                              category='C',
                                              i=i)
                    optimizer_functions = [objective_function] + constraint_functions
                    # Check that all optimizer function are post-coupling functions for IDF and MDF
                    if mdao_arch in self.OPTIONS_ARCHITECTURES[2:4]:
                        func_cats = self.graph['problem_formulation']['function_ordering']
                        diff = set(optimizer_functions).difference(func_cats[self.FUNCTION_ROLES[2]])
                        coup_check = self.check_for_coupling(optimizer_functions, only_feedback=False)
                        category_check, i = check(diff,
                                                  'Not all optimizer functions are not post-coupling functions, '
                                                  'namely: %s' % diff,
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
                        category_check, i = check(coup_check,
                                                  'The optimizer functions %s are not independent of each other.'
                                                  % optimizer_functions,
                                                  status=category_check,
                                                  category='C',
                                                  i=i)
            if mdao_arch in self.OPTIONS_ARCHITECTURES[:2] + self.OPTIONS_ARCHITECTURES[5:7]:
                # unc-MDA, con-MDA, unc-DOE, con-DOE
                # Check whether quantities of interest have been defined.
                qoi_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[3]])
                category_check, i = check(len(qoi_nodes) == 0,
                                          'No quantities of interest are specified. Use the problem_role attribute for '
                                          'this.',
                                          status=category_check,
                                          category='C',
                                          i=i)
            if mdao_arch in self.OPTIONS_ARCHITECTURES[5:7]:  # unc-DOE, con-DOE
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                category_check, i = check(len(des_var_nodes) == 0,
                                          'No design variables are specified. Use the problem_role attribute for this.',
                                          status=category_check,
                                          category='C',
                                          i=i)
                if category_check:
                    # If custom table, check the samples
                    if self.graph['problem_formulation']['doe_settings']['doe_method'] == self.OPTIONS_DOE_METHODS[3]:
                        all_samples = []
                        for des_var_node in des_var_nodes:
                            category_check, i_not = check('samples' not in self.node[des_var_node],
                                                          'The samples attributes is missing for design variable node'
                                                          ' %s.' % des_var_node,
                                                          status=category_check,
                                                          category='C',
                                                          i=i)
                            if category_check:
                                all_samples.append(self.node[des_var_node]['samples'])
                        i += 1
                        sample_lengths = [len(item) for item in all_samples]
                        # Check whether all samples have the same length
                        category_check, i = check(not sample_lengths.count(sample_lengths[0]) == len(sample_lengths),
                                                  'Not all given samples have the same length, this is mandatory.',
                                                  status=category_check,
                                                  category='C',
                                                  i=i)

        # Return
        return category_check, i

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #

    def add_function_problem_roles(self, function_order_method='manual'):
        """
        Method to add the function problem roles (pre-coupled, coupled, post-coupled functions).

        :param function_order_method: algorithm to be used for the order in which the functions are executed.
        :type function_order_method: basestring
        """

        logger.info('Adding function problem roles...')

        # Input assertions
        assert not self.find_all_nodes(subcategory='all problematic variables'), \
            'Problem roles could not be determined. Graph still has problematic variables.'

        # Determine and check function ordering method
        assert function_order_method in self.OPTIONS_FUNCTION_ORDER_METHOD
        if function_order_method == 'manual':
            assert 'function_order' in self.graph['problem_formulation'], 'function_order must be given as attribute.'
            function_order = self.graph['problem_formulation']['function_order']
        elif function_order_method == 'random':
            raise IOError('Random function ordering method not allowed for adding function problem roles.')

        # Determine the coupling matrix
        coupling_matrix = self.get_coupling_matrix()

        # Determine the different function roles
        # determine non-zero values in the coupling matrix
        non_zeros = np.transpose(np.nonzero(coupling_matrix))
        # remove upper triangle and diagonal elements
        lower_zeros = []
        left_ind = None
        low_ind = None
        for pos in non_zeros:
            if pos[1] < pos[0]:
                lower_zeros.append(pos)
                # Assess left-most feedback coupling node position -> first coupled function
                if left_ind is None:
                    left_ind = pos[1]
                elif pos[1] < left_ind:
                    left_ind = pos[1]
                # Assess lowest feedback coupling node position -> last coupled function
                if low_ind is None:
                    low_ind = pos[0]
                elif pos[0] > low_ind:
                    low_ind = pos[0]

        # Enrich graph function nodes and create dictionary with ordering results
        function_ordering = dict()
        function_ordering[self.FUNCTION_ROLES[0]] = list()
        function_ordering[self.FUNCTION_ROLES[1]] = list()
        function_ordering[self.FUNCTION_ROLES[2]] = list()
        if left_ind is not None:
            for i in range(0, left_ind):
                self.node[function_order[i]]['problem_role'] = self.FUNCTION_ROLES[0]
                function_ordering[self.FUNCTION_ROLES[0]].append(function_order[i])
            for i in range(left_ind, low_ind+1):
                self.node[function_order[i]]['problem_role'] = self.FUNCTION_ROLES[1]
                function_ordering[self.FUNCTION_ROLES[1]].append(function_order[i])
            if low_ind < len(function_order)-1:
                for i in range(low_ind+1, len(function_order)):
                    self.node[function_order[i]]['problem_role'] = self.FUNCTION_ROLES[2]
                    function_ordering[self.FUNCTION_ROLES[2]].append(function_order[i])
        else:
            # noinspection PyUnboundLocalVariable
            for function in function_order:
                self.node[function]['problem_role'] = self.FUNCTION_ROLES[0]
                function_ordering[self.FUNCTION_ROLES[0]].append(function)

        # Add function ordering to the graph as well
        self.graph['problem_formulation']['function_ordering'] = function_ordering

        logger.info('Successfully added function problem roles...')

        return

    def add_problem_formulation(self, mdao_definition, function_order, doe_settings=None):

        # Impose the MDAO architecture
        mdao_architecture, convergence_type, allow_unconverged_couplings = get_mdao_setup(mdao_definition)

        # Define settings of the problem formulation
        self.graph['problem_formulation'] = dict()
        self.graph['problem_formulation']['function_order'] = function_order
        self.graph['problem_formulation']['mdao_architecture'] = mdao_architecture
        self.graph['problem_formulation']['convergence_type'] = convergence_type
        self.graph['problem_formulation']['allow_unconverged_couplings'] = allow_unconverged_couplings

        if doe_settings:
            self.graph['problem_formulation']['doe_settings'] = dict()
            self.graph['problem_formulation']['doe_settings']['doe_method'] = doe_settings['doe_method']
            self.graph['problem_formulation']['doe_settings']['doe_seed'] = doe_settings['doe_seed']
            self.graph['problem_formulation']['doe_settings']['doe_runs'] = doe_settings['doe_runs']

    def get_mg_function_ordering(self):
        """Method to determine the function ordering for MDAO graphs (FPG and MDG) based on an FPG.

        Function ordering has to be adjusted when design variables are used. In that case, the pre-coupling functions
        have to be divided in  two parts: the first part does not use the design variables yet, while the second does.

        :return: function ordering dictionary
        :rtype: dict
        """

        mdao_arch = self.graph['problem_formulation']['mdao_architecture']
        pre_functions = self.graph['problem_formulation']['function_ordering'][self.FUNCTION_ROLES[0]]
        mg_function_ordering = dict(self.graph['problem_formulation']['function_ordering'])

        if mdao_arch in self.OPTIONS_ARCHITECTURES[2:7]:  # IDF, MDF, unc-OPT, unc-DOE, con-DOE
            del mg_function_ordering[self.FUNCTION_ROLES[0]]
            if pre_functions:
                target_set = set()
                des_var_nodes = self.find_all_nodes(attr_cond=['problem_role', '==', self.PROBLEM_ROLES_VARS[0]])
                for des_var in des_var_nodes:
                    # Find targets
                    des_var_targets = self.get_targets(des_var)
                    target_set.update(des_var_targets)
                post_desvars_idx = len(pre_functions)
                for idx, func in enumerate(pre_functions):
                    # Check if the function is in the target set
                    if func in target_set:
                        post_desvars_idx = idx
                        break
                pre_desvars_funcs = pre_functions[:post_desvars_idx]
                post_desvars_funcs = pre_functions[post_desvars_idx:]
            else:
                pre_desvars_funcs = []
                post_desvars_funcs = []
            mg_function_ordering[self.FUNCTION_ROLES[3]] = pre_desvars_funcs
            mg_function_ordering[self.FUNCTION_ROLES[4]] = post_desvars_funcs
            if mdao_arch == self.OPTIONS_ARCHITECTURES[2]:  # IDF
                mg_function_ordering[self.FUNCTION_ROLES[2]].append(self.CONSCONS_STRING)

        return mg_function_ordering

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CONVERSION METHODS                                                    #
    # ---------------------------------------------------------------------------------------------------------------- #

    def create_mpg(self, mg_function_ordering, name='MPG'):
        """Function to automatically create a MPG based on a FPG.

        :param mg_function_ordering: dictionary with MDAO graph function ordering
        :type mg_function_ordering: dict
        :param name: name for the MPG graph
        :type name: basestring
        :return: unconnected FPG (only action blocks and their diagonal position)
        :rtype: MdaoProcessGraph
        """

        from graph_process import MdaoProcessGraph
        mpg = MdaoProcessGraph(kb_path=self.graph.get('kb_path'), name=name,
                               fpg=self, mg_function_ordering=mg_function_ordering)
        mpg.graph['problem_formulation'] = self.graph['problem_formulation']

        return mpg

    def create_mdg(self, mg_function_ordering, name='MDG'):
        """Function to automatically create an MDG based on an FPG.

        :param mg_function_ordering: dictionary with MDAO graph function ordering
        :type mg_function_ordering: dict
        :param name: name for the MDG graph
        :type name: basestring
        :return: baseline MDG (only added additional action blocks, no changed connections)
        :rtype: MdaoDataGraph
        """

        mdg = MdaoDataGraph(self, name=name, mg_function_ordering=mg_function_ordering)

        return mdg

    def get_mpg(self, name='MPG', mdg=None):
        """Create the MDAO process graph for a given FPG.

        :param name: name of the new graph
        :type name: basestring
        :param mdg: data graph to be used for process optimization
        :type mdg: MdaoDataGraph
        :return: MDAO process graph
        :rtype: MdaoProcessGraph
        """

        # Start-up checks
        logger.info('Composing MPG...')
        assert isinstance(name, basestring)
        self.add_function_problem_roles()
        self.check(raise_error=True)

        # Make clean copy of the graph to avoid unwanted links and updates
        graph = self.deepcopy()

        # Local variables
        coor = graph.COORDINATOR_STRING
        mdao_arch = graph.graph['problem_formulation']['mdao_architecture']
        conv_type = graph.graph['problem_formulation']['convergence_type']

        # Get the function ordering for the FPG and assign function lists accordingly.
        mg_function_ordering = graph.get_mg_function_ordering()
        if graph.FUNCTION_ROLES[0] in mg_function_ordering:
            pre_functions = mg_function_ordering[graph.FUNCTION_ROLES[0]]
        elif graph.FUNCTION_ROLES[3] in mg_function_ordering:
            pre_desvars_funcs = mg_function_ordering[graph.FUNCTION_ROLES[3]]
            post_desvars_funcs = mg_function_ordering[graph.FUNCTION_ROLES[4]]
        coup_functions = mg_function_ordering[graph.FUNCTION_ROLES[1]]
        post_functions = mg_function_ordering[graph.FUNCTION_ROLES[2]]

        # Set up MDAO process graph
        mpg = graph.create_mpg(mg_function_ordering, name=name)

        # Make process step of the coordinator equal to zero
        mpg.node[coor]['process_step'] = 0

        # Add process edges for each architecture
        if mdao_arch == graph.OPTIONS_ARCHITECTURES[0]:  # unconverged-MDA
            # noinspection PyUnboundLocalVariable
            sequence1 = [coor] + pre_functions
            mpg.add_simple_sequential_process(sequence1, mpg.node[coor]['process_step'],
                                              end_in_iterative_node=sequence1[0] if
                                              conv_type == graph.OPTIONS_CONVERGERS[2] else None)
            if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                # Then run coupled and post-coupling functions in parallel
                start_node = sequence1[-1]
                mpg.add_parallel_process(start_node, coup_functions,
                                         mpg.node[start_node]['process_step'],
                                         end_node=sequence1[0] if not post_functions else None,
                                         end_in_converger=True if not post_functions else None,
                                         use_data_graph=None)
                start_nodes_post = coup_functions
            elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                sequence2 = [sequence1[-1]] + coup_functions
                mpg.add_simple_sequential_process(sequence2, mpg.node[sequence1[-1]]['process_step'],
                                                  end_in_iterative_node=sequence1[0] if not post_functions else None)
                start_nodes_post = [sequence2[-1]]
            if conv_type in graph.OPTIONS_CONVERGERS[0:2] and post_functions:  # Jacobi or Gauss-Seidel
                # noinspection PyUnboundLocalVariable
                mpg.add_parallel_process(start_nodes_post, post_functions,
                                         start_step=mpg.node[start_nodes_post[0]]['process_step'],
                                         end_node=coor, end_in_converger=True, use_data_graph=mdg)
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
            conv = graph.CONVERGER_STRING
            # noinspection PyUnboundLocalVariable
            sequence = [coor] + pre_functions + [conv]
            mpg.add_simple_sequential_process(sequence, mpg.node[coor]['process_step'])
            if conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                sequence2 = [graph.CONVERGER_STRING] + coup_functions
                mpg.add_simple_sequential_process(sequence2, mpg.node[conv]['process_step'], end_in_iterative_node=conv)
            elif conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                mpg.add_parallel_process(conv, coup_functions, mpg.node[conv]['process_step'],
                                         end_node=conv, end_in_converger=True, use_data_graph=None)
            if post_functions:
                mpg.add_parallel_process(conv, post_functions, mpg.node[conv]['converger_step'],
                                         end_node=coor, end_in_converger=True, use_data_graph=None)
            else:
                mpg.connect_nested_iterators(coor, conv)
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[2]:  # IDF
            opt = graph.OPTIMIZER_STRING
            # noinspection PyUnboundLocalVariable
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_simple_sequential_process(sequence1, mpg.node[coor]['process_step'])
            # noinspection PyUnboundLocalVariable
            sequence2 = [opt] + post_desvars_funcs
            mpg.add_simple_sequential_process(sequence2, mpg.node[opt]['process_step'])
            mpg.add_parallel_process(sequence2[-1], coup_functions, mpg.node[sequence2[-1]]['process_step'],
                                     use_data_graph=None)
            mpg.add_parallel_process(coup_functions, post_functions, mpg.node[coup_functions[0]]['process_step'],
                                     end_node=opt, end_in_converger=True, use_data_graph=mdg)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[3]:  # MDF
            opt = graph.OPTIMIZER_STRING
            conv = graph.CONVERGER_STRING
            # noinspection PyUnboundLocalVariable
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_simple_sequential_process(sequence1, mpg.node[coor]['process_step'])
            # noinspection PyUnboundLocalVariable
            sequence2 = [opt] + post_desvars_funcs + [conv]
            mpg.add_simple_sequential_process(sequence2, mpg.node[opt]['process_step'])
            if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                mpg.add_parallel_process(conv, coup_functions, mpg.node[conv]['process_step'],
                                         end_node=conv, end_in_converger=True, use_data_graph=None)
            elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                sequence3 = [conv] + coup_functions
                mpg.add_simple_sequential_process(sequence3, mpg.node[conv]['process_step'],
                                                  end_in_iterative_node=sequence3[0])
            mpg.add_parallel_process(conv, post_functions, mpg.node[conv]['converger_step'],
                                     end_node=opt, end_in_converger=True, use_data_graph=None)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[4]:  # unconverged-OPT
            opt = graph.OPTIMIZER_STRING
            # noinspection PyUnboundLocalVariable
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_simple_sequential_process(sequence1, mpg.node[coor]['process_step'])
            # noinspection PyUnboundLocalVariable
            sequence2 = [opt] + post_desvars_funcs
            mpg.add_simple_sequential_process(sequence2, mpg.node[opt]['process_step'],
                                              end_in_iterative_node=sequence2[0] if
                                              conv_type == graph.OPTIONS_CONVERGERS[2] else None)
            if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                # Then run coupled and post-coupling functions in parallel
                start_node = sequence2[-1]
                mpg.add_parallel_process(start_node, coup_functions,
                                         mpg.node[start_node]['process_step'], use_data_graph=None)
                start_nodes_post = coup_functions
            elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                sequence = [sequence2[-1]]+coup_functions
                mpg.add_simple_sequential_process(sequence, mpg.node[sequence2[-1]]['process_step'])
                start_nodes_post = [sequence[-1]]
            if conv_type in graph.OPTIONS_CONVERGERS[0:2]:  # Jacobi or Gauss-Seidel
                # noinspection PyUnboundLocalVariable
                mpg.add_parallel_process(start_nodes_post, post_functions,
                                         start_step=mpg.node[start_nodes_post[0]]['process_step'],
                                         end_node=opt, end_in_converger=True, use_data_graph=mdg)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[5]:  # unconverged-DOE
            doe = graph.DOE_STRING
            # noinspection PyUnboundLocalVariable
            sequence1 = [coor] + pre_desvars_funcs + [doe]
            mpg.add_simple_sequential_process(sequence1, mpg.node[coor]['process_step'])
            # noinspection PyUnboundLocalVariable
            sequence2 = [doe] + post_desvars_funcs
            mpg.add_simple_sequential_process(sequence2, mpg.node[doe]['process_step'],
                                              end_in_iterative_node=sequence2[0] if
                                              conv_type == graph.OPTIONS_CONVERGERS[2] else None)
            if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                # Then run coupled and post-coupling functions in parallel
                start_node = sequence2[-1]
                mpg.add_parallel_process(start_node, coup_functions,
                                         mpg.node[start_node]['process_step'], use_data_graph=None)
                start_nodes_post = coup_functions
            elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                sequence = [sequence2[-1]] + coup_functions
                mpg.add_simple_sequential_process(sequence, mpg.node[sequence2[-1]]['process_step'])
                start_nodes_post = [sequence[-1]]
            if conv_type in graph.OPTIONS_CONVERGERS[0:2] and post_functions:  # Jacobi or Gauss-Seidel
                # noinspection PyUnboundLocalVariable
                mpg.add_parallel_process(start_nodes_post, post_functions,
                                         start_step=mpg.node[start_nodes_post[0]]['process_step'],
                                         end_node=doe, end_in_converger=True, use_data_graph=mdg)
            mpg.connect_nested_iterators(coor, doe)
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
            doe = graph.DOE_STRING
            conv = graph.CONVERGER_STRING
            # noinspection PyUnboundLocalVariable
            sequence1 = [coor] + pre_desvars_funcs + [doe]
            mpg.add_simple_sequential_process(sequence1, mpg.node[coor]['process_step'])
            # noinspection PyUnboundLocalVariable
            sequence2 = [doe] + post_desvars_funcs + [conv]
            mpg.add_simple_sequential_process(sequence2, mpg.node[doe]['process_step'])
            if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                mpg.add_parallel_process(conv, coup_functions, mpg.node[conv]['process_step'],
                                         end_node=conv, end_in_converger=True, use_data_graph=None)
            elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                sequence3 = [conv] + coup_functions
                mpg.add_simple_sequential_process(sequence3, mpg.node[conv]['process_step'],
                                                  end_in_iterative_node=sequence3[0])
            if post_functions:
                mpg.add_parallel_process(conv, post_functions, mpg.node[conv]['converger_step'],
                                         end_node=doe, end_in_converger=True, use_data_graph=None)
            else:
                mpg.connect_nested_iterators(doe, conv)
            mpg.connect_nested_iterators(coor, doe)

        mpg.graph['process_hierarchy'] = mpg.get_process_hierarchy()

        logger.info('Composed MPG.')

        return mpg

    def get_mdg(self, name='MDG'):
        """
        Create the MDAO data graph for a given FPG.

        :param name: name of the new graph
        :type name: basestring
        :return: MDAO data graph
        :rtype: MdaoDataGraph
        """

        # Start-up checks
        logger.info('Composing MDG...')
        assert isinstance(name, basestring)
        self.add_function_problem_roles()
        self.check(raise_error=True)

        # Make clean copy of the graph to avoid unwanted links and updates
        graph = self.deepcopy()

        # Load variables from FPG
        mdao_arch = graph.graph['problem_formulation']['mdao_architecture']
        conv_type = graph.graph['problem_formulation']['convergence_type']
        if 'allow_unconverged_couplings' in graph.graph['problem_formulation']:
            allow_unconverged_couplings = graph.graph['problem_formulation']['allow_unconverged_couplings']
        else:
            allow_unconverged_couplings = False

        # Determine special variables and functions
        if mdao_arch in graph.OPTIONS_ARCHITECTURES[2:7]:  # IDF, MDF, unc-OPT, unc-DOE, con-DOE
            des_var_nodes = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[0]])
        if mdao_arch in graph.OPTIONS_ARCHITECTURES[2:5]:  # IDF, MDF, unconverged-OPT
            constraint_nodes = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[2]])
            objective_node = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[1]])[0]
        qoi_nodes = graph.find_all_nodes(attr_cond=['problem_role', '==', graph.PROBLEM_ROLES_VARS[3]])

        # Get the function ordering for the FPG and assign coupling function lists accordingly.
        mg_function_ordering = graph.get_mg_function_ordering()
        coup_functions = mg_function_ordering[graph.FUNCTION_ROLES[1]]

        # Set up MDAO data graph
        mdg = graph.create_mdg(mg_function_ordering, name=name)

        # Manipulate data graph
        if mdao_arch == graph.OPTIONS_ARCHITECTURES[0]:  # unconverged-MDA
            if allow_unconverged_couplings:
                # Manipulate the coupling variables based on the architecture
                if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                                  converger=None, include_couplings_as_final_output=False)
                elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=False,
                                                  converger=None, include_couplings_as_final_output=False)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
            conv = graph.CONVERGER_STRING
            # Connect converger
            mdg.connect_converger(conv, conv_type, coup_functions, True)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[2]:  # IDF
            opt = graph.OPTIMIZER_STRING
            # Connect optimizer as a converger using the consistency constraint function
            mdg.connect_converger(opt, graph.OPTIONS_ARCHITECTURES[2], coup_functions, True)
            # Connect optimizer w.r.t. design variables, objective, contraints
            # noinspection PyUnboundLocalVariable
            mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[3]:  # MDF
            opt = graph.OPTIMIZER_STRING
            conv = graph.CONVERGER_STRING
            # Connect converger
            mdg.connect_converger(conv, conv_type, coup_functions, True)
            # Connect optimizer
            # noinspection PyUnboundLocalVariable
            mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[4]:  # unconverged-OPT
            opt = graph.OPTIMIZER_STRING
            if allow_unconverged_couplings:
                # Manipulate the coupling variables based on the architecture
                if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                                  converger=None, include_couplings_as_final_output=True)
                elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=False,
                                                  converger=None, include_couplings_as_final_output=True)
            # Connect optimizer
            # noinspection PyUnboundLocalVariable
            mdg.connect_optimizer(opt, des_var_nodes, objective_node, constraint_nodes)
            # Connect QOIs to the coordinator
            mdg.connect_qoi_nodes_as_input(qoi_nodes, graph.COORDINATOR_STRING, True)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[5]:  # unconverged-DOE
            doe = graph.DOE_STRING
            if allow_unconverged_couplings:
                # Manipulate the coupling variables based on the architecture
                if conv_type == graph.OPTIONS_CONVERGERS[0]:  # Jacobi
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=True,
                                                  converger=None, include_couplings_as_final_output=False)
                elif conv_type == graph.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
                    mdg.manipulate_coupling_nodes(coup_functions, remove_feedback=True, remove_feedforward=False,
                                                  converger=None, include_couplings_as_final_output=False)
            # Connect doe block
            # noinspection PyUnboundLocalVariable
            mdg.connect_doe_block(doe, des_var_nodes, qoi_nodes)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()
        elif mdao_arch == graph.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
            doe = graph.DOE_STRING
            conv = graph.CONVERGER_STRING
            # Connect converger
            mdg.connect_converger(conv, conv_type, coup_functions, False)
            # Connect doe block
            # noinspection PyUnboundLocalVariable
            mdg.connect_doe_block(doe, des_var_nodes, qoi_nodes)
            # Connect remaining system inputs and outputs to the coordinator
            mdg.connect_coordinator()

        logger.info('Composed MDG.')

        return mdg

    def impose_mdao_architecture(self):
        """
        Method to directly get both the MDG and MPG of an FPG.

        :return: MdaoDataGraph and MdaoProcessGraph
        :rtype: tuple
        """
        mdg = self.get_mdg()
        mpg = mdg.get_mpg()
        return mdg, mpg


class MdaoDataGraph(DataGraph, MdaoMixin):

    def __init__(self, *args, **kwargs):
        super(MdaoDataGraph, self).__init__(*args, **kwargs)
        if 'mg_function_ordering' in kwargs:
            mg_function_ordering = kwargs['mg_function_ordering']
            self._add_action_blocks_and_roles(mg_function_ordering)
            self.graph['function_ordering'] = mg_function_ordering

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CHECKING METHODS                                                      #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _check_category_a(self):
        """Extended method to perform a category A check on the graph.

        :return: result of the check and index
        :rtype: bool, int
        """

        # Set check
        category_check, i = super(MdaoDataGraph, self)._check_category_a()

        # Get nodes
        func_nodes = self.find_all_nodes(category='function')
        var_nodes = self.find_all_nodes(category='variable')

        # Get information
        n_nodes = self.number_of_nodes()
        n_functions = len(func_nodes)
        n_variables = len(var_nodes)

        # Checks on nodes
        category_check, i = check(n_nodes != (n_functions+n_variables),
                                  'The number of total nodes does not match number of function and variable nodes.',
                                  status=category_check,
                                  category='A',
                                  i=i)
        for node in var_nodes:
            category_check, i_not = check(self.in_degree(node) == 0,
                                          'The node %s has in-degree 0.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i)
            category_check, i_not = check(self.out_degree(node) == 0,
                                          'The node %s has out-degree 0.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i+1)
        i += 1
        category_check, i = check(not self.has_node(self.COORDINATOR_STRING),
                                  'The %s node is missing in the graph.' % self.COORDINATOR_STRING,
                                  status=category_check,
                                  category='A',
                                  i=i)
        for node in func_nodes:
            category_check, i_not = check('architecture_role' not in self.node[node],
                                          'The architecture_role attribute is missing on the node %s.' % node,
                                          status=category_check,
                                          category='A',
                                          i=i)
        i += 1

        # Return
        return category_check, i

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                            CREATE METHODS                                                        #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _create_cmdows_workflow_problem_def(self):

        # Create workflow/problemDefinitionUID
        cmdows_workflow_problem_def = Element('problemDefinitionUID')
        cmdows_workflow_problem_def.text = (str(self.graph['problem_formulation'].get('mdao_architecture')) +
                                            str(self.graph['problem_formulation'].get('convergence_type')))

        return cmdows_workflow_problem_def

    def _create_cmdows_architecture_elements(self):

        # Create architectureElement
        cmdows_architecture_elements = Element('architectureElements')

        # Create architectureElements/parameters
        cmdows_parameters = cmdows_architecture_elements.add('parameters')
        # Create architectureElements/parameters/instances
        # noinspection PyUnusedLocal
        cmdows_instances = cmdows_parameters.add('instances')
        # TODO: Implement this
        # Create architectureElements/parameters/...
        for architecture_roles_var in self.ARCHITECTURE_ROLES_VARS:
            cmdows_parameter = cmdows_parameters.add(make_camel_case(architecture_roles_var, make_plural_option=True))
            graph_parameter_nodes = self.find_all_nodes(attr_cond=['architecture_role', '==', architecture_roles_var])
            for graph_parameter_node in graph_parameter_nodes:
                cmdows_parameter_node = cmdows_parameter.add(make_camel_case(architecture_roles_var))
                cmdows_parameter_node.set('uID', graph_parameter_node)
                cmdows_parameter_node.add('relatedParameterUID',
                                          self.node[graph_parameter_node].get('related_to_schema_node'))
                cmdows_parameter_node.add('label',
                                          self.node[graph_parameter_node].get('label'))

        # Create architectureElements/executableBlocks
        cmdows_executable_blocks = cmdows_architecture_elements.add('executableBlocks')
        # Create architectureElements/executableBlocks/...
        for architecture_roles_fun in self.CMDOWS_ARCHITECTURE_ROLE_SPLITTER:
            graph_nodes = self.find_all_nodes(attr_cond=['architecture_role', '==', architecture_roles_fun])
            cmdows_executable_block = cmdows_executable_blocks.add(make_camel_case(architecture_roles_fun,
                                                                                   make_plural_option=True))
            # Create architectureElements/executableBlocks/.../...
            for graph_node in graph_nodes:

                cmdows_executable_block_elem = cmdows_executable_block.add(make_camel_case(architecture_roles_fun))
                cmdows_executable_block_elem.set('uID', graph_node)
                cmdows_executable_block_elem.add('label', self.node[graph_node].get('label'))

                if architecture_roles_fun == 'optimizer':
                    cmdows_executable_block_elem.add('settings', self.node[graph_node].get('settings'))
                    graph_des_vars = [{'designVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[0]+var} for var in
                                      self.node[graph_node].get('design_variables')]
                    cmdows_executable_block_elem.add('designVariables', graph_des_vars)
                    graph_obj_vars = [{'objectiveVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[1] + var} for var in
                                      self.node[graph_node].get('objective_variable')]
                    cmdows_executable_block_elem.add('objectiveVariables', graph_obj_vars)
                    graph_con_vars = [{'constraintVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[2] + var} for var in
                                      self.node[graph_node].get('constraint_variables')]
                    cmdows_executable_block_elem.add('constraintVariables', graph_con_vars)

                elif architecture_roles_fun == 'doe':
                    graph_settings = self.node[graph_node].get('settings')
                    cmdows_settings = cmdows_executable_block_elem.add('settings')
                    if graph_settings.get('doe_table') is not None:
                        cmdows_table = cmdows_settings.add('doeTable')
                        for graph_row_index, graph_row in enumerate(graph_settings.get('doe_table_order')):
                            cmdows_row = cmdows_table.add('tableRow', attrib={'relatedParameterUID': str(graph_row)})
                            for graph_element_index, graph_element in enumerate(graph_settings.get('doe_table')):
                                cmdows_row.add('tableElement', graph_element[graph_row_index],
                                               attrib={'experimentID': str(graph_element_index)})
                    cmdows_settings.add('doeMethod', graph_settings.get('doe_method'))
                    graph_des_vars = [{'designVariableUID': self.PROBLEM_ROLES_VAR_SUFFIXES[0] + var} for var in
                                      self.node[graph_node].get('design_variables')]
                    cmdows_executable_block_elem.add('designVariables', graph_des_vars)

                else:
                    cmdows_executable_block_elem.add('settings', self.node[graph_node].get('settings'))

        # Create architectureElements/executableBlocks/...Analyses/...
        architecture_roles_funs = np.setdiff1d(self.ARCHITECTURE_ROLES_FUNS, self.CMDOWS_ARCHITECTURE_ROLE_SPLITTER,
                                               assume_unique=True)
        for architecture_roles_fun in architecture_roles_funs:
            nodes = self.find_all_nodes(attr_cond=['architecture_role', '==', str(architecture_roles_fun)])
            cmdows_analyses = cmdows_executable_blocks.add(make_camel_case(architecture_roles_fun,
                                                                           make_plural_option=True))
            for node in nodes:
                cmdows_analysis = cmdows_analyses.add(make_camel_case(architecture_roles_fun))
                cmdows_analysis.add('relatedExecutableBlockUID', node)

        return cmdows_architecture_elements

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                             LOAD METHODS                                                         #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _load_cmdows_architecture_elements(self, cmdows):

        # Create architecture element nodes
        cmdows_architecture_parameters = cmdows.find('architectureElements/parameters')
        for cmdows_architecture_parameter in list(cmdows_architecture_parameters):
            for cmdows_single_architecture_parameter in list(cmdows_architecture_parameter):
                cmdows_uid = cmdows_single_architecture_parameter.get('uID')
                attrb = cmdows.finddict(cmdows_single_architecture_parameter, ordered=False, camel_case_conversion=True)
                attrb = translate_dict_keys(attrb, {'related_parameter_u_i_d': 'related_to_schema_node'})
                self.add_node(cmdows_uid,
                              attr_dict=attrb,
                              category='variable',
                              architecture_role=unmake_camel_case(cmdows_single_architecture_parameter.tag, ' '))
        cmdows_architecture_exe_blocks = cmdows.find('architectureElements/executableBlocks')
        for cmdows_architecture_exe_block in list(cmdows_architecture_exe_blocks):
            for cmdows_single_architecture_exe_block in list(cmdows_architecture_exe_block):
                cmdows_uid = cmdows_single_architecture_exe_block.get('uID')

                if cmdows_uid is not None:
                    role = unmake_camel_case(cmdows_single_architecture_exe_block.tag, ' ')
                    self.add_node(cmdows_uid,
                                  category='function',
                                  architecture_role=role,
                                  label=cmdows_single_architecture_exe_block.findasttext('label'),
                                  settings=cmdows_single_architecture_exe_block.findasttext('settings'))
                    if role == 'optimizer' or role == 'doe':
                        cmdows_des_vars = cmdows_single_architecture_exe_block.findall('designVariables/designVariable')
                        graph_des_vars = [var.findtext('designVariableUID')[10:] for var in list(cmdows_des_vars)]
                        self.node[cmdows_uid]['design_variables'] = graph_des_vars
                    if role == 'optimizer':
                        cmdows_des_vars = cmdows_single_architecture_exe_block.findall('objectiveVariables/objectiveVariable')
                        graph_des_vars = [var.findtext('objectiveVariableUID')[10:] for var in list(cmdows_des_vars)]
                        self.node[cmdows_uid]['objective_variable'] = graph_des_vars
                        cmdows_des_vars = cmdows_single_architecture_exe_block.findall('constraintVariables/constraintVariable')
                        graph_des_vars = [var.findtext('constraintVariableUID')[10:] for var in list(cmdows_des_vars)]
                        self.node[cmdows_uid]['constraint_variables'] = graph_des_vars
                    elif role == 'doe':
                        cmdows_rows = list(cmdows_single_architecture_exe_block.findall('settings/doeTable/tableRow'))
                        graph_rows = [cmdows_row.get('relatedParameterUID') for cmdows_row in cmdows_rows]
                        graph_table = []
                        for cmdows_row in cmdows_rows:
                            def get_experiment_id(elem):
                                return float(elem.get('experimentID'))
                            elements = sorted(cmdows_row, key=get_experiment_id)
                            graph_table.append([element.findasttext() for element in elements])
                        graph_table = map(list, zip(*graph_table))
                        if 'settings' not in self.node[cmdows_uid] or self.node[cmdows_uid]['settings'] is None:
                            self.node[cmdows_uid]['settings'] = {}
                        self.node[cmdows_uid]['settings']['doe_table_order'] = graph_rows
                        self.node[cmdows_uid]['settings']['doe_table'] = graph_table
                        self.node[cmdows_uid]['settings']['doe_method'] = cmdows_single_architecture_exe_block.findtext('settings/doeMethod')

                else:
                    for role in self.ARCHITECTURE_ROLES_FUNS:
                        cmdows_role_name = make_camel_case(role)
                        if cmdows_single_architecture_exe_block.tag == cmdows_role_name:
                            cmdows_uid = cmdows_single_architecture_exe_block.find('relatedExecutableBlockUID').text
                            self.node[cmdows_uid]['architecture_role'] = role

    # ---------------------------------------------------------------------------------------------------------------- #
    #                                          GRAPH SPECIFIC METHODS                                                  #
    # ---------------------------------------------------------------------------------------------------------------- #

    def _add_action_blocks_and_roles(self, mg_function_ordering):
        """Method to add function blocks to the MDG based on the FPG function ordering

        :param mg_function_ordering: ordered list of functions to be added
        :type mg_function_ordering: list
        """

        # Set input settings
        mdao_arch = self.graph['problem_formulation']['mdao_architecture']

        # Add coordinator node
        assert not self.has_node(self.COORDINATOR_STRING), 'Coordinator name already in use in FPG.'
        self.add_node(self.COORDINATOR_STRING,
                      category='function',
                      architecture_role=self.ARCHITECTURE_ROLES_FUNS[0],
                      shape='8',
                      label=self.COORDINATOR_LABEL,
                      level=None)

        # No optimizer present
        if self.FUNCTION_ROLES[0] in mg_function_ordering:
            functions = mg_function_ordering[self.FUNCTION_ROLES[0]]
            for func in functions:
                self.node[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[4]

        # Optimizer / DOE present
        if self.FUNCTION_ROLES[3] in mg_function_ordering:
            # Add pre-optimizer functions
            functions = mg_function_ordering[self.FUNCTION_ROLES[3]]
            for func in functions:
                self.node[func]['architecture_role'] = 'pre-iterator analysis'
            # Add optimizer / DOE
            if mdao_arch in self.OPTIONS_ARCHITECTURES[2:5]:  # IDF, MDF, unc-OPT
                assert not self.has_node(self.OPTIMIZER_STRING), 'Optimizer name already in use in FPG.'
                self.add_node(self.OPTIMIZER_STRING,
                              category='function',
                              architecture_role=self.ARCHITECTURE_ROLES_FUNS[1],
                              shape='8',
                              label=self.OPTIMIZER_LABEL,
                              level=None)
            elif mdao_arch in self.OPTIONS_ARCHITECTURES[5:7]:  # unc-DOE, con-DOE
                assert not self.has_node(self.DOE_STRING), 'DOE name already in use in FPG.'
                self.add_node(self.DOE_STRING,
                              category='function',
                              architecture_role=self.ARCHITECTURE_ROLES_FUNS[3],  # doe
                              shape='8',
                              label=self.DOE_LABEL,
                              level=None,
                              settings=self.graph['problem_formulation']['doe_settings'])
            # Add architecture role to post-iterator functions
            functions = mg_function_ordering[self.FUNCTION_ROLES[4]]
            for func in functions:
                self.node[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[6]

        # Converger required
        if mdao_arch in [self.OPTIONS_ARCHITECTURES[1]] + [self.OPTIONS_ARCHITECTURES[3]] + \
                [self.OPTIONS_ARCHITECTURES[6]]:  # con-MDA, MDF, con-DOE
            # Add converger
            assert not self.has_node(self.CONVERGER_STRING), 'Converger name already in use in FPG.'
            self.add_node(self.CONVERGER_STRING,
                          category='function',
                          architecture_role=self.ARCHITECTURE_ROLES_FUNS[2],
                          shape='8',
                          label=self.CONVERGER_LABEL,
                          level=None)

        # Add architecture role to coupled functions
        for func in mg_function_ordering[self.FUNCTION_ROLES[1]]:
            self.node[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[7]

        # Add post-coupling functions
        for func in mg_function_ordering[self.FUNCTION_ROLES[2]]:
            if func != self.CONSCONS_STRING:
                self.node[func]['architecture_role'] = self.ARCHITECTURE_ROLES_FUNS[8]
            else:
                assert not self.has_node(self.CONSCONS_STRING), 'Consistency constraint name already in use in FPG.'
                self.add_node(self.CONSCONS_STRING,
                              label=self.CONSCONS_LABEL,
                              level=None,
                              shape='s',
                              category='function',
                              architecture_role=self.ARCHITECTURE_ROLES_FUNS[9])

        return

    def copy_node_as(self, node, architecture_role):
        """Method to copy a given node for an architecture role.

        :param node: node to be copied
        :type node: str
        :param architecture_role: architecture role of the copied node
        :type architecture_role: basestring
        :return: modified node
        """

        assert self.has_node(node), "Node %s is not present in the graph." % node
        assert architecture_role in self.ARCHITECTURE_ROLES_VARS, "Invalid architecture role %s specified." % \
                                                                  architecture_role
        xpath_nodes = node.split('/')
        root = xpath_nodes[1]
        if architecture_role == self.ARCHITECTURE_ROLES_VARS[6]:  # consistency constraint variable
            new_node = '/' + root + '/architectureNodes/' + make_camel_case(architecture_role) + 's' + \
                       '/' + root + 'Copy/' + '/'.join(xpath_nodes[2:-1]) + '/gc_' + xpath_nodes[-1]
            # TODO: This needs to be fixed, now used to make RCE WF work for IDF (g_y1) instead of (y1)
        else:
            new_node = '/' + root + '/architectureNodes/' + make_camel_case(architecture_role) + 's' + \
                       '/' + root + 'Copy/' + '/'.join(xpath_nodes[2:])
        if architecture_role == self.ARCHITECTURE_ROLES_VARS[0]:  # initial guess coupling variable
            label_prefix = ''
            label_suffix = '^{c0}'
        elif architecture_role in [self.ARCHITECTURE_ROLES_VARS[1],
                                   self.ARCHITECTURE_ROLES_VARS[5]]:  # final coupling/output variable
            label_prefix = ''
            label_suffix = '^*'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[2]:  # coupling variable
            label_prefix = ''
            label_suffix = '^c'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[3]:  # initial guess design variable
            label_prefix = ''
            label_suffix = '^0'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[4]:  # final design variable
            label_prefix = ''
            label_suffix = '^*'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[6]:  # consistency constraint variable
            label_prefix = 'gc_'
            label_suffix = ''
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[7]:  # doe input samples
            label_prefix = 'DOE_'
            label_suffix = '_inp'
        elif architecture_role == self.ARCHITECTURE_ROLES_VARS[8]:  # doe output samples
            label_prefix = 'DOE_'
            label_suffix = '_out'
        else:
            raise IOError('Label extension could not be found.')

        node_data_dict = dict(self.node[node])

        # Determine the related schema node
        if 'related_to_schema_node' in node_data_dict:
            related_schema_node = node_data_dict['related_to_schema_node']
        else:
            related_schema_node = node

        if not self.has_node(new_node):
            self.add_node(new_node,
                          category=node_data_dict['category'],
                          related_to_schema_node=related_schema_node,
                          architecture_role=architecture_role,
                          shape=node_data_dict.get('shape'),
                          label=label_prefix+node_data_dict['label']+label_suffix)
        return new_node

    def connect_qoi_nodes_as_input(self, nodes, function, override_with_final_outputs):
        """Method to connect a list of qoi nodes as input to a given function node.

        :param nodes: list of nodes to be connected as input
        :type nodes: list
        :param function: function to which the nodes are connected
        :type function: basestring
        :param override_with_final_outputs: setting on whether to override the use of final outputs
        :type override_with_final_outputs: bool
        """

        for node in nodes:
            assert self.has_node(node)
            # Check if there is a final output node as well and use that one instead.
            if override_with_final_outputs:
                schema_related_nodes = self.find_all_nodes(category='variable',
                                                           attr_cond=['related_to_schema_node', '==', node])
                for schema_related_node in schema_related_nodes:
                    if 'architecture_role' in self.node[schema_related_node]:
                        if self.node[schema_related_node]['architecture_role'] in \
                                get_list_entries(self.ARCHITECTURE_ROLES_VARS, 1, 4, 5):
                            node = schema_related_node
            self.add_edge(node, function)

        return

    def connect_nodes_as_output(self, nodes, function):
        """Method to connect a list of nodes as output to a function node.

        :param nodes: list of nodes to be connected as output
        :type nodes: list
        :param function: function to which the nodes are connected
        :type function: basestring
        """

        for node in nodes:
            assert self.has_node(node)
            self.add_edge(function, node)

        return

    def connect_coordinator(self):
        """Method to automatically connect all system inputs and outputs of a graph to the coordinator node."""

        # Get system inputs and outputs
        input_nodes = self.find_all_nodes(subcategory='all inputs')
        output_nodes = self.find_all_nodes(subcategory='all outputs')

        # Connect the nodes to the coordinator
        for input_node in input_nodes:
            self.add_edge(self.COORDINATOR_STRING, input_node)
        for output_node in output_nodes:
            self.add_edge(output_node, self.COORDINATOR_STRING)

        return

    def connect_converger(self, converger, conv_type, coupling_functions, include_couplings_as_final_output):
        """Method to automatically connect a converger around a collection of coupled functions.

        :param converger: name of the converger to be connected
        :type converger: basestring
        :param conv_type: setting for the type of convergence (Jacobi, Gauss-Seidel)
        :type conv_type: basestring
        :param coupling_functions: list of coupled functions
        :type coupling_functions: list
        :param include_couplings_as_final_output: setting on whether coupling variables should always be added as output
        :type include_couplings_as_final_output: bool
        """

        # Input assertions
        assert self.has_node(converger), 'Converger is not present in the graph.'
        assert conv_type in self.OPTIONS_CONVERGERS + [self.OPTIONS_ARCHITECTURES[2]], \
            'Invalid converger type %s specified.' % conv_type
        assert isinstance(coupling_functions, list)
        for coupling_function in coupling_functions:
            assert self.has_node(coupling_function), 'Missing coupling function %s in the graph.' % coupling_function

        # Manipulate the coupling variables based on the architecture
        if conv_type == self.OPTIONS_CONVERGERS[0]:  # Jacobi
            self.manipulate_coupling_nodes(coupling_functions, remove_feedback=True, remove_feedforward=True,
                                           converger=converger,
                                           include_couplings_as_final_output=include_couplings_as_final_output)
        elif conv_type == self.OPTIONS_CONVERGERS[1]:  # Gauss-Seidel
            self.manipulate_coupling_nodes(coupling_functions, remove_feedback=True, remove_feedforward=False,
                                           converger=converger,
                                           include_couplings_as_final_output=include_couplings_as_final_output)
        elif conv_type == self.OPTIONS_ARCHITECTURES[2]:  # IDF
            self.manipulate_coupling_nodes(coupling_functions, remove_feedback=True, remove_feedforward=True,
                                           converger=converger,
                                           include_couplings_as_final_output=include_couplings_as_final_output)

        return

    def connect_optimizer(self, optimizer, design_variable_nodes, objective_node, constraint_nodes):
        """Method to automatically connect an optimizer w.r.t. the design variables, objective, and constraints.

        :param optimizer: name of the optimizer to be connected
        :type optimizer: basestring
        :type design_variable_nodes: list
        :param objective_node: node used as objective by the optimizer
        :type objective_node: basestring
        :param constraint_nodes: list of constraint nodes
        :type constraint_nodes: list
        :return: enriched MDAO data graph with connected optimizer
        :rtype: MdaoDataGraph
        """

        # Input assertions
        assert self.has_node(optimizer), 'Optimizer is not present in the graph.'
        assert isinstance(design_variable_nodes, list)
        for des_var in design_variable_nodes:
            assert self.has_node(des_var), 'Design variable %s is missing in the graph.' % des_var
        assert isinstance(objective_node, basestring)
        assert self.has_node(objective_node), 'Objective node %s is missing in the graph.' % objective_node
        assert isinstance(constraint_nodes, list)
        for con_var in constraint_nodes:
            assert self.has_node(con_var), 'Constraint variable %s is missing in the graph.' % con_var

        # Add attributes to the optimizer block
        self.node[optimizer]['design_variables'] = dict()
        for des_var in design_variable_nodes:
            self.node[optimizer]['design_variables'][des_var] = dict()
            if 'upper_bound' in self.node[des_var]:
                self.node[optimizer]['design_variables'][des_var]['upper_bound'] = self.node[des_var]['upper_bound']
            else:
                self.node[optimizer]['design_variables'][des_var]['upper_bound'] = None
            if 'lower_bound' in self.node[des_var]:
                self.node[optimizer]['design_variables'][des_var]['lower_bound'] = self.node[des_var]['lower_bound']
            else:
                self.node[optimizer]['design_variables'][des_var]['lower_bound'] = None
            if 'nominal_value' in self.node[des_var]:
                self.node[optimizer]['design_variables'][des_var]['nominal_value'] = self.node[des_var]['nominal_value']
            else:
                self.node[optimizer]['design_variables'][des_var]['nominal_value'] = None
        self.node[optimizer]['objective_variable'] = [objective_node]
        self.node[optimizer]['constraint_variables'] = dict()
        for con_var in constraint_nodes:
            self.node[optimizer]['constraint_variables'][con_var] = dict()
            if 'upper_bound' in self.node[con_var]:
                self.node[optimizer]['constraint_variables'][con_var]['upper_bound'] = self.node[con_var]['upper_bound']
            else:
                self.node[optimizer]['constraint_variables'][con_var]['upper_bound'] = None
            if 'lower_bound' in self.node[con_var]:
                self.node[optimizer]['constraint_variables'][con_var]['lower_bound'] = self.node[con_var]['lower_bound']
            else:
                self.node[optimizer]['constraint_variables'][con_var]['lower_bound'] = None

        # Manipulate the graph based on the architecture
        # Connect design variables to the optimizer
        pre_opt_funcs = self.graph['function_ordering'][self.FUNCTION_ROLES[3]]
        for des_var in design_variable_nodes:
            # Create initial guess design variable
            ini_guess_node = self.copy_node_as(des_var, architecture_role=self.ARCHITECTURE_ROLES_VARS[3])
            # If des_var comes from pre-des-var function, then reconnect (remove previous connection, connect to guess)
            des_var_sources = self.get_sources(des_var)
            if des_var_sources:
                pre_des_var_func = list(set(des_var_sources).intersection(pre_opt_funcs))[0]
                if pre_des_var_func:
                    self.remove_edge(pre_des_var_func, des_var)
                    self.add_edge(pre_des_var_func, ini_guess_node)
            # Connect initial guess design variable to optimizer
            self.add_edge(ini_guess_node, optimizer)
            # Connect design variable as output from optimizer
            self.add_edge(optimizer, des_var)
            # Create final design variable
            fin_value_node = self.copy_node_as(des_var, architecture_role=self.ARCHITECTURE_ROLES_VARS[4])
            # Connect final design variable as output from optimizer
            self.add_edge(optimizer, fin_value_node)
        # Connect objective and constraint nodes to the optimizer
        for var in [objective_node] + constraint_nodes:
            # Connect regular variable version to optimizer
            self.add_edge(var, optimizer)
            # Create a final value copy and connect it as output of the associated functions
            fin_value_node = self.copy_node_as(var, architecture_role=self.ARCHITECTURE_ROLES_VARS[5])
            self.copy_edge([self.get_sources(var)[0], var],[self.get_sources(var)[0], fin_value_node])
        # If the graph contains consistency constraint variables, then connect these to the optimizer as well
        consconcs_nodes = self.find_all_nodes(category='variable',
                                              attr_cond=['architecture_role', '==', self.ARCHITECTURE_ROLES_VARS[6]])
        # Add consistency constraints as constraints in the graph
        for node in consconcs_nodes:
            rel_node = self.node[node]['related_to_schema_node']
            # Add design variables to optimizer attributes
            self.node[optimizer]['design_variables'][rel_node] = dict()
            if 'upper_bound' in self.node[rel_node]:
                self.node[optimizer]['design_variables'][rel_node]['upper_bound'] = self.node[rel_node]['upper_bound']
            else:
                self.node[optimizer]['design_variables'][rel_node]['upper_bound'] = None
            if 'lower_bound' in self.node[rel_node]:
                self.node[optimizer]['design_variables'][rel_node]['lower_bound'] = self.node[rel_node]['lower_bound']
            else:
                self.node[optimizer]['design_variables'][rel_node]['lower_bound'] = None
            self.add_edge(node, optimizer)

    def connect_doe_block(self, doe_block, design_variable_nodes, qoi_nodes):
        """Method to automatically connect an doe_block w.r.t. the design variables, objective, and constraints.

        :param doe_block: name of the doe_block to be connected
        :type doe_block: basestring
        :param design_variable_nodes: list of design variables
        :type design_variable_nodes: list
        :param qoi_nodes: list of constraint nodes
        :type qoi_nodes: list
        :return: enriched MDAO data graph with connected doe_block
        :rtype: MdaoDataGraph
        """

        # Input assertions
        assert self.has_node(doe_block), 'DOE is not present in the graph.'
        assert isinstance(design_variable_nodes, list)
        for des_var in design_variable_nodes:
            assert self.has_node(des_var), 'Design variable %s is missing in the graph.' % des_var
        assert isinstance(qoi_nodes, list)
        for qoi_var in qoi_nodes:
            assert self.has_node(qoi_var), 'Q.O.I. variable %s is missing in the graph.' % qoi_var

        # Add attributes to the doe block
        self.node[doe_block]['design_variables'] = dict()
        for des_var in design_variable_nodes:
            self.node[doe_block]['design_variables'][des_var] = dict()
            if 'upper_bound' in self.node[des_var]:
                self.node[doe_block]['design_variables'][des_var]['upper_bound'] = self.node[des_var]['upper_bound']
            else:
                self.node[doe_block]['design_variables'][des_var]['upper_bound'] = None
            if 'lower_bound' in self.node[des_var]:
                self.node[doe_block]['design_variables'][des_var]['lower_bound'] = self.node[des_var]['lower_bound']
            else:
                self.node[doe_block]['design_variables'][des_var]['lower_bound'] = None
            if 'nominal_value' in self.node[des_var]:
                self.node[doe_block]['design_variables'][des_var]['nominal_value'] = self.node[des_var][
                    'nominal_value']
            else:
                self.node[doe_block]['design_variables'][des_var]['nominal_value'] = None
            if 'samples' in self.node[des_var]:
                self.node[doe_block]['design_variables'][des_var]['samples'] = self.node[des_var]['samples']
            else:
                self.node[doe_block]['design_variables'][des_var]['samples'] = None
        self.node[doe_block]['quantities_of_interest'] = qoi_nodes

        # For the custom design table, add the table with values to the settings
        if self.graph['problem_formulation']['doe_settings']['doe_method'] == 'Custom design table':
            n_samples = len(self.node[doe_block]['design_variables'][design_variable_nodes[-1]]['samples'])
            doe_table = []
            for idj in range(n_samples):
                doe_table.append([])
                for des_var in design_variable_nodes:
                    doe_table[idj].append(self.node[des_var]['samples'][idj])
            self.graph['problem_formulation']['doe_settings']['doe_table'] = doe_table
            self.graph['problem_formulation']['doe_settings']['doe_table_order'] = design_variable_nodes

        # Manipulate the graph based on the architecture
        # Connect design variables to the doe_block
        pre_doe_funcs = self.graph['function_ordering'][self.FUNCTION_ROLES[3]]
        for des_var in design_variable_nodes:
            # Create DOE input samples
            doe_input_node = self.copy_node_as(des_var, architecture_role=self.ARCHITECTURE_ROLES_VARS[7])
            # If des_var comes from pre-des-var function then remove this connection (DOE uses separate list of samples)
            des_var_sources = self.get_sources(des_var)
            pre_des_var_funcs = list(set(des_var_sources).intersection(pre_doe_funcs))
            if pre_des_var_funcs:
                pre_des_var_func = pre_des_var_funcs[0]
                self.remove_edge(pre_des_var_func, des_var)
                # If des_var has become a hole, remove it
                if self.node_is_hole(des_var):
                    self.add_edge(pre_des_var_func, doe_input_node)
            # Connect DOE input samples to doe_block
            self.add_edge(doe_input_node, doe_block)
            # Connect design variable as output from doe_block
            self.add_edge(doe_block, des_var)
        # Connect QOI nodes to the doe_block
        for var in qoi_nodes:
            # Connect regular variable version to doe_block
            self.add_edge(var, doe_block)
            # Create a DOE output samples node and connect it as output of the DOE
            doe_output_node = self.copy_node_as(var, architecture_role=self.ARCHITECTURE_ROLES_VARS[8])
            self.add_edge(doe_block, doe_output_node)

        return

    def manipulate_coupling_nodes(self, func_order, remove_feedback, remove_feedforward, converger=None,
                                  include_couplings_as_final_output=False):
        """Method to manipulate the coupling nodes in a data graph in order to remove unwanted feedback/feedforward.

        :param func_order: the order of the functions to be analyzed
        :type func_order: list
        :param remove_feedback: setting on whether feedback coupling should be removed
        :type remove_feedback: bool
        :param remove_feedforward: setting on whether feedforward coupling should be removed
        :type remove_feedforward: bool
        :param converger: setting on whether the couplings should be linked to a converger
        :type converger: basestring or None
        :param include_couplings_as_final_output: setting on whether coupling variables should always be added as output
        :type include_couplings_as_final_output: bool
        """

        # Get all the relevant couplings
        if remove_feedback and remove_feedforward:
            direction = "both"
        elif remove_feedback and not remove_feedforward:
            direction = "backward"
        elif not remove_feedback and remove_feedforward:
            direction = "forward"
        else:
            raise IOError("Invalid settings on feedback and feedforward specific.")
        couplings = self.get_direct_coupling_nodes(func_order, direction=direction, print_couplings=False)

        # Manipulate the coupling nodes accordingly
        for coupling in couplings:
            # Remove coupling edge between coupling variable -> function
            self.remove_edge(coupling[2], coupling[1])
            # Create initial guess coupling variable node
            ini_guess_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[0])
            # If there is no converger node, then just add an initial guess of the coupled node
            if converger is None:
                # Connect initial guess as input to coupled function
                self.add_edge(ini_guess_node, coupling[1])
            # If there is a converger node, then connect it accordingly
            elif converger == self.CONVERGER_STRING:
                # Connect initial guess as input to the converger
                self.add_edge(ini_guess_node, converger)
                # Create coupling copy variable (coming from converger) and connect it accordingly
                coupling_copy_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[2])
                if not self.has_edge(converger, coupling_copy_node):
                    self.add_edge(converger, coupling_copy_node)
                self.add_edge(coupling_copy_node, coupling[1])
                # Connect original coupling node to the converger
                self.add_edge(coupling[2], self.CONVERGER_STRING)
            # If the converger node in an optimizer (IDF), then connect it accordingly
            elif converger == self.OPTIMIZER_STRING:
                # Connect initial guess as input to the optimizer
                self.add_edge(ini_guess_node, converger)
                # Make original coupling node a design variable
                self.mark_as_design_variable(coupling[2])
                # Create coupling copy variable (coming from converger/optimizer) and connect it accordingly
                coupling_copy_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[2])
                if not self.has_edge(converger, coupling_copy_node):
                    self.add_edge(converger, coupling_copy_node)
                self.add_edge(coupling_copy_node, coupling[1])
                # Connect original and copied coupling node to the consistency constraint function
                self.add_edge(coupling[2], self.CONSCONS_STRING)
                self.add_edge(coupling_copy_node, self.CONSCONS_STRING)
                # Create consistency constraint variables for each coupling and make them output of the function
                consistency_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[6])
                self.mark_as_constraint(consistency_node, '==', 0.0)
                self.add_edge(self.CONSCONS_STRING, consistency_node)
                if 'consistency_nodes' in self.node[self.CONSCONS_STRING]:
                    self.node[self.CONSCONS_STRING]['consistency_nodes'].append(consistency_node)
                else:
                    self.node[self.CONSCONS_STRING]['consistency_nodes'] = [consistency_node]
            # If required, create final coupling variable node and let it come from the coupled function
            if converger and ('problem_role' in self.node[coupling[2]] or include_couplings_as_final_output):
                final_node = self.copy_node_as(coupling[2], self.ARCHITECTURE_ROLES_VARS[1])
                self.copy_edge([coupling[0], coupling[2]], [coupling[0], final_node])
                keep_original_coupling_node = False
            elif not converger and ('problem_role' in self.node[coupling[2]] or include_couplings_as_final_output):
                keep_original_coupling_node = True
            else:
                keep_original_coupling_node = False
            # Remove original coupling node if it has become an output
            if self.node_is_output(coupling[2]) and not keep_original_coupling_node:
                self.remove_node(coupling[2])

        return

    def create_mpg(self, name='MPG'):
        """Function to automatically create a MPG based on an MDG.

        :param name: name for the MPG graph
        :type name: basestring
        :return: unconnected MDG (only action blocks and their diagonal position)
        :rtype: MdaoProcessGraph
        """
        from graph_process import MdaoProcessGraph
        mpg = MdaoProcessGraph(self, name=name)
        node_list = list(mpg.nodes)
        for node in node_list:
            if 'category' not in mpg.node[node]:
                raise AssertionError('category attribute missing for node: {}.'.format(node))
            elif mpg.node[node]['category'] == 'variable':
                mpg.remove_node(node)
            elif mpg.node[node]['category'] not in ['variable', 'function']:
                raise AssertionError('Node {} has invalid category attribute: {}.'.format(node, mpg.node[node]['category']))
        mpg._add_diagonal_positions()
        return mpg

    def get_mpg(self, name='MPG'):
        """Create the MDAO process graph for a given FPG.

        :param name: name of the new graph
        :type name: basestring
        :return: MDAO process graph
        :rtype: MdaoProcessGraph
        """

        # Start-up checks
        logger.info('Composing MPG...')
        assert isinstance(name, basestring)
        self.check(raise_error=True)

        # Make clean copy of the graph to avoid unwanted links and updates
        mdg = self.copy_as(MdaoDataGraph, as_view=True)

        # Local variables
        coor = mdg.COORDINATOR_STRING
        mdao_arch = mdg.graph['problem_formulation']['mdao_architecture']

        # Get the function ordering for the FPG and assign function lists accordingly.
        mg_function_ordering = mdg.graph['mg_function_ordering']
        if mdg.FUNCTION_ROLES[0] in mg_function_ordering:
            pre_functions = mg_function_ordering[mdg.FUNCTION_ROLES[0]]
        elif mdg.FUNCTION_ROLES[3] in mg_function_ordering:
            pre_desvars_funcs = mg_function_ordering[mdg.FUNCTION_ROLES[3]]
            post_desvars_funcs = mg_function_ordering[mdg.FUNCTION_ROLES[4]]
        coup_functions = mg_function_ordering[mdg.FUNCTION_ROLES[1]]
        post_functions = mg_function_ordering[mdg.FUNCTION_ROLES[2]]

        # Set up MDAO process graph
        mpg = mdg.create_mpg(name=name)

        # Make process step of the coordinator equal to zero
        mpg.node[coor]['process_step'] = 0

        # Add process edges for each architecture
        if mdao_arch == mdg.OPTIONS_ARCHITECTURES[0]:  # unconverged-MDA
            sequence = [coor] + pre_functions + coup_functions + post_functions
            mpg.add_process(sequence, 0, mdg, end_in_iterative_node=coor)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[1]:  # converged-MDA
            conv = mdg.CONVERGER_STRING
            sequence = [coor] + pre_functions + [conv]
            mpg.add_process(sequence, 0, mdg)
            sequence2 = [conv] + coup_functions
            mpg.add_process(sequence2, mpg.node[sequence[-1]]['process_step'], mdg, end_in_iterative_node=conv)
            if post_functions:
                sequence3 = [conv] + post_functions
                mpg.add_process(sequence3, mpg.node[conv]['converger_step'], mdg, end_in_iterative_node=coor)
            else:
                mpg.connect_nested_iterators(coor, conv)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[2]:  # IDF
            opt = mdg.OPTIMIZER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [opt] + post_desvars_funcs + coup_functions + post_functions
            mpg.add_process(sequence2, mpg.node[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=opt)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[3]:  # MDF
            opt = mdg.OPTIMIZER_STRING
            conv = mdg.CONVERGER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [opt] + post_desvars_funcs + [conv]
            mpg.add_process(sequence2, mpg.node[sequence1[-1]]['process_step'], mdg)
            sequence3 = [conv] + coup_functions
            mpg.add_process(sequence3, mpg.node[sequence2[-1]]['process_step'], mdg, end_in_iterative_node=conv)
            sequence4 = [conv] + post_functions
            mpg.add_process(sequence4, mpg.node[conv]['converger_step'], mdg, end_in_iterative_node=opt)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[4]:  # unconverged-OPT
            opt = mdg.OPTIMIZER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [opt]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [opt] + post_desvars_funcs + coup_functions + post_functions
            mpg.add_process(sequence2, mpg.node[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=opt)
            mpg.connect_nested_iterators(coor, opt)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[5]:  # unconverged-DOE
            doe = mdg.DOE_STRING
            sequence1 = [coor] + pre_desvars_funcs + [doe]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [doe] + post_desvars_funcs + coup_functions + post_functions
            mpg.add_process(sequence2, mpg.node[sequence1[-1]]['process_step'], mdg, end_in_iterative_node=doe)
            mpg.connect_nested_iterators(coor, doe)
        elif mdao_arch == mdg.OPTIONS_ARCHITECTURES[6]:  # converged-DOE
            doe = mdg.DOE_STRING
            conv = mdg.CONVERGER_STRING
            sequence1 = [coor] + pre_desvars_funcs + [doe]
            mpg.add_process(sequence1, 0, mdg)
            sequence2 = [doe] + post_desvars_funcs + [conv]
            mpg.add_process(sequence2, mpg.node[sequence1[-1]]['process_step'], mdg)
            sequence3 = [conv] + coup_functions
            mpg.add_process(sequence3, mpg.node[sequence2[-1]]['process_step'], mdg, end_in_iterative_node=conv)
            if post_functions:
                sequence4 = [conv] + post_functions
                mpg.add_process(sequence4, mpg.node[conv]['converger_step'], mdg, end_in_iterative_node=doe)
            else:
                mpg.connect_nested_iterators(doe, conv)
            mpg.connect_nested_iterators(coor, doe)

        mpg.graph['process_hierarchy'] = mpg.get_process_hierarchy()

        logger.info('Composed MPG.')

        return mpg
