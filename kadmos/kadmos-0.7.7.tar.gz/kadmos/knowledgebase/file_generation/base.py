import os
import datetime
import json
import copy
import shutil
from lxml import etree
import matlab.engine as ME

import kadmos.utilities.mapping as MU
import kadmos.utilities.prompting as PRO
import kadmos.utilities.printing as PRI
import kadmos.utilities.executing as EX

class Base_file_generator():
    """
    This class contains methods to generate Basefiles according to the provided MDO Problem Graph (MPG) and tool
    sequence.
    """


    def __init__(self, graph, schema_files_dir_path, print_details=True):

        self.graph = graph
        self.schema_files_dir_path = schema_files_dir_path
        self.print_details = print_details


    def generate_basefile(self, tool_order, spec_files_dir_path, basefile_name = None):
        """
        This function generates a Basefile by executing the functions in the MPG according to the provided sequence.
        The outputs of each tool execution are saved to the Basefile.

        :param tool_order:
        :param spec_files_dir_path:
        :param basefile_name:
        :return:
        """

        # add to class attribs for easier access
        self.tool_order = tool_order
        self.spec_files_dir_path = spec_files_dir_path
        self.basefile_name = basefile_name

        # copy schema file
        self.copy_schema_file(spec_files_dir_path)

        # print init
        msg = "Basefile generation initiated for tool sequence: {}".format(self.tool_order)
        print "\n\n{1}\n{0}\n{1}".format(msg, "~"*(len(msg)+1))

        # load schema and info files
        self.schemaTreeDict = EX.parse_schematic_io_files(self.graph, self.tool_order, self.schema_files_dir_path)

        # load and check mapping_dict for completeness
        self.mapping_dict = EX.load_mapping_dict(self.schema_files_dir_path, self.schemaTreeDict)


        # check for System Inputs
        self.check_graph_for_system_inputs(ignore_toolspecific=True)

        # create base file in specific files dir
        if self.basefile_name is None:
            self.basefile_name = os.path.basename(self.spec_files_dir_path)
        self.basefile_path = EX.create_cpacs_basefile(self.spec_files_dir_path, self.basefile_name)
        self.baseTree = etree.parse(self.basefile_path)

        # execute tool sequence, write outputs to Basefile
        self.run_tool_sequence()

        return self.basefile_path


    def copy_schema_file(self, target_dir):
        """
        Copies .xsd file to target path.

        :param target_path:
        :return:
        """

        for item in os.listdir(self.schema_files_dir_path):
            if item.endswith(".xsd"):
                item_path = os.path.join(self.schema_files_dir_path, item)
                item_target = os.path.join(target_dir, item)
                if not os.path.exists(item_target):
                    shutil.copy(item_path, item_target)  # copy file to target path
                else:
                    print "NOTE: XML-schema already exists in target paths."


    def check_graph_for_system_inputs(self, ignore_toolspecific=True):
        """
        This function checks whether there are System Inputs present in the graph and prints them to the console,
        ordered by tool. If present, user is asked whether to continue or not.

        :param ignore_toolspecific:
        :return:
        """

        # check whether input nodes are NOT produced any by tools in workflow, i.e. design variables exist
        systemInputNodes = self.graph.get_system_inputs(*self.tool_order, ignore_toolspecific=ignore_toolspecific)

        # print design variables and let user decide whether to continue (may want to add tools or so)
        if systemInputNodes:
            print "\nThe following System Inputs have been found in the workflow:"
            pList = list(sorted(systemInputNodes.items(), key=lambda x: x[1]))
            PRI.print_in_table(pList, headers=["Xpath", "Tools"], print_indeces=True)

            msg = "Would you like to continue? "
            yn_sel = PRO.user_prompt_yes_no(message=msg) # TODO:DEMO
            # yn_sel = 1

            if not yn_sel:
                return None
        else:
            print "\nNOTE: No System Inputs found in graph."


    def run_tool_sequence(self):
        """
        This function runs the tool sequence and executes the tools in the specified order. Before a tool is executed,
        the Basefile is checked whether nodes are missing according to the schematic tree. When the nodes are added and
        the Basefile is rendered executable, the tool is run. If an error occurs, the procedure is repeated or the
        execution canceled.

        :return:
        """

        # loop through tool sequence, execute tools and generate Basefile
        for fnode in self.tool_order:

            # get tool name and execution mode
            tool = self.graph.node[fnode]['name']
            mode = self.graph.node[fnode]['mode']
            toolspec_elem = self.graph.node[fnode]['toolspecific']

            # print exection message
            print "\n\nTool Execution: {0}[{1}]\n{2}".format(tool, mode, "-" * (len(tool + mode) + 19))

            # copy toolspecific nodes from schema tree to basefile; filter tree by modes
            inputSchemaTree = self.schemaTreeDict[(tool, mode)]['input']
            self.baseTree = MU.copy_toolspecific_elements_to_tree(self.baseTree,
                                                                  inputSchemaTree,
                                                                  toolspec_elem,
                                                                  overwrite_if_exist=True,
                                                                  nodes_valued=True)
            MU.write_xml_tree_to_file(self.baseTree, self.basefile_path)

            # add missing nodes to Basefile and run tool
            # while loop ensures execution until forced stop or success
            while True:

                # add missing nodes to tree and ensure basefile is executable
                execTree = self.ensure_basefile_executable(inputSchemaTree, tool, mode)

                # execute the tool until
                try:
                    output_file_path = EX.execute_tool(tool, mode, execTree)
                    break

                # if execution fails, print errer and ask whether to repeat
                except ME.MatlabExecutionError as err:  # TODO: will error be raised here? check if placement appropriate

                    print "The failed to execute due to the following error: \n", str(err)
                    repeat_msg = "Would you like to repeat the process?"
                    rep_sel = PRO.user_prompt_yes_no(message=repeat_msg)
                    if rep_sel:
                        continue
                    else:
                        return

            # write execTree to Basefile path; written to path AFTER execution to ensure validity
            outputTree = etree.parse(output_file_path)
            self.baseTree = MU.merge_XML_trees_by_UID(execTree, outputTree)  # careful with sequence: 1st pos dominant?
            MU.write_xml_tree_to_file(self.baseTree, self.basefile_path)

            # print execution complete
            print "\nTool execution completed; output successfully written to Basefile."


    def ensure_basefile_executable(self, inputSchemaTree, tool, mode):
        """
        This function add missing nodes too the basefile and checks references/dependencies/links between nodes in
        the Basefile to ensure validitiy.

        :return:
        """

        # make copy of Basetree for tool execution; make execTree the new Basetree if execution is successful!
        execTree = copy.deepcopy(self.baseTree)

        # get paths in basetree and schemaTree; get nodes that are not in basetree
        execTreePaths = MU.get_xpaths_in_element_tree(execTree, leaf_nodes=True)
        schemaPaths = MU.get_xpaths_in_element_tree(inputSchemaTree, apply_modes=[mode], leaf_nodes=True)

        # get missing schematic nodes
        # missingSchemaNodes = [x for x in schemaPaths if x not in execTreePaths]
        missingSchemaNodes = schemaPaths - execTreePaths # faster?

        # if nodes are missing, add nodes for temporarily tool execution (permanently if System Input)
        if missingSchemaNodes:

            # print missing nodes
            print "\nThe following nodes are missing for execution of {}[{}]:".format(tool, mode)
            print "-" * 3
            for node in sorted(missingSchemaNodes):
                print node
            print "-" * 3

            # let user decide whether to continue
            cont_msg = "Continue?"
            yn_sel = PRO.user_prompt_yes_no(message=cont_msg)
            if not yn_sel:
                return

            # check whether basetree has UID-items that refer to missing nodes
            # the reference UIDs (links) are onnly checked for the nodes applying to the tool's schema!
            refUIDs = {}
            checkPaths = MU.get_xpaths_in_element_tree(inputSchemaTree, apply_modes=[mode], leaf_nodes=False)
            checkTree = MU.filter_tree_by_xpaths(execTree, checkPaths)

            for path in missingSchemaNodes:
                refUIDs = MU.get_applied_uids_by_path(self.mapping_dict, checkTree, path, refUIDs)

            # add nodes missing nodes to tree
            execTree = MU.add_nodes_to_tree(self.mapping_dict, execTree, missingSchemaNodes, self.spec_files_dir_path, refUIDs)

        # initiate list for unlinked UID-items (non-existing elements referenced)
        self.noLink = []

        # check dependency on added nodes first; may not have all necessary info
        for xpath in missingSchemaNodes:
            execTree = self.check_node_dependencies(self.mapping_dict, execTree, xpath)

        # check dependency on toolspecific nodes
        toolspec_schema_paths = [p for p in schemaPaths if "toolspecific" in p]
        for xpath in toolspec_schema_paths:
            execTree = self.check_node_dependencies(self.mapping_dict, execTree, xpath)

        # check schema leaf paths in Basefile
        for xpath in schemaPaths:
            execTree = self.check_node_dependencies(self.mapping_dict, execTree, xpath)
            # TODO: SHOULD ALL INPUT VARS BE CHECKED OR SHOULD CORRECTNESS BE RELIED UPON BY TOOL (future implementation should check ALL nodes to assert file validity/consistency)?

        # print unlinked items
        if self.noLink and self.print_details:
            msg = "WARNING: The following input UID-items (links) do not refer to any existing elements:"
            PRI.print_in_table(self.noLink, headers=["uID-item (link)", "Value"], message=msg, print_indeces=True)
        pass

        return execTree


    def check_node_dependencies(self, mapping_dict, tree, path):
        """
        This function checks the dependencies of the elements in the tree that correspond to the provided xpath. First, the
        element is checked whether it is a UID-item (leaf element with 'UID' in its tag, referring to a UID-elelemt) and
        whether it refers to an existing UID-element. Second, all its ancestors are iterated over to ensure they have the
        'uID'-attribute if they are UID-elements (its presence in the mapping-dict is checked).

        :param mapping_dict: dictionary mapping UID-items to UID-elements
        :param tree: element tree
        :param path: xpath of element
        :return:
        """

        # get search path; find elements that path refers to
        search_path = MU.xpath_to_searchpath(path)
        elementsFound = tree.findall(search_path)

        # check whether elements are UID-items
        if elementsFound:
            for elem in elementsFound:

                # if element is UID-item, perform item-mapping and check whether UID corresponds to UID-element
                if MU.element_is_UID_item(elem):
                    tree = self.ensure_UID_item_validity(tree, elem)

                # loop ancestors; check whether they are UID-elements and whether they have UID.
                for anc in elem.iterancestors():

                    # check if ancestor is UID-element
                    ancPath = MU.xpath_to_clean_xpath(tree.getpath(anc))

                    # if UID-element, make sure that UID is present
                    if ancPath in mapping_dict.values():
                        tree = self.ensure_UID_element_validity(mapping_dict, tree, anc)

        else:  # if no elements found
            print "WARNING: No elements in tree with xpath {} for dependency check.".format(path)

        return tree

    def ensure_UID_item_validity(self, tree, uid_item):
        """
        This function ensures that the UID-item refers to an existing UID-element (text-value of UID-item must correspond
        to the 'uID'-attribute of a UID-element). If no UID-element can be found that corresponds to UID-item value, the
        user is asked to:
        [1] change UID-item text-value (if other UID-elements exist),
        [2] add UID-element according to schema

        :param mapping_dict: dictionary that carries [UID-item --> UID-element] mappings
        :param tree: element tree
        :param uid_item: element in tree that carries a UID value
        :return:
        """

        # get item xpath and return mappend UID-elements
        cleanPath = MU.xpath_to_clean_xpath(tree.getpath(uid_item))
        itemPath = MU.xpath_to_uid_xpath(cleanPath, uid_item)
        uid_elements = MU.map_UID_item(self.mapping_dict, tree, cleanPath)

        # if elements found, check whether any matches this UID-item value
        if uid_elements:

            # check whether UID matches one of the mapped elements
            uid_dict = {e.get("uID"): MU.xpath_to_uid_xpath(tree.getpath(e), e) for e in uid_elements}
            if uid_item.text not in uid_dict:

                # let user decide what to do
                if len(uid_dict) > 1:

                    # get list of tuples [(xpath, uid),...]
                    elemPaths = [(v, k) for k, v in uid_dict.iteritems()]

                    # print list and ask user which UID to apply
                    pr_msg = "The UID-item '{}' with value '{}' does not match any of the following elements:".format(
                        itemPath, uid_item.text)  # following UID-elements are referred to
                    PRI.print_in_table(elemPaths, headers=["Xpath", "uID"], print_indeces=True, message=pr_msg)
                    sel_msg = "Please select one 'uID' is applied to UID-item:"
                    uid_sel = PRO.user_prompt_select_options(*elemPaths, message=sel_msg, allow_empty=True,
                                                             allow_multi=False)

                    # apply selected UID to UID-item
                    if uid_sel:
                        uid_item.text = next(iter(uid_sel))[1]
                        print "\nNOTE: '{}' has been applied to element '{}'.".format(uid_item.text, itemPath)
                    else:
                        self.noLink.append((itemPath, uid_item.text))

                else:
                    # get only possible element
                    mapUID = next(iter(uid_dict))
                    pr1 = "\nWARNING: UID-item '{}' with value '{}' maps to element:".format(itemPath, uid_item.text)
                    pr2 = "{} with uID={}".format(uid_dict[mapUID], mapUID)
                    print "{}\n{}".format(pr1, pr2)

                    # prompt user on what to do with mismatched UID-item value
                    msg = "What would you like to do?"
                    opt = ["Keep UID-item value", "Replace UID-item value"]
                    PRI.print_indexed_list(*opt, message=msg),
                    sel = PRO.user_prompt_select_options(*range(len(opt)), message='\n', allow_empty=False,
                                                         allow_multi=False)

                    # execute user choice
                    if sel == 0:  # keep uid-value
                        self.noLink.append((itemPath, uid_item.text))
                        # TODO: PROBLEM >> if element is referred to that is not missing, nodes should be added according to refUIDs

                    else:  # replace uid-value
                        uid_item.text = mapUID
                        print "\nNOTE: '{}' has been applied to element '{}'.\n".format(mapUID, itemPath)

        else:  # if no mapped elements found
            self.noLink.append((itemPath, uid_item.text))
            # NOTE: in this case, the fact that the UID-item refers to a non-existent element, is ignored

        return tree


    def ensure_UID_element_validity(self, mapping_dict, tree, uid_element):
        """
        This function checks whether the UID-element has a defined 'uID'-attribute. If not, user is asked to either provide
        a UID manually, or select a UID from UID-items that refer to this element.

        :param mapping_dict:
        :param tree:
        :param uid_element:
        :return:
        """

        elemPath = MU.xpath_to_clean_xpath(tree.getpath(uid_element))

        # if UID-element does not have a UID, choose from elements that refer to it OR ask user to define it
        if uid_element.get('uID') is None:

            # map UID-element to UID-item and retrieve UID's (reverse mapping)
            uid_items = MU.map_UID_element(mapping_dict, tree, elemPath)
            uids = set(i.text for i in uid_items)

            # make sure UID is added
            while True:

                # check if user wants to provide UID manually or not
                manual = True
                if uid_items:
                    msg = "\nWARNING: Element '{}' does not have a UID. Would you like to provide it manually?".format(
                        elemPath)
                    manual = PRO.user_prompt_yes_no(message=msg)
                    if manual:
                        print "Please provide UID: \n"
                else:
                    print "\nWARNING: Element '{}' does not have a UID. Please provide UID: \n".format(elemPath)
                    # TODO: apply existing UID, make user select if multiple exist

                    # prompt user to provide UID
                if manual:
                    sel_uid = PRO.user_prompt_string()
                else:
                    idx_msg = "The following UIDs have been found to refer to this element:"
                    PRI.print_indexed_list(*uids, message=idx_msg)
                    pr_msg = "Please select one:"
                    sel_uid = PRO.user_prompt_select_options(*uids, message=pr_msg, allow_empty=False,
                                                             allow_multi=False)

                # leave loop if uid is selected/provided
                if sel_uid:
                    break

            # set 'uID' attribute to selected UID
            uid_element.set('uID', next(iter(sel_uid)))

        return tree

