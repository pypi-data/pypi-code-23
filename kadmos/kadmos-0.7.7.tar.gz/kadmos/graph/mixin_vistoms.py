# Imports
import json
import os
import re
import shutil
import linecache
import logging
# noinspection PyPackageRequirements
import tempfile

import progressbar
from kadmos.cmdows import CMDOWS

import kadmos.vispack as vispack

from lxml import etree

from ..utilities.xmls import get_element_details, recursively_unique_attribute, merge
from ..utilities.general import make_camel_case, get_list_entries, format_string_for_vistoms, get_element_dict


# Settings for the logger
logger = logging.getLogger(__name__)

THEDATA_PREFIX = '			theData = '
VISTOMS_NAME = 'VISTOMS.html'
VISTOMS_TV_NAME = 'VISTOMS_TreeViewer.html'
LOCAL_FILE_REFS = dict(REP__Acknowledgements__REP="file:include/Acknowledgements.svg",
                       REP__AGILE_Icon__REP="include/AGILE_Icon.png",
                       REP__AGILE_Logo__REP="file:include/AGILE_Logo.png",
                       REP__Contact__REP="file:include/Contact.svg",
                       REP__Home__REP="file:include/Home.svg",
                       REP__RWTH_Logo__REP="file:include/RWTH_Logo.svg",
                       REP__TUDelft_Logo__REP="file:include/TUDelft_Logo.svg",
                       REP__Tutorial__REP="file:include/Tutorial.svg",
                       REP__VISTOMS_Label__REP="file:include/VISTOMS_Label.svg")

