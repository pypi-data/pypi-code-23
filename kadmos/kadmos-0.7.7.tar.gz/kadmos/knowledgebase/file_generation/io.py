from lxml import etree
import copy
import shutil
import os
import re
import collections
import kadmos.utilities.prompting as PRO
import kadmos.utilities.mapping as MU
import kadmos.utilities.printing as PRI
import kadmos.utilities.executing as EX


class IO_file_generator(object):
    """
    This class is used to generate XML input and output tree using an existing (base)tree. The tree can then be written
    to a file and saved to a knowledge base. A mapping dict is used to check and ensure node references throughout the
    tree.
    """

    def __init__(self, graph, basefile_path, schema_files_dir_path, print_details=False):

        self.graph = graph
        self.basefile_path = basefile_path
        self.schema_files_dir_path = schema_files_dir_path
        self.print_details = print_details
        self.base_tree = etree.parse(self.basefile_path)


    def generate_io_files(self, tool_order, spec_files_dir_path):
        """
        This function generates the input/output files for a given Basefile.

        :param tool_order:
        :param spec_files_dir_path:
        :return:
        """

        self.spec_files_dir_path = spec_files_dir_path
        self.tool_order = tool_order

        # print init
        msg = "I/O-file generation initiated for tool sequence: {}".format(self.tool_order)
        print "\n\n{1}\n{0}\n{1}".format(msg, "~" * (len(msg) + 1))

        # load schema and info files
        self.schemaTreeDict = EX.parse_schematic_io_files(self.graph, self.tool_order, self.schema_files_dir_path)

        # load and check mapping_dict for completeness
        self.mapping_dict = EX.load_mapping_dict(self.schema_files_dir_path, self.schemaTreeDict)

        # loop through tools and generate input and output files
        for func in tool_order:

            # get tool name and execution mode
            tool = self.graph.node[func]['name']
            mode = self.graph.node[func]['mode']
            toolspec_elem = self.graph.node[func]['toolspecific']
            print "\nGenerating case-specific IO-files for {}[{}]...".format(tool, mode)

            # generate input and output file for each tool
            for io in ["input", "output"]:
                self.generate_file(io, tool, mode, toolspec_elem)

        print "\nNOTE: Case-specific I/O-files generated and written to {}.".format(spec_files_dir_path)


    def generate_file(self, io, tool, mode, toolspec):
        """
        This function generates the input or output file for a specific tool and mode.

        :param io:
        :param tool:
        :param mode:
        :param toolspec:
        :return:
        """

        # check whether info-file present in use-case dir; otherwise copy from schematic
        info_file = "{}-info.json".format(tool)
        info_target = os.path.join(self.spec_files_dir_path, info_file)
        if not os.path.exists(info_target):
            info_source = os.path.join(self.schema_files_dir_path, info_file)
            shutil.copy(info_source, info_target)  # copy file to target path

        # get target path; check whether file already exists
        ioFile = "{tool}-{io}.xml".format(tool=tool, io=io)
        targetPath = os.path.join(self.spec_files_dir_path, ioFile)
        targetTree = None
        if os.path.exists(targetPath):
            targetTree = etree.parse(targetPath)

        # get schema input or output tree
        schemaTree = self.schemaTreeDict[(tool, mode)][io]

        # perform file generation
        ioTree = self._extract_io_tree(schemaTree, mode, toolspec)

        # if tool file already exists, merge trees
        if targetTree:
            targetTree = MU.merge_XML_trees_by_UID(targetTree, ioTree)
            # TODO: check whether tree merge overwrites the wrong tree attribs; target should be prioritized
        else:
            targetTree = ioTree

        # iterate all schema nodes and check if MODES-attrib present
        # if present, add mode to target tree
        # since modes-search follows the schema-file, a simple search for corresponding elements is enough
        # (no need to check ancestors or descendants for modes)
        for node in schemaTree.iter():
            if node.get("modes") and mode in node.get("modes"):
                searchPath = MU.xpath_to_searchpath(schemaTree.getpath(node))
                foundElems = targetTree.findall(searchPath)

                # get all related elements and add mode
                for elem in foundElems:
                    if elem.get("modes"):  # if exists, add to existing
                        modesList = elem.get("modes").split()
                        if mode not in modesList:
                            modesList.append(mode)
                        modesComb = " ".join(modesList)
                        elem.set("modes", modesComb)
                    else:
                        elem.set("modes", mode)

        # write to tree
        MU.write_xml_tree_to_file(targetTree, targetPath)


    def _extract_io_tree(self, schema_tree, execution_mode, toolspec_node):
        """
        (PRIVATE) This function extracts the input or output tree from the provided base-tree. The corresponding schema-tree is
        used to check for the nodes to keep in the target tree. The steps for the generation are as follows:

        [1] Apply Schematic Nodes
        [2] Check 'toolspecific' for uID-references/dependencies
        [3] Auto-Check UID-Items [removed this step]
        [4] Check dependencies in tree
        [5] Remove irrelevant nodes from tree

        :param schema_tree:
        :param execution_mode:
        :param toolspec_node:
        :return:
        """

        # initiate keep set and remove sets
        self.keepElements = set([])
        self.removeElements = set([])

        # make target tree and create copy of original base-file (for later checks)
        targetTree = copy.deepcopy(self.base_tree)
        cBaseTree = copy.deepcopy(self.base_tree) # not sure if needed

        # apply schematic nodes; strip target tree off of unneeded nodes
        targetTree = self._apply_schematic_nodes(targetTree, schema_tree, execution_mode)

        # iterate through toolspecific nodes and check for node references/dependencies
        # remove all KEEP elements from REMOVE-set, then remove elements
        addKeep, addRemove = self._check_toolspecific(targetTree, toolspec_node)
        self.keepElements = self.keepElements.union(addKeep)
        rem = set(elem for elem in addRemove if elem not in self.keepElements)
        self.removeElements = self.removeElements.union(rem)
        MU.remove_elements_from_tree(*rem)

        # check references/links within the target tree to get elements to remove
        addKeep, addRemove = self._check_node_references(targetTree)
        self.keepElements = self.keepElements.union(addKeep)
        rem = set(elem for elem in addRemove if elem not in self.keepElements)
        MU.remove_elements_from_tree(*rem)

        # dirty way to solve problem with some elements remaining in tree
        # >> remove all empty leaf elements
        empty_found = True
        # removeEmpty = []
        while empty_found:
            empty_found = False
            for elem in targetTree.iter():
                if not elem.getchildren():
                    if re.search("[a-zA-Z0-9]+", elem.text) is None : # TODO: THIS SHOULD CHECK FOR ALPHANUMERIC CHARACTERS!
                        MU.remove_elements_from_tree(elem)
                        empty_found = True

        return targetTree


    def _apply_schematic_nodes(self, target_tree, schema_tree, exec_mode):
        """
        (PRIVATE) This function compares the nodes in the schematic tree to the nodes in the target tree and removes "unmatched"
        elements from the target tree. This leaves the target with a set of elements as described by schematic tree,
        but node multiplicities may still exist.

        :param target_tree:
        :param schema_tree:
        :param exec_mode:
        :return:
        """

        # create set of "clean" element paths in schematicTree
        # the "clean" paths are used to filter the XML file
        schemaPaths = MU.get_xpaths_in_element_tree(schema_tree, [exec_mode])

        # check if elements in baseTree correspond to elements in schematicTree; if not, remove
        removeElems = set([])
        for elem in target_tree.iter():
            elemPath = MU.xpath_to_clean_xpath(target_tree.getpath(elem))
            if elemPath not in schemaPaths:
                removeElems.add(elem)

        # remove all elements that were added to remove-list
        MU.remove_elements_from_tree(*removeElems)

        return target_tree


    def _check_toolspecific(self, target_tree, toolspec_node):
        """
        (PRIVATE) This function checks the 'toolspecific' nodes of the tool for node references. If references are found, the
        referenced elements are added to a 'keep'-list, whereas all other mutliplicity-items are added to the
        'remove'-list.

        :param target_tree:
        :param toolspec_node:
        :return: keep, remove: sets of elements to keep in or remove from tree
        """

        # initiate keep-, remove-, checked-lists
        keep, remove = set([]), set([])

        # get toolspecific node
        toolspec_search = ".//toolspecific/{}".format(toolspec_node)
        toolspec_node = target_tree.find(toolspec_search)

        # if toolspecific node present, iterate children and check for UID-references in tree
        if toolspec_node is not None:

            for el in toolspec_node.iter():

                if MU.element_is_UID_item(el):  # if el is UID-element, perform reference check

                    # get elem value and xpath
                    uidVal = el.text
                    elemPath = target_tree.getpath(el)
                    cleanPath = MU.xpath_to_clean_xpath(elemPath)

                    # get referenced elements and keep referenced elem
                    mappedElems = MU.map_UID_item(self.mapping_dict, target_tree, cleanPath)
                    matched, unmatched = MU.match_uid_element(uidVal, *mappedElems)

                    # give warning if no element is found with uid-reference
                    if not matched:
                        uidPath = MU.xpath_to_uid_xpath(elemPath, el)
                        if self.print_details:
                            print "\nWARNING: Could not find any UID-elements referenced by '{}' with 'uID': '{}'".format(uidPath, uidVal)

                    # add matched/unmatched to relevant set
                    keep = keep.union(matched)
                    remove = remove.union(unmatched)


        return keep, remove


    def _check_node_references(self, target_tree):
        """
        (PRIVATE) This function iterates through all children in the provided element and checks if any references are
        are present within the element tree, such as the dependency between wing and wing profile. If dependencies
        are found, elements are added to 'keep' set, otherwise to 'remove' set.

        :param target_tree:
        :return: keep, remove: sets of elements to keep/remove
        """

        # iterate children of element an check for UID-items
        keep, remove = set([]), set([])
        for elem in target_tree.iter():
            if MU.element_is_UID_item(elem):
                uidVal = elem.text
                cleanPath = MU.xpath_to_clean_xpath(target_tree.getpath(elem))
                uidPath = MU.xpath_to_uid_xpath(cleanPath, elem)

                # skip toolspecific nodes
                if "toolspecific" in cleanPath: continue

                # get mapped uid-elements
                mappedElems = MU.map_UID_item(self.mapping_dict, target_tree, cleanPath, print_details=self.print_details)


                #Three things can happen:
                #(1) if mapped elements found, check UIDs and keep matched element
                #(2) if no mapped elements found, and xpath in mapping dict: remove node ancestry (print warning)
                #(3) if no mapped elements found, and xpath not in mapping dict: ignore (print warning)

                # match the mapped elements; add them to appropriate set (KEEP or REMOVE)
                if mappedElems: # (1)

                    # match element; add elements to appropriate set
                    # note: match is ensured in Basefile-generation workflow
                    matched, unmatched = MU.match_uid_element(uidVal, *mappedElems)
                    keep = keep.union(matched)
                    remove = remove.union(unmatched)

                else:  # no mapped elems found

                    # TODO: continue here
                    if cleanPath in self.mapping_dict: # (2)

                        # add element and ancestry to remove
                        matched, unmatched = MU.match_uid_element(uidVal, *self.removeElements)
                        if matched:
                            remove = self._remove_element_ancestry(elem, remove)
                            if self.print_details:
                                print "WANRING: UID-item path '{}' references a removed element; node and ancestry is removed.".format(uidPath)

                    else: # (3)
                        pass # warning is printed in MU.map_UID_item

        return keep, remove


    def _remove_element_ancestry(self, element, removeElements = None):
        """
        (PRIVATE) This function returns a list of the element and its ancestors that are to be removed from the tree. The
        ancestors are checked recursively whether they have other nodes child elements whose descendants do not end up
        in the element to be removed. If other elements present, element is not returned. This function is used to
        "clean up" the element tree.

        :param element:
        :return:
        """

        # initiate removeList and loop starting node/condition
        if removeElements is None:
            removeElements = set([])
        assert isinstance(removeElements, set), "argument must be of type set."

        # initiate while loop; run until condition fails
        elem = element.getparent()
        condition = True
        while condition:
            removeElements.add(elem)
            elem = elem.getparent()

            # check conditions for next loop
            c1 = (not bool(elem.getchildren()))
            c2 = all(child in removeElements for child in elem.getchildren())
            condition = c1 or c2

        return removeElements


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
This script below was my first attempt at performing a node mapping between a schematic and specific tree in order to extract
the input/output file for a specific tool. Many function have been written in 'mapping_utilities.py' that are very
similar to the ones found here, but have a slightly different purpose. I had no time to clean up both function
collections and unify these, but it should definitely be possible. Some functions written here seem to be not very
relevant since they are implemented in the workflow differently than they were originally though to work.
"""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def generate_IO_tree(mapping_dict, base_tree, schema_tree, execution_mode, toolspec_node):
    """
    This function generation the input or output tree from the provided base-tree. The corresponding schema-tree is used
    to check for the nodes to keep. The steps for the generation are as follows:

    [1] Apply Schematic Nodes
    [2] Apply Toolspecific UID-items
    [3] Auto-Check UID-Items
    [4] Check dependencies
    [5] Remove irrelevant nodes from tree

    :param mapping_dict:
    :param base_tree:
    :param schema_tree:
    :param execution_mode:
    :param toolspec_node:
    :return:
    """

    # create copy of original base-file (original for later checks)
    IO_tree = copy.deepcopy(base_tree)
    IO_tree_original = copy.deepcopy(base_tree)


    """[STEP 1]: Apply Schematic Nodes"""
    # >> get "schematic" paths from map file and compare these paths to the ones present in baseFile
    # >> if the "generic" path from the schematicTree matches the one in the baseTree, keep it; otherwise remove

    # create set of "clean" element paths in schematicTree; the "clean" paths will be used to filter the XML file
    mapPathsSet = MU.get_xpaths_in_element_tree(schema_tree, [execution_mode])

    # check if elements in baseTree correspond to elements in schematicTree; if not, remove
    removeUnmappedElems = set([])
    for elem in IO_tree.iter():
        baseElemPath = MU.xpath_to_clean_xpath(IO_tree.getpath(elem))
        if baseElemPath not in mapPathsSet:
            removeUnmappedElems.add(elem)

    # remove all elements that were added to remove-list
    MU.remove_elements_from_tree(*removeUnmappedElems)


    """[STEP 2]: Apply Toolspecific UID-items"""
    # >> Iterate through toolspecific node, if exists; check if child elements are UID-items

    # initiate keep-, remove-, checked-lists
    keepElements, removeElements = set([]), set([])

    # if toolspec node in file, iterate children and check if UID-elements match item-UID
    toolspec_node = IO_tree.find(".//toolspecific/{}".format(toolspec_node))
    if toolspec_node is not None:
        for el in toolspec_node.iterchildren():
            elVal = el.text
            elemPath = IO_tree.getpath(el) # path may contain indeces

            if MU.element_is_UID_item(el): # if el is UID-element (**)

                # remove indeces from element path, if any present
                UID_itemPath = MU.xpath_to_clean_xpath(elemPath)

                # check if UID-elements exist that match item-UID
                addKeep, addRemove, addElemPathChecked = search_UID_elements(mapping_dict, IO_tree, UID_itemPath, UID_elemPath=None, applied_UID=elVal)

                # add results to lists
                keepElements = keepElements.union(addKeep)
                removeElements = removeElements.union(addRemove)

                # if not UID specified in toolspec, add the selected option
                if not elVal:
                    el.text = next(iter(addKeep))[1] # get UID of kept element


    """[STEP 3]: Auto-Check UID-Items""" # TODO: NOT SURE IF STILL NEEDED
    # >> Filter "important" items if not yet done so; these may not be in toolspecific, but should be checked either way

    # These elements are checked regardless of the toolspecific nodes
    AUTO_CHECK_UID_ELEMENTS = [] # "/cpacs/vehicles/aircraft/model"

    if AUTO_CHECK_UID_ELEMENTS:
        # loop through auto check elements and determine whether already checked or not; if not, perform check
        for UIDelemPath in AUTO_CHECK_UID_ELEMENTS:
            addKeep, addRemove, addElemPathChecked = search_UID_elements(mapping_dict, IO_tree, None, UIDelemPath)

            # add results to lists
            keepElements = keepElements.union(addKeep)
            removeElements = removeElements.union(addRemove)

        # if elements appear in keepElements and in removeElements, delete from removeElements
        keepElements = set(keepElements) # make unique
        removeElements = set(removeElements)
        for elem in keepElements:
            if elem in removeElements:
                removeElements.remove(elem)

    # remove the remaining elements in removeElements from tree
    MU.remove_elements_from_tree(*removeElements)


    """[STEP 4]: Check dependencies"""
    # >> check for dependencies in the remaining nodes; e.g. if wing needs certain wing profile nodes, keep those nodes

    # initiate new removeElements list
    removeElements = set([])

    # get root of tree and check node dependencies among all child nodes
    root = IO_tree.getroot()
    for childEl in root.getchildren():

        # do not check toolspecific nodes
        if 'toolspecific' not in childEl.tag:
            addKeep, addRemove = check_node_dependencies(mapping_dict, IO_tree, childEl, keepElements, IO_tree_original)

            # add matching elements to keep and remove list
            keepElements = keepElements.union(addKeep)
            removeElements = removeElements.union(addRemove)


    """[STEP 5]: Remove nodes from tree"""
    # >> remove all elements from removeElements if they exist in keepElements; delete elements in removeElements

    # delete all required elements from removeList, then remove elements
    for elem in keepElements:
        if elem in removeElements:
            removeElements.remove(elem)
    MU.remove_elements_from_tree(*removeElements)


    return IO_tree

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # (*) toolspecific nodes should be named differently for each execution. (?)
    # (**) UID-elements are elements that have "UID" in its tag
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def remove_element_ancestry(element):
    """
    This function returns the element and its ancestors from the tree that are to be removed. The ancestors are checked
    recursively whether they have other nodes child elements whose descendants do not end up in the element to be
    removed. If other elements present, element is not returned. This function is used to "clean up" the element tree.

    :param element:
    :return:
    """

    # initiate removeList and loop starting node/condition
    removeElements = set([])
    elem = element.getparent()
    condition = True

    while condition:
        removeElements.add(elem)
        elem = elem.getparent()

        # check conditions for next loop
        condition = (not bool(elem.getchildren())) or all(child in removeElements for child in elem.getchildren())

    return removeElements


def search_UID_elements(mapping_dict, elementTree, UID_itemPath, UID_elemPath=None, applied_UID=None):
    """
    This function uses either UID_itemPath or UID_elemPath arguments to search for elements in the base-file.

    If UID_itemPath is provided, the mapping dict is used to look up the search path to get the wanted elements. If UID_elemPath
    is provided, it is directly used as a search path (must start with './/' in order to work properly)*, and no dictionary
    is needed for look-up.

    If multiple elements are found, the user is asked to pick the relevant ones. This way. the base-tree
    is "filtered" and unwanted nodes are removed.

    * './/' is used in lxml to search ALL paths that relate to search path (ignores indeces), not just a specific one.

    :param elementTree: XML-tree
    :param UID_itemPath: Path of the UID-item that is used to look up the search path
    :param UID_elemPath: Path of the UID-element that is directly used as a search path
    :param applied_UID: If provided, it's the UID that will be applied in the tree; otherwise None
    :return: keepElements: List of elements that are kept in basefile
    :return: removeElements: List of elements that are removed from basefile
    :return: UID_elemPathChecked: String of the path checked, or None
    """

    # make sure that EITHER UID_itemPath OR UID_elemPath is provided; exclusive-OR
    assert (UID_itemPath is None) is not (UID_elemPath is None), "Either 'UID_itemPath' or 'UID_elemPath' must be provided."

    # assert arguments
    if UID_itemPath is not None:
        assert isinstance(UID_itemPath, basestring), 'Argument must be of type string or None.'
    if UID_elemPath is not None:
        assert isinstance(UID_elemPath, basestring), 'Argument must be of type string.'
    if applied_UID is not None:
        assert isinstance(applied_UID, basestring), 'Argument must be of type string.'

    # inititate keep and remove lists
    keepElements, removeElements = set([]), set([])

    # use UID-tags to match elements in tree
    # either search by itemPath or elementPath (check definition)
    if UID_itemPath is not None:
        matched_UIDelems, UID_elemPathChecked = map_UIDtags_to_elements(mapping_dict, elementTree, UID_itemPath)
    else:
        matched_UIDelems, UID_elemPathChecked = map_UIDtags_to_elements(mapping_dict, elementTree, None, UID_elemPath)

    # if applied_UID is provided, check if it exists and apply it, if it does
    if applied_UID is not None:

        # get all elements that match item-UID
        addKeep, addRemove = match_UID_elements(applied_UID, matched_UIDelems)

        # add matched element to keeplist; other elements to removeList
        if not keepElements:
            keepElements = keepElements.union(addKeep)
            removeElements = removeElements.union(addRemove)

        assert addKeep, "Could not match the provided UID {} among the found nodes using {}.".format(applied_UID, UID_elemPathChecked)
        # TODO: make sure this will not cause Error

    else: # if applied_UID is None

        # promt user to select one of the found UIDs from matched_UIDelems
        if len(matched_UIDelems) > 1:

            # let user select UID
            mssg = "The following UID-elements were found:"
            PRI.print_indexed_list(*matched_UIDelems, message=mssg)
            mssg = "Please select the matched UID-elements to be kept in Basefile:"
            selectedOpt = PRO.user_prompt_select_options(*matched_UIDelems, message=mssg, allow_multi=True, allow_empty=False)

            # add element to keep and remove lists
            matchedTpl = matched_UIDelems.pop(selectedOpt)
            keepElements.add(matchedTpl[0])
            removeElements = removeElements.union(set([tpl[0] for tpl in matched_UIDelems]))

        # if only one found, keep it
        elif len(matched_UIDelems) == 1:

            # add UID to toolspec and keepElements
            matchedTpl = next(iter(matched_UIDelems))
            keepElements.add(matchedTpl[0])

    return keepElements, removeElements, UID_elemPathChecked


def map_UIDtags_to_elements(mapping_dict, tree, UID_itemPath, UID_elemPath=None):
    """
    This function takes a UID-tag and returns specific XML-elements that are referred to by this tag. Either UID-item
    path or UID-element path must be provided.

    Example:
    Input "airfoilUID" will map to XML-element "/cpacs/vehicles/profiles/wingAirfoils/wingAirfoil", and return this
    element. All mappings are stored in the dictionary "MAPPING_DICT"

    :param tree: XML-tree
    :param UID_itemPath: UID-item path that is used to map to search path, String
    :param UID_elemPath: Search path for UID-elements (must start with './/' to work properly), String
    :return UIDelemList: List of UID-elements found using search path
    :return searchPath: String representing used search path; None if no mapping found
    """
    # make sure that EITHER UID_itemPath OR UID_elemPath is provided; exclusive-OR
    assert (UID_itemPath is None) is not (
    UID_elemPath is None), "Either 'UID_itemPath' or 'UID_elemPath' must be provided."

    # assert arguments
    if UID_itemPath is not None:
        assert isinstance(UID_itemPath, basestring), 'Argument must be of type string or None.'
    if UID_elemPath is not None:
        assert isinstance(UID_elemPath, basestring), 'Argument must be of type string.'

    # define search path according to the argument provided;
    # either use UID-element path directly, or translate UID-item path through mapping-dict
    if UID_itemPath:
        if UID_itemPath in mapping_dict:
            searchPath = MU.xpath_to_searchpath(mapping_dict[UID_itemPath])
        else: # if item path not found in mapping dict
            searchPath = None

            # this should not happen, but it will give user the information how to update the mapping dict
            print "WARNING: Could not find UID-item path {} in MAPPING-DICT. UID-item is not mapped.".format(UID_itemPath)

    else:
        searchPath = UID_elemPath
        if not searchPath.startswith('.//'):
            searchPath = MU.xpath_to_searchpath(UID_elemPath)

    # search for UID elements in tree; return found elements
    if searchPath:

        # find all elements according to searchP path
        UIDelemList = [(el, el.attrib["uID"]) for el in tree.findall(searchPath)]

        if not UIDelemList: # if no elems found
            print "WARNING: Could not find any UID-elements using search path '{}' during mapping.".format(searchPath) # TOdO: debug this

        # return list of tuples with elements and UIDs (element, UID), empty if none found; search path
        return UIDelemList, searchPath

    # if no search path found
    return [], None


def check_node_dependencies(mapping_dict, tree, element, checkElements, checkTree, ignoreNodes = None):
    """
    (PRIVATE) This function iterates through all children in the provided element and checks if any dependencies are
    are present within the element tree, such as the dependency between wing and wing profile. If dependencies are found,
    elements remain in the tree.
    The function recurrently performs the check of the child nodes up until the leaf nodes.

    The checkTree argument is contains the original tree in order to check whether any of the nodes refer to elements
    that have already been removed. In case they do, the user is asked whether to keep the node or not.

    :param tree:
    :param element:
    :param keepElements:
    :param checkTree:
    :return:
    """

    # if ignoreNodes in element path, return empty lists (skip)
    # ignoreNode must simply be a string in the elementpath to be ignored
    elementPath = tree.getpath(element)
    if ignoreNodes:
        assert isinstance(ignoreNodes, collections.Iterable), "'ignoreNodes' argument must be iterable.'"
        if any(ignoreNode in elementPath for ignoreNode in ignoreNodes):
            return set([]), set([])

    # iterate children of element an check for UID-items
    keepElements, removeElements = set([]),set([])
    for elemChild in element.iterchildren():  # loop is only entered when children present

        # if elem is UID-item, check if its UID can be mapped
        if MU.element_is_UID_item(elemChild):
            childItem_UID = elemChild.text
            UID_itemPath = MU.xpath_to_clean_xpath(tree.getpath(elemChild))

            # return all elements that were found using search path
            UIDelemList, searchPath = map_UIDtags_to_elements(mapping_dict, tree, UID_itemPath)

            if UIDelemList: # if any mapped UID-elements found

                # check if any found elements match item-UID; if any matches exist, add to relevant lists
                addKeep, addRemove = match_UID_elements(childItem_UID, UIDelemList)

                # if found element matches UID, keep; otherwise remove
                # if no matches are found, remove UID-item
                if addKeep:
                    keepElements = keepElements.union(addKeep)
                    removeElements = removeElements.union(addRemove)
                else:
                    print "WANRING: UID-item '{}' with value '{}' does not refer to any elements; is removed from tree.".format( # TODO: debug this
                        UID_itemPath, childItem_UID)
                    addRemove = remove_element_ancestry(elemChild)
                    removeElements = removeElements.union(addRemove)


            elif searchPath and not UIDelemList:  # if search path is found, but no UID-elements returned

                # the UID-item may refer to elements that were already removed from tree
                # check the original tree for the elements
                UIDelemList, searchPath = map_UIDtags_to_elements(mapping_dict, checkTree, None, searchPath)
                addKeep, addRemove = match_UID_elements(childItem_UID, UIDelemList)

                # if elements found in original tree, ask user to keep or not; otheriwse remove
                if addKeep:
                    msg = "\nUID-item '{}' with value '{}' refers to removed elements.\nWould you like to remove it and its relevant ancestors from the tree?".format(UID_itemPath, childItem_UID)
                    sel = PRO.user_prompt_yes_no(message=msg)
                    if sel:
                        addRemove = remove_element_ancestry(elemChild)
                        removeElements = removeElements.union(addRemove)
                else:
                    print "WANRING: UID-item '{}' with value '{}' does not refer to any elements; is removed from tree.".format(UID_itemPath, childItem_UID)
                    addRemove = remove_element_ancestry(elemChild)
                    removeElements = removeElements.union(addRemove)

            else: # if no searchpath (and UID element list)
                print "WARNING: No search path found for element {} in mapping dict; element removed.".format(UID_itemPath)
                addRemove = remove_element_ancestry(elemChild)
                removeElements = removeElements.union(addRemove)


        # recurrency until leaf node; add elements to keep and remove sets
        addKeep, addRemove = check_node_dependencies(mapping_dict, tree, elemChild, checkElements, checkTree, ignoreNodes)
        keepElements = keepElements.union(addKeep)
        removeElements = removeElements.union(addRemove)

    return keepElements, removeElements


def match_UID_elements(UID, UID_element_tuples):
    """
    (PRIVATE) This function tries to look for a match of the provided UID with any of the provided
    element tuples. The element tuples are required to have the following structure:

    tpl = (lxml.etree._Element, 'elementUID')

    :param UID: The UID to be matched (string)
    :param UID_element_tuples: List of tuples containing lxml-element and its UID
    :return: keepElements, removeElements: List containing elements to keep in /remove from basefile
    """

    # iterate through list of tuples and check for match
    keepElements, removeElements = [], []
    for idx, UID_elem in enumerate(UID_element_tuples):  # if no elements found, loop won't be entered
        if UID_elem[1] == UID:

            # add elements to keep and reove lists
            matchedTpl = UID_element_tuples.pop(idx)
            keepElements.append(matchedTpl[0])  # dependencies added to keep list
            removeElements += [tpl[0] for tpl in UID_element_tuples] # otherwise to removelist

            break  # loop is exited after first match

    return set(keepElements), set(removeElements)