class VistomsMixin(object):

    def vistoms_create(self, vistoms_dir, vistoms_version=None, mpg=None, function_order=None, reference_file=None,
                       compress=False, remove_after_compress=True, graph_id=None, use_png_figs=False, file_refs=None):
        """Function to create a new VISTOMS instance from a graph.

        :type self: KadmosGraph
        :param vistoms_dir: directory of the VISTOMS directory to be created
        :type vistoms_dir: str
        :param vistoms_version: version of the VISTOMS instance to be used (as stored in the package itself)
        :param vispack_version: str
        :param mpg: optional MPG graph to be saved with MDG as XDSM (if None a DSM is created)
        :type mpg: MdaoProcessGraph
        :param function_order: optional function order for the diagonal of the graph (only applicable for DSMs)
        :type function_order: list
        :param reference_file: file from which reference values are extracted (either full path or file in same folder)
        :type reference_file: str
        :param compress: setting whether to compress the final VISTOMS instance folder to a zip file
        :type compress: bool
        :param remove_after_compress: setting whether to remove the original folder after compression
        :type remove_after_compress: bool
        :param graph_id: identifier of the new graph
        :type graph_id: basestring
        :param use_png_figs: setting whether to use the PNG figures instead of the SVG figures for local execution
        :type use_png_figs: bool
        :param file_refs: setting to provide file references manually (to use VISTOMS on a server)
        :type file_refs: dict
        """
        # Check inputs
        self._vistoms_assertions(mpg, function_order, reference_file, vistoms_version, graph_id)

        # Logging
        logger.info('Creating the VISTOMS instance (this might take a while)...')

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        # Get absolute path of vistoms_dir
        vistoms_dir = os.path.abspath(vistoms_dir)

        # Initiate VISTOMS instance
        vispack.copy(temp_dir, vispack_version=vistoms_version)

        # Create dictionary for the data.json file
        data = dict(graphs=[], categories=[])

        # Add categories
        data['categories'].append({'name': 'schema', 'description': 'schema'})
        data['categories'].append({"name": "catschema_nodeLev", "description": "node levels"})
        data['categories'].append({"name": "catschema_funLev", "description": "function levels"})
        data['categories'].append({"name": "catschema_roleLev", "description": "role levels"})
        data['categories'].append({"name": "catschema_sysLev", "description": "system levels"})

        # Set default graph ID
        if graph_id is None:
            graph_id = '01'

        # Determine graph data entry
        graph_entry = self._vispack_get_graph_data_entry(graph_id, mpg=mpg, order=function_order,
                                                         reference_file=reference_file)

        # Put graph data entry in the data dictionary
        data['graphs'].append(graph_entry)

        data_str = json.dumps(data)

        # Define string replacements based on file referencing
        if file_refs is None:
            rep = dict(LOCAL_FILE_REFS)
            if use_png_figs:
                for key,item in rep.iteritems():
                    if '.svg' in item:
                        rep[key] = item.replace('.svg', '.png')
            rep['REP__GRAPH_DATA__REP'] = data_str
        else:
            rep = file_refs
            for key,item in LOCAL_FILE_REFS.iteritems():
                assert key in rep, 'Replacement key %s is missing in the file_refs.' % key
            rep['REP__GRAPH_DATA__REP'] = data_str

        # Perform the text replacement
        rep = dict((re.escape(k), v) for k, v in rep.iteritems())
        pattern = re.compile("|".join(rep.keys()))
        with open(os.path.join(temp_dir, 'VISTOMS_datarepl.html'), "rt") as fin:
            with open(os.path.join(temp_dir, VISTOMS_NAME), "wt") as fout:
                for line in fin:
                    fout.write(pattern.sub(lambda m: rep[re.escape(m.group(0))], line))

        # Remove the original VISTOMS file
        os.remove(os.path.join(temp_dir, 'VISTOMS_datarepl.html'))

        # Copy temp directory to file path
        # Remove previous VISTOMS directory (if present)
        try:
            shutil.rmtree(vistoms_dir)
        except OSError:
            pass
        # Place new VISTOMS folder
        shutil.copytree(temp_dir, vistoms_dir)
        # Remove temporary directory
        shutil.rmtree(temp_dir)

        if compress:
            _compress_vistoms_instance(vistoms_dir, remove_after_compress)

        # Logging
        logger.info('Successfully created the VISTOMS instance.')

        return

    def vistoms_add(self, vistoms_dir, mpg=None, function_order=None, reference_file=None, compress=False,
                    remove_after_compress=True, graph_id=None, replacement_id=None):
        """Function to add a graph to a existing VISTOMS instance.

        In one VISTOMS instance different graphs can be shown. For example it is possible to include different
        architectures for the same problem in one VISTOMS instance.

        :param vistoms_dir: directory of the VISTOMS directory to be used for addition
        :type vistoms_dir: str
        :param mpg: optional MPG graph to be saved with MDG as XDSM (if None a DSM is created)
        :type mpg: MdaoProcessGraph
        :param function_order: optional function order for the diagonal of the graph (only applicable for DSMs)
        :type function_order: list
        :param reference_file: file from which reference values are extracted (either full path or file in same folder)
        :type reference_file: str
        :param compress: setting whether to compress the final VISTOMS instance folder to a zip file
        :type compress: bool
        :param remove_after_compress: setting whether to remove the original folder after compression
        :type remove_after_compress: bool
        :param replacement_id: indentifier of the graph to be replaced
        :type replacement_id: basestr
        """

        # Check inputs
        self._vistoms_assertions(mpg, function_order, reference_file, None, graph_id)
        if replacement_id:
            assert isinstance(replacement_id, str), 'The attribute replacement_id should be of type str.'
        assert os.path.exists(vistoms_dir), 'There is not VISTOMS instance at %s.' % vistoms_dir
        assert os.path.exists(os.path.join(vistoms_dir, VISTOMS_NAME)), VISTOMS_NAME + \
                                                                           ' not found in folder %s.' % vistoms_dir

        # Logging
        logger.info('Adding graph to the VISTOMS instance (this might take a while)...')

        # Create vistoms file name path
        vistoms_file = os.path.join(vistoms_dir, VISTOMS_NAME)

        # Create temporary directory
        temp_dir = tempfile.mkdtemp()

        # Copy VISTOMS_NAME file to the temp directory
        temp_file = os.path.join(temp_dir, VISTOMS_NAME)
        shutil.copy(vistoms_file, temp_file)

        # Get the graph data and line number
        data, data_linenumber = _get_the_data(temp_file)

        if replacement_id is not None:
            # Find IDs in the current data.json
            graph_ids = [graph['id'] for graph in data['graphs']]
            assert replacement_id in graph_ids, 'Could not find replacement_id: %s. Available IDs: %s.' % \
                                                (replacement_id, graph_ids)
            replacement_index = graph_ids.index(replacement_id)
        if graph_id is None:
            if replacement_id is None:
                graph_id = str(len(data['graphs']) + 1).zfill(2)
                assert int(graph_id) < 100, 'graph_id (%d) should be smaller than 100.' % int(graph_id)
            else:
                graph_id = replacement_id

        # Determine graph data entry
        graph_entry = self._vispack_get_graph_data_entry(graph_id, mpg=mpg, order=function_order,
                                                         reference_file=reference_file)

        # Add graph_entry at the right location
        if replacement_id is None:
            data['graphs'].append(graph_entry)
        else:
            data['graphs'][replacement_index] = graph_entry

        # Replace the graph data
        data_str = json.dumps(data)
        _replace_line(temp_file, data_linenumber, THEDATA_PREFIX + data_str)

        # Copy VISTOMS_NAME to original folder
        # Remove previous VISTOMS_NAME
        try:
            os.remove(vistoms_file)
        except OSError:
            pass
        # Place new VISTOMS_NAME file
        os.rename(temp_file, vistoms_file)
        # Remove temporary directory
        shutil.rmtree(temp_dir)

        if compress:
            _compress_vistoms_instance(vistoms_dir, remove_after_compress)

        # Logging
        logger.info('Successfully added graph to the VISTOMS instance.')

        return

    def _vistoms_assertions(self, mpg, function_order, reference_file, vistoms_version, graph_id):
        """Function to check the inputs for the VISTOMS instance functions."""

        from graph_kadmos import KadmosGraph
        from graph_process import MdaoProcessGraph
        assert isinstance(self, KadmosGraph)
        if mpg:
            assert isinstance(mpg, MdaoProcessGraph)
        assert not isinstance(self, MdaoProcessGraph)
        assert isinstance(function_order, list) or function_order is None
        assert isinstance(vistoms_version, basestring) or vistoms_version is None
        if reference_file is not None:
            assert os.path.exists(reference_file)
        if mpg and function_order:
            logger.warning('Both an FPG and order list are given. The FPG is used for the determination of the order.')
        assert isinstance(graph_id, basestring) or graph_id is None

    def _vispack_get_graph_data_entry(self, graph_id, mpg=None, order=None, reference_file=None):
        """
        Function to make the json files required to for the VISTOMS instance.

        :type self: KadmosGraph
        :param mpg: MDO Process Graph
        :type mpg: MdaoProcessGraph
        :param order: list with the order in which the tools should be placed (only required if the FPG is not given)
        :type order: list, None
        :param reference_file: file from which reference values are extracted (either full path or file in same folder)
        :type reference_file: file
        :return: dictionary entry with all graph data
        :rtype: dict
        """

        # Start-up
        self.get_nodes_subcategory()

        coordinator_str = self.COORDINATOR_STRING

        # Check graph name and description
        if not 'name' in self.graph:
            self.add_default_name()
        if not 'description' in self.graph:
            self.add_default_description()

        # Create graph_data dictionary entry and fill in initial attributes
        graph_data_entry = dict(name=self.graph.get('name'),
                                id=graph_id,
                                description=self.graph.get('description'),
                                variableSchemes=dict())
        for attr in self.graph:
            graph_data_entry[attr] = self.graph[attr]

        # Get full_graph dictionary
        full_graph = self._get_full_graph()

        # Determine / check analysis order based on the full_graph
        if not order:
            if not mpg:
                # Get tool list and put the coordinator in the top left corner
                tool_list = list(full_graph['attributes']['tools'])
                tool_list.remove(coordinator_str)
                order = [coordinator_str] + tool_list
            else:
                # Find order based on FPG
                order = []
                for idx in range(0, mpg.number_of_nodes()):
                    node_list = mpg.find_all_nodes(attr_cond=['diagonal_position', '==', idx])
                    assert len(
                        node_list) == 1, "Somehow, a unique diagonal position '%d' could not be found in the FPG" % idx
                    order.append(node_list[0])
        else:
            order = [coordinator_str] + order
            order_differences = set(order).difference(full_graph['attributes']['tools'])
            name_differences = set(full_graph['attributes']['tools']).difference(order)
            actual_tool_names = full_graph['attributes']['tools']
            actual_tool_names.remove(coordinator_str)

            assert not order_differences, \
                'Given order of tools does not match the tool names in the graph. \nInvalid name(s): %s.' \
                ' \nActual tool names: %s' % (', '.join(list(order_differences)), ', '.join(actual_tool_names))
            assert not name_differences, 'Given order of tools misses one or more tools present in the graph, ' \
                                         'namely: %s.' % ', '.join(name_differences)

        # Get edge bundles data and tools data
        edge_bundles_list, functions_data_list = self._get_edge_bundles_and_functions_data(full_graph)
        # Write dictionary entry
        graph_data_entry['edgeBundles'] = edge_bundles_list

        # Get xdsm definition
        xdsm_dict = self._get_xdsm(order, edge_bundles_list, mpg)
        # Write dictionary entry
        graph_data_entry['xdsm'] = xdsm_dict

        # Get variable tree based on schema
        variable_tree_dataschema = self._get_variable_tree_dataschema(full_graph, reference_file)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['schema'] = variable_tree_dataschema

        # Get variable tree based on system level categories (inputs, outputs, couplings)
        variable_tree_categorized_system_level = self._get_variable_tree_categorized_system_level(full_graph)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['catschema_sysLev'] = variable_tree_categorized_system_level

        # Node level sorting of the variables (input, shared input, shared coupling, collision, etc.)
        variable_tree_categorized_node_level = self._get_variable_tree_categorized_node_level(full_graph)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['catschema_nodeLev'] = variable_tree_categorized_node_level

        # Role level sorting of the variables (problem roles / architecture roles)
        variable_tree_categorized_role_level = self._get_variable_tree_categorized_role_level(full_graph)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['catschema_roleLev'] = variable_tree_categorized_role_level

        # Function level sorting of the variables (function inputs, function outputs)
        variable_tree_categorized_function_level = self._get_variable_tree_categorized_function_level(functions_data_list)
        # Write dictionary entry
        graph_data_entry['variableSchemes']['catschema_funLev'] = variable_tree_categorized_function_level

        return graph_data_entry

    def _get_full_graph(self):
        """Method to create the full_graph dictionary. The full_graph is a dictionary with the following structure
        {node_key:[input_nodes to node_key]}

        :return: full_graph dictionary
        :rtype: dict
        """

        # Settings
        circular_cats = self.NODE_GROUP_SUBCATS['all circular variables']
        circular_coor_input_cats = get_list_entries(circular_cats, 0, 1)
        circular_coor_output_cats = get_list_entries(circular_cats, 0, 2)
        coordinator_str = self.COORDINATOR_STRING

        # Start-up
        logger.debug('Creating full_graph_data dictionary...')
        full_graph = dict(attributes=dict(tools=[], variables=[]))

        # Add coordinator to the full_graph to avoid errors later on (in case the coordinator has no inputs)
        full_graph[coordinator_str] = []
        full_graph['attributes']['tools'].append(coordinator_str)
        for edge in self.edges():
            # Check if the source is already in the dictionary (else add empty list)
            if edge[0] not in full_graph:
                # Add as output of coordinator (if node is a system input or of a certain circular variable category)
                if (self.in_degree(edge[0]) == 0 and self.node[edge[0]]['category'] == 'variable') or \
                                self.node[edge[0]]['subcategory'] in circular_coor_input_cats:
                    full_graph[edge[0]] = [coordinator_str]
                    full_graph['attributes']['tools'].append(coordinator_str)
                else:
                    full_graph[edge[0]] = []
                if self.node[edge[0]]['category'] == 'function':
                    full_graph['attributes']['tools'].append(edge[0])
                elif self.node[edge[0]]['category'] == 'variable':
                    full_graph['attributes']['variables'].append(edge[0])
                else:
                    raise NotImplementedError('Node category %s is not allowed.' % self.node[edge[0]]['category'])
            else:
                # Add as output of coordinator (if node is a system input or of a certain circular variable category)
                if (self.in_degree(edge[0]) == 0 and self.node[edge[0]]['category'] == 'variable') or \
                                self.node[edge[0]]['subcategory'] in circular_coor_input_cats:
                    full_graph[edge[0]].append(coordinator_str)
            # Check if the target is already in the dictionary
            if edge[1] in full_graph:
                full_graph[edge[1]].append(edge[0])
            else:
                full_graph[edge[1]] = [edge[0]]
                if self.node[edge[1]]['category'] == 'function':
                    full_graph['attributes']['tools'].append(edge[1])
                elif self.node[edge[1]]['category'] == 'variable':
                    full_graph['attributes']['variables'].append(edge[1])
                else:
                    raise NotImplementedError('Node category %s is not allow.' % self.node[edge[1]]['category'])
            # Check if the target is a system output (according to indegree or circularity)
            if (self.out_degree(edge[1]) == 0 and self.node[edge[1]]['category'] == 'variable') or \
                            self.node[edge[1]]['subcategory'] in circular_coor_output_cats:
                if coordinator_str in full_graph:
                    full_graph[coordinator_str].append(edge[1])
                else:
                    full_graph[coordinator_str] = [edge[1]]
                    full_graph['attributes']['tools'].append(coordinator_str)

        # Remove duplicates from the list
        full_graph['attributes']['tools'] = list(set(full_graph['attributes']['tools']))
        full_graph['attributes']['variables'] = list(set(full_graph['attributes']['variables']))
        full_graph[coordinator_str] = list(set(full_graph[coordinator_str]))

        # Add holes in the graph as source functions
        hole_functions = self.find_all_nodes(category='function', subcategory='independent')
        for hole in hole_functions:
            full_graph[hole] = []
            full_graph['attributes']['tools'].append(hole)

        # Write log output
        logger.debug('Successfully created full_graph_data dictionary.')

        return full_graph

    def _get_edge_bundles_and_functions_data(self, full_graph):
        """ Function to get the lists for edge bundles and functions data.

        :param full_graph: full_graph dictionary
        :type full_graph: dict
        :return: edge bundles and functions data lists in a single tuple
        :rtype: tuple
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        # Create empty dictionary edge_bundles
        logger.debug('Creating edge_bundles_list and tools_data_list...')
        edge_bundles = dict(attributes=dict(tools=full_graph['attributes']['tools'],
                                                      variables=full_graph['attributes']['variables']))
        tools_data = dict(attributes=dict(tools=full_graph['attributes']['tools'],
                                                       variables=full_graph['attributes']['variables']))

        # Setting progress bar as this process takes some time
        n_keys = len(full_graph.keys())
        if logging.getLogger().getEffectiveLevel() in [logging.DEBUG, logging.INFO] and n_keys > 10000:
            n_key = 0
            logger.info('Looping through all nodes...')
            progress_bar = progressbar.ProgressBar(max_value=n_keys)
            progress_bar.start()

        for key in full_graph:
            if logging.getLogger().getEffectiveLevel() in [logging.DEBUG, logging.INFO] and n_keys > 10000:
                # noinspection PyUnboundLocalVariable
                progress_bar.update(n_key)
                n_key += 1
            if key is not 'attributes' and key is not coordinator_str:
                if self.node[key]['category'] == 'variable':
                    input_tools = full_graph[key]
                    # Extend tools_data with tool outputs
                    for input_tool in input_tools:
                        if input_tool not in tools_data:
                            tools_data[input_tool] = dict(name=format_string_for_vistoms(input_tool),
                                                          input=[],
                                                          output=[key])
                        else:
                            tools_data[input_tool]['output'].append(key)
                    # Create edge_bundles
                    for tool in full_graph['attributes']['tools']:
                        if key in full_graph[tool]:
                            if tool not in edge_bundles:
                                edge_bundles[tool] = dict(name=format_string_for_vistoms(tool), input=[],
                                                          pipeline_data=dict())
                            # Add input tools
                            edge_bundles[tool]['input'].extend(input_tools)
                            for input_tool in input_tools:
                                # Extend edge_bundles with pipeline data (variables passed between tools)
                                if input_tool not in edge_bundles[tool]['pipeline_data']:
                                    edge_bundles[tool]['pipeline_data'][input_tool] = []
                                edge_bundles[tool]['pipeline_data'][input_tool].append(key)
                    # Check if variable is also input to the coordinator
                    if key in full_graph[coordinator_str]:
                        if coordinator_str not in edge_bundles:
                            edge_bundles[coordinator_str] = dict(name=format_string_for_vistoms(coordinator_str),
                                                                 input=[],
                                                                 pipeline_data=dict())
                        # Add input tools to coordinator
                        edge_bundles[coordinator_str]['input'].extend(input_tools)
                        for input_tool in input_tools:
                            # Extend edge_bundles with pipeline data (variables passed between tools)
                            if input_tool not in edge_bundles[coordinator_str]['pipeline_data']:
                                edge_bundles[coordinator_str]['pipeline_data'][input_tool] = []
                            edge_bundles[coordinator_str]['pipeline_data'][input_tool].append(key)
                elif not self.node[key]['category'] == 'function':
                    raise NotImplementedError('Node category %s is not allowed.' % self.node[key]['category'])
            if key is not 'attributes':
                if key is coordinator_str:
                    if key not in tools_data:
                        tools_data[key] = dict(name=format_string_for_vistoms(key), input=full_graph[key],
                                               output=[])
                    else:
                        tools_data[key]['input'] = full_graph[key]
                elif self.node[key]['category'] == 'function':
                    if key not in tools_data:
                        tools_data[key] = dict(name=format_string_for_vistoms(key), input=full_graph[key],
                                               output=[])
                    else:
                        tools_data[key]['input'] = full_graph[key]
        if logging.getLogger().getEffectiveLevel() in [logging.DEBUG, logging.INFO] and n_keys > 10000:
            # noinspection PyUnboundLocalVariable
            progress_bar.finish()
            logger.info('Successfully looped through all nodes.')

        # Remove duplicates from the list
        for key, value in tools_data.iteritems():
            if 'output' in value:
                tools_data[key]['output'] = list(set(value['output']))
        for key, value in edge_bundles.iteritems():
            if 'input' in value:
                edge_bundles[key]['input'] = list(set(value['input']))
            if 'pipeline_data' in value:
                for subkey, subvalue in value['pipeline_data'].iteritems():
                    edge_bundles[key]['pipeline_data'][subkey] = list(set(subvalue))

        # Export edge_bundles dictionary to list
        edge_bundles_list = []
        for key in edge_bundles.iterkeys():
            if key is not 'attributes':
                edge_bundles_list.append(edge_bundles[key])

        # Export tools_data dictionary to list
        tools_data_list = []
        for key in tools_data.iterkeys():
            if key is not 'attributes':
                new_dict = tools_data[key]
                new_dict['type'] = 'function'
                tools_data_list.append(new_dict)

        logger.debug('Successfully created edge_bundles_list and tools_data_list.')

        return edge_bundles_list, tools_data_list

    def _get_xdsm(self, order, edge_bundles_list, mpg):
        """ Function to get the xdsm dictionary defintion for VISTOMS.

        :param order: function order
        :type order: list
        :param edge_bundles_list: data connections
        :type edge_bundles_list: list
        :param mpg: MDAO process graph
        :type mpg: MdaoProcessGraph
        :return: xdsm definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating xdsm...')
        xdsm_dict = dict(nodes=[], edges=[])

        # Add diagonal nodes
        for block in order:
            if block is not coordinator_str:
                if self.node[block]['category'] == 'function':
                    if 'architecture_role' in self.node[block]:
                        arch_role = self.node[block]['architecture_role']
                        if arch_role == self.ARCHITECTURE_ROLES_FUNS[0]:  # coordinator
                            block_type = 'coordinator'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[1]:  # optimizer
                            block_type = 'optimization'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[2]:  # converger
                            block_type = 'converger'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[3]:  # doe
                            block_type = 'doe'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[4]:  # pre-coupling analysis
                            block_type = 'precouplinganalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[5]:  # pre-iterator analysis
                            block_type = 'preiteratoranalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[6]:  # post-iterator analysis
                            block_type = 'postiteratoranalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[7]:  # coupled analysis
                            block_type = 'coupledanalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[8]:  # post-coupling analysis
                            block_type = 'postcouplinganalysis'
                        elif arch_role == self.ARCHITECTURE_ROLES_FUNS[9]:  # consistency constraint function
                            block_type = 'consistencyconstraintfunction'
                        else:
                            raise NotImplementedError('Architecture role %s not implemented.' % arch_role)
                    elif 'problem_role' in self.node[block]:
                        if self.node[block]['problem_role'] == self.FUNCTION_ROLES[0]:  # pre-coupling
                            block_type = 'precouplinganalysis'
                        elif self.node[block]['problem_role'] == self.FUNCTION_ROLES[1]:  # coupled
                            block_type = 'coupledanalysis'
                        elif self.node[block]['problem_role'] == self.FUNCTION_ROLES[2]:  # post-coupling
                            block_type = 'postcouplinganalysis'
                    else:
                        block_type = 'rcganalysis'
                    block_metadata = self.get_function_metadata(block)
                else:
                    raise Exception('Block category %s not supported.' % self.node[block]['category'])
            else:
                block_type = 'coordinator'
                block_metadata = [{'name': 'Coordinator'},
                                  {'description': 'Action block providing system inputs and collecting outputs.'},
                                  {'creator': 'Imco van Gent'}]
            # noinspection PyUnboundLocalVariable
            xdsm_dict['nodes'].append(dict(type=block_type,
                                           id=format_string_for_vistoms(block, prefix='id_'),
                                           name=format_string_for_vistoms(block),
                                           metadata=block_metadata))

        # Add edges between blocks
        for item in edge_bundles_list:
            name_keyword = ' couplings'
            if item['name'] is coordinator_str:
                to_node_id = format_string_for_vistoms(coordinator_str, prefix='id_')
                name_keyword = ' outputs'
            else:
                to_node_id = format_string_for_vistoms(item['name'], prefix='id_')
            for from_node in item['input']:
                if from_node is coordinator_str:
                    from_node_id = format_string_for_vistoms(coordinator_str, prefix='id_')
                    name_keyword = ' inputs'
                else:
                    from_node_id = format_string_for_vistoms(from_node, prefix='id_')
                if not to_node_id == from_node_id:  # check to avoid showing circular couplings on top of the diagonal
                    xdsm_dict['edges'].append({"to": to_node_id,
                                               "from": from_node_id,
                                               "name": ','.join(item['pipeline_data'][from_node]),
                                               "short_name": str(len(item['pipeline_data'][from_node])) + name_keyword})

        # Add workflow
        if mpg:
            xdsm_dict['workflow'] = mpg.get_process_list()
        else:
            xdsm_dict['workflow'] = []

        logger.debug('Successfully created xdsm.')
        return xdsm_dict

    def _get_variable_tree_dataschema(self, full_graph, reference_file):
        """ Function to determine the variable tree based on the data schema.

        :param full_graph: dictionary with graph data
        :type full_graph: dict
        :param reference_file: file with reference values
        :type reference_file: file
        :return: variable tree definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating schema variable tree...')

        variable_tree_dataschema = dict()
        if reference_file:
            # Parse reference XML
            reference_xml = etree.parse(reference_file)
            # Check validity of the CPACS file
            # noinspection PyUnusedLocal
            reference_valid = recursively_unique_attribute(reference_xml)
        for key in full_graph:
            if key is not 'attributes' and key is not coordinator_str:
                if self.node[key]['category'] == 'variable':
                    # Determine element element value and dimension based on reference file
                    if reference_file:
                        # Check if the variable node is actually a related node
                        if 'related_to_schema_node' in self.node[key]:
                            xpath = self.node[key]['related_to_schema_node']
                        else:
                            xpath = key
                        # Get element details
                        # noinspection PyUnboundLocalVariable
                        var_value, var_dim = get_element_details(reference_xml, xpath)
                    else:
                        var_value = 'unknown'
                        var_dim = None
                    var_dict = get_element_dict(key, var_value, var_dim, include_reference_data=True)
                    variable_tree_dataschema = merge(variable_tree_dataschema, var_dict)
        logger.debug('Successfully created schema variable tree.')
        return variable_tree_dataschema

    def _get_variable_tree_categorized_system_level(self, full_graph):
        """ Function for system level sorting of the variables (inputs, outputs, couplings, holes)

        :param full_graph: dictionary with graph data
        :type full_graph: dict
        :return: variable tree definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating system level categorized variable tree...')

        variable_tree_categorized_system_level = dict()
        for key in full_graph:
            if key is not 'attributes' and key is not coordinator_str:
                if self.node[key]['category'] == 'variable':
                    in_degree = self.in_degree(key)
                    out_degree = self.out_degree(key)
                    if in_degree == 0 and out_degree > 0:
                        key = '/systemVariables/inputs' + key
                    elif in_degree > 0 and out_degree > 0:
                        key = '/systemVariables/couplings' + key
                    elif in_degree > 0 and out_degree == 0:
                        key = '/systemVariables/outputs' + key
                    else:
                        key = '/systemVariables/holes' + key
                    var_dict = get_element_dict(key)
                    variable_tree_categorized_system_level = merge(variable_tree_categorized_system_level, var_dict)
        logger.debug('Successfully created system level categorized variable tree.')
        return variable_tree_categorized_system_level

    def _get_variable_tree_categorized_node_level(self, full_graph):
        """ Function for system level sorting of the variables (inputs, outputs, couplings, holes)

        :param full_graph: dictionary with graph data
        :type full_graph: dict
        :return: variable tree definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating node level categorized variable tree...')
        variable_tree_categorized_node_level = dict()
        for key in full_graph:
            if key is not 'attributes' and key is not coordinator_str:
                if self.node[key]['category'] == 'variable':
                    subcategory = self.node[key]['subcategory']
                    key = '/variables/' + make_camel_case(subcategory) + key
                    var_dict = get_element_dict(key)
                    variable_tree_categorized_node_level = merge(variable_tree_categorized_node_level, var_dict)
        logger.debug('Successfully created node level categorized variable tree.')
        return variable_tree_categorized_node_level

    def _get_variable_tree_categorized_role_level(self, full_graph):
        """ Function for system level sorting of the variables (inputs, outputs, couplings, holes)

        :param full_graph: dictionary with graph data
        :type full_graph: dict
        :return: variable tree definition
        :rtype: dict
        """

        # Settings
        coordinator_str = self.COORDINATOR_STRING

        logger.debug('Creating role level categorized variable tree...')
        variable_tree_categorized_role_level = dict()
        # Create empty start tree
        key = '/variables/architectureRoles'
        var_dict = get_element_dict(key)
        variable_tree_categorized_role_level = merge(variable_tree_categorized_role_level, var_dict)
        key = '/variables/problemRoles'
        var_dict = get_element_dict(key)
        variable_tree_categorized_role_level = merge(variable_tree_categorized_role_level, var_dict)
        for key in full_graph:
            if key is not 'attributes' and key is not coordinator_str:
                if self.node[key]['category'] == 'variable':
                    if 'problem_role' in self.node[key]:
                        prob_role = self.node[key]['problem_role']
                        new_key = '/variables/problemRoles/' + make_camel_case(prob_role) + 's' + key
                        var_dict = get_element_dict(new_key)
                        variable_tree_categorized_role_level = merge(variable_tree_categorized_role_level, var_dict)
                    if 'architecture_role' in self.node[key]:
                        arch_role = self.node[key]['architecture_role']
                        new_key = '/variables/architectureRoles/' + make_camel_case(arch_role) + 's' + key
                        var_dict = get_element_dict(new_key)
                        variable_tree_categorized_role_level = merge(variable_tree_categorized_role_level, var_dict)
        logger.debug('Successfully created role level categorized variable tree.')
        return variable_tree_categorized_role_level

    def _get_variable_tree_categorized_function_level(self, function_data_list):
        """ Function for function level sorting of variables (inputs / outputs per function)

        :param function_data_list: list with function-based inputs and outputs
        :type function_data_list: list
        :return: variable tree definition
        :rtype: dict
        """

        logger.debug('Creating function level categorized variable tree...')
        variable_tree_categorized_function_level = dict()
        for item in function_data_list:
            name = item['name']
            inputs = item['input']
            outputs = item['output']
            for inp in inputs:
                key = '/functions/' + name + '/inputs' + inp
                var_dict = get_element_dict(key)
                variable_tree_categorized_function_level = merge(variable_tree_categorized_function_level, var_dict)
            for output in outputs:
                key = '/functions/' + name + '/outputs' + output
                var_dict = get_element_dict(key)
                variable_tree_categorized_function_level = merge(variable_tree_categorized_function_level, var_dict)
        logger.debug('Successfully created function level categorized variable tree...')
        return variable_tree_categorized_function_level


def vistoms_remove(graph_id, vistoms_dir, compress=False, remove_after_compress=True):
    """ Function to remove a graph from a VISTOMS instance.

    :param graph_id: ID of the graph to be removed
    :type graph_id: str
    :param vistoms_dir: folder of the existing VISTOMS instance
    :type vistoms_dir: str
    :param compress: setting whether to compress the final VISTOMS instance folder to a zip file
    :type compress: bool
    :param remove_after_compress: setting whether to remove the original folder after compression
    :type remove_after_compress: bool
    :return: updated VISTOMS instance
    :rtype: file
    """
    # Logging
    logger.info('Removing graph from the VISTOMS instance...')

    # Create vistoms file name path
    vistoms_file = os.path.join(vistoms_dir, VISTOMS_NAME)

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    # Copy VISTOMS_NAME file to the temp directory
    temp_file = os.path.join(temp_dir, VISTOMS_NAME)
    shutil.copy(vistoms_file, temp_file)

    # Get the graph data and line number
    data, data_linenumber = _get_the_data(temp_file)

    # Find IDs in the current graph data.json
    graph_ids = [graph['id'] for graph in data['graphs']]
    assert graph_id in graph_ids, 'Could not find graph_id: %s. Available IDs: %s.' % \
                                  (graph_id, graph_ids)
    removal_index = graph_ids.index(graph_id)

    # Remove graph from the data dictionary
    data['graphs'].pop(removal_index)

    # Replace the graph data
    data_str = json.dumps(data)
    _replace_line(temp_file, data_linenumber, THEDATA_PREFIX + data_str)

    # Copy VISTOMS_NAME to original folder
    # Remove previous VISTOMS_NAME
    try:
        os.remove(vistoms_file)
    except OSError:
        pass
    # Place new VISTOMS_NAME file
    os.rename(temp_file, vistoms_file)
    # Remove temporary directory
    shutil.rmtree(temp_dir)

    if compress:
        _compress_vistoms_instance(vistoms_dir, remove_after_compress)

    # Logging
    logger.info('Successfully removed graph from the VISTOMS instance.')

    return


def vistoms_get_graph_ids(vistoms_dir):
    """ Function to get a list with current graph IDs in a VISTOMS file.

    :param vistoms_dir: path to the VISTOMS folder
    :type vistoms_dir: basestring
    :return: list with graph IDs
    :rtype: list
    """

    # Create vistoms file name path
    vistoms_file = os.path.join(vistoms_dir, VISTOMS_NAME)

    # Get the graph data and line number
    data, data_linenumber = _get_the_data(vistoms_file)

    # Find IDs in the current graph data
    graph_ids = [graph['id'] for graph in data['graphs']]

    return graph_ids


def vistoms_get_graph_info(vistoms_dir):
    """ Function to retrieve the graph information from a VISTOMS file.

    :param vistoms_dir: path to the VISTOMS folder
    :type vistoms_dir: basestring
    :return: dictionary with graph info
    :rtype: dict
    """

    # Create vistoms file name path
    vistoms_file = os.path.join(vistoms_dir, VISTOMS_NAME)

    # Get the graph data and line number
    data, data_linenumber = _get_the_data(vistoms_file)

    # Find info in the current graph data
    graph_ids = [graph['id'] for graph in data['graphs']]
    graph_names = [graph['name'] for graph in data['graphs']]
    graph_descriptions = [graph['description'] for graph in data['graphs']]

    # Build dictionary
    graph_dict = dict()
    for graph_id, graph_name, graph_description in zip(graph_ids, graph_names, graph_descriptions):
        graph_dict[graph_id] = dict(name=graph_name, description=graph_description)

    return graph_dict


def get_vistoms_tree_viewer(xml_file, vistoms_dir, use_png_figs=False, file_refs=None):

    # Create temporary directory
    temp_dir = tempfile.mkdtemp()

    # Get absolute path of vistoms_dir
    vistoms_dir = os.path.abspath(vistoms_dir)

    # Initiate VISTOMS instance
    vispack.copy(temp_dir, vispack_version="TreeViewer")

    # Settings
    dummy_tool_name = '__dummy__'
    dummy_cmdows_name = '__dummy__CMDOWS.xml'
    dummy_input_file_name = dummy_tool_name + '-input.xml'

    # File names
    dummy_cmdows_file = os.path.join(temp_dir, dummy_cmdows_name)
    dummy_input_file = os.path.join(temp_dir, dummy_input_file_name)

    # create dummy CMDOWS (done to get full_graph data)
    cmdows = CMDOWS()
    cmdows.add_header(creator='VISTOMS', description='CMDOWS for VISTOMS TreeViewer creation')
    cmdows.add_dc(dummy_tool_name, dummy_tool_name, 'main', 1, '1.0', dummy_tool_name)

    cmdows.save(dummy_cmdows_file, pretty_print=True)

    # rename merged_basefile as input file
    shutil.copyfile(xml_file, dummy_input_file)

    # read file as an RCG with load function
    from kadmos.graph import load
    graph = load(dummy_cmdows_file, 'cmdows', file_check_critical=False, ignore_modes=True)

    full_graph = graph._get_full_graph()

    variable_tree_dataschema = graph._get_variable_tree_dataschema(full_graph,
                                                                   reference_file=dummy_input_file)

    the_data = {"modelName": "Tree view of latest baseline file.",
                "schema": variable_tree_dataschema}
    data_str = json.dumps(the_data)

    # Define string replacements based on file referencing
    if file_refs is None:
        rep = dict(LOCAL_FILE_REFS)
        if use_png_figs:
            for key, item in rep.iteritems():
                if '.svg' in item:
                    rep[key] = item.replace('.svg', '.png')
        rep['REP__GRAPH_DATA__REP'] = data_str
    else:
        rep = file_refs
        for key, item in LOCAL_FILE_REFS.iteritems():
            assert key in rep, 'Replacement key %s is missing in the file_refs.' % key
        rep['REP__GRAPH_DATA__REP'] = data_str

    # Perform the text replacement
    rep = dict((re.escape(k), v) for k, v in rep.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    with open(os.path.join(temp_dir, "VISTOMS_TreeViewer_datarepl.html"), "rt") as fin:
        with open(os.path.join(temp_dir, VISTOMS_TV_NAME), "wt") as fout:
            for line in fin:
                fout.write(pattern.sub(lambda m: rep[re.escape(m.group(0))], line))

    # Remove the original VISTOMS file
    os.remove(os.path.join(temp_dir, 'VISTOMS_TreeViewer_datarepl.html'))

    # Remove the dummy files
    os.remove(dummy_cmdows_file)
    os.remove(dummy_input_file)

    # Copy temp directory to file path
    # Remove previous VISTOMS directory (if present)
    try:
        shutil.rmtree(vistoms_dir)
    except OSError:
        pass
    # Place new VISTOMS folder
    shutil.copytree(temp_dir, vistoms_dir)
    # Remove temporary directory
    shutil.rmtree(temp_dir)


def _write_json_file(vistoms_dir, data_json):
    """ Function to write the data.json file and first remove the previous one.

    :param vistoms_dir: location of VISTOMS instance
    :type vistoms_dir: str
    :param data_json: dictionary with all graph data
    :type data_json: dict
    :return: data.json file
    :rtype: file
    """

    # Write data.json file
    dst = os.path.join(vistoms_dir, 'supportFiles', 'data.json')
    try:
        os.remove(dst)
    except OSError:
        pass
    with open(dst, 'w') as f:
        json.dump(data_json, f)


def _compress_vistoms_instance(vistoms_dir, remove_original):
    """ Function to compress the VISTOMS instance with option to remove original folder.

    :param vistoms_dir: location of VISTOMS instance
    :type vistoms_dir: str
    :param remove_original: option to
    :type remove_original:
    :return: compressed VISTOMS instance
    :rtype: file
    """

    shutil.make_archive(vistoms_dir, 'zip', vistoms_dir)
    if remove_original:
        shutil.rmtree(vistoms_dir)


def _replace_line(file_name, line_num, text):
    lines = open(file_name, 'r').readlines()
    lines[line_num-1] = text + '\n'
    out = open(file_name, 'w')
    out.writelines(lines)
    out.close()


def _get_the_data(vistoms_file):
    """
    Function to read the graph data dictionary from a VISTOMS html file.

    :param vistoms_file: the existing VISTOMS html file
    :type vistoms_file: basestring
    :return: dictionary with the graph data
    :rtype: dict
    """

    # Find the line number of the Data
    thedata_linenumber = None
    with open(vistoms_file) as myFile:
        for num, line in enumerate(myFile, 1):
            if THEDATA_PREFIX in line:
                thedata_linenumber = num
    assert thedata_linenumber is not None, 'Could not find THEDATA_PREFIX string in the html file.'

    # Read data from the VISTOMS_NAME file
    data_line = linecache.getline(vistoms_file, thedata_linenumber)
    data_str = data_line.replace(THEDATA_PREFIX, '')
    data = json.loads(data_str)
    return data, thedata_linenumber
