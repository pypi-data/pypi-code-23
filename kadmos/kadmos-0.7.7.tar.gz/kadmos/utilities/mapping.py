import copy
import re
import os
import xml
from lxml import etree

from kadmos.external.XML_merger.XMLmerger import XMLCombiner, XMLCombiner_UID

import prompting
import printing


class Continue(Exception):
    pass   # exception class to return to outermost loops in nested iterations


def get_applied_uids_by_path(mapping_dict, tree, xpath, uiDict = {}):
    """
    This function checks whether the xpath (or any part of it) is a UID-element and checks whether there exist UID-items
    in the tree that refer to these elements. The text-values of the UID-items are retrieved in a dict so that
    {"path-to-uid-element":set([""applied-uid,..]), ...}.

    :param mapping_dict:
    :param tree:
    :param xpath:
    :param uiDict: dictionary carrying reference UIDs and paths {path:set([uids])}
    :return: uiDict: dictionary containing {path: set(reference uids)}
    :rtype dict
    """

    # get uid-element paths from mapping dict
    uidElemPaths = set(mapping_dict.values())

    # split path to check each parent for existence in mapping-dict
    pathSpl = xpath.split('/')

    # iterate through split path and check whether each ancestor path is in mapping-dict
    # if found in mapping dict, uid-element path is mapped and UID-items (and UIDs) retrieved
    for idx, elem in enumerate(pathSpl):
        if idx == 0: continue
        path = '/'.join(pathSpl[:idx+1])

        if path in uidElemPaths:

            # add path to dict
            if path not in uiDict:
                uiDict[path] = set()

            # check which uid items refer (link) to this uid element
            uidItems = map_UID_element(mapping_dict, tree, path)
            uidAdded = False
            if uidItems:
                for item in uidItems:
                    if item.text:
                        uiDict[path].add(item.text)
                        uidAdded = True
            # if no links found, check whether this element already exists; add uid
            if not uidAdded:
                searchPath = xpath_to_searchpath(path)
                for el in tree.findall(searchPath):
                    uiDict[path].add(el.get("uID"))

    return uiDict


def add_xpath_to_tree(tree, xpath):
    """
    This function creates an xml element tree out of the provided xpath, and adds it to the provided tree.

    :param tree:
    :param xpath:
    :return: mTree: resulting tree from merge of xpath tree with provided tree
    """

    # get root in xpath and create tree
    path_elems = xpath.split('/')[1:]  # dont include empty string
    root = etree.Element(path_elems[0])

    # iterate xpath elements and add to xpathTree
    parentEl = root
    for path_elem in path_elems[1:]: # skip root
        childEl = etree.SubElement(parentEl, path_elem)
        parentEl = childEl

    # make element tree; merge xpathTree with existing tree
    xpathTree = etree.ElementTree(root)
    mTree = merge_XML_trees(tree, xpathTree)

    return mTree


def element_is_UID_item(element):
    '''
    (PRIVATE) This function checks whether the provided element is an UID-item or not. A UID-item is a child element
    that carries 'UID' in its name, and normally used to refer to specific elements in the xml-tree.

    :param element: lxml.etree._Element; element to be checked
    :return: bool
    '''
    # make sure argument is etree-element
    assert isinstance(element, etree._Element), 'Element must be lxml-element.'

    # check if element has children and whether 'UID' in its tag
    return not bool(element.getchildren()) and element.tag.upper().endswith('UID')



def match_uid_element(uid, *uid_elements):
    """
    (PRIVATE) This function tries to look for a match of the provided UID with any of the provided
    elements. The first matching element is added to a 'keep' set, the rest is moved to the 'remove' set.

    :param uid: The UID to be matched (string)
    :param uid_elements: elements containing lxml-element and its UID
    :return: matched, unmatched: sets with matched and unmatched
    """

    # initiate matched/unmatched sets
    matched, unmatched = set([]), set(el for el in uid_elements)

    # iterate through list of tuples and check for match
    for idx, uid_elem in enumerate(unmatched):  # if no elements found, loop won't be entered
        if uid_elem.get('uID') == uid:

            # add elements to matched, unmatched
            matched.add(uid_elem)
            unmatched.remove(uid_elem)
            break  # loop is exited after first match

    return matched, unmatched



def xpath_to_uid_xpath(xpath, element):
    """
    This function adds element UIDs to the corresponding elements in the xpath. The ancestors of the element that
    belongs to the xpath are iterated and checked for the "uID" attribute. If one is found, it is added to the
    approriate place in the xpath. If xpath contains indeces in elements that have no defined UID, the indeces
    are kept.


    :param xpath: xpath of xml-element
    :type basestring
    :param element: lxml-element
    :return: uid_xpath
    :rtype basestring
    """

    # define bracket pattern for regex search
    bracketPattern = re.compile('\[.*?\]')

    # get elements in xpath and reverse list for easier operation with ancestors
    path_elems = xpath.split('/')[1:]
    rev_path_elems = list(reversed(path_elems))

    # if element has UID attribute, add it to xpath element
    if element.get('uID'):
        # remove existing index-bracket, if present; add uid to element
        cleanElem = bracketPattern.sub("", rev_path_elems[0])
        rev_path_elems[0] = '{}[{}]'.format(cleanElem, element.get('uID'))

    # loop through ancestors, check for uid attribute
    for idx, anc in enumerate(element.iterancestors()):

        # if uid attribute present, add to appropriate element
        if anc.get('uID') is not None:
            # remove any existing index-brackets; add uid to element
            cleanElem = bracketPattern.sub("", rev_path_elems[idx + 1])
            rev_path_elems[idx + 1] = '{}[{}]'.format(cleanElem, anc.get('uID'))

    # join elements to uid-xpath
    uid_xpath = "/" + "/".join(reversed(rev_path_elems))

    return uid_xpath


def xpath_to_clean_xpath(xpath):
    """
    This function removes all indeces from a string. Indeces are defined as squared brackets containing an integer
    value, such as '[56]'.

    :param xpath: xpath
    :return: new_string: String without indeces
    """

    # define index pattern
    indexPattern = re.compile('\[.*?\]')

    # remove all indeces from string, if any present
    clean_xpath = re.sub(indexPattern, '', xpath)

    return clean_xpath


def xpath_to_searchpath(xpath, exact_search = False):
    """
    This function converts an xpath to a searchpath that can be used with "etree.find()" or "etree.findall()". The
    search path does not include the root elements, and instead has './/' for complete search (see lxml documentation).

    :param xpath:
    :type basestring
    :return: search_path
    """
    prefix = ".//"
    if exact_search:
        prefix = "./"

    # split string, get rid of root element; add ".//" to front
    path_elems = xpath.split('/')[1:]  # dont include empty string
    search_path = "{}{}".format(prefix, "/".join(path_elems[1:]))

    return search_path


def isolate_element_path_in_tree(element, delete_root_attr=True):
    """
    This function eliminates all nodes from the tree that do not lie on the path of the provided element. A new tree
    with copies of the isolated nodes is returned.

    :param element:
    :return: iso_tree
    """

    # copy element
    c_element = copy.deepcopy(element)
    ancs = [a for a in c_element.iterancestors()]
    chil = [a for a in c_element.iterchildren()]

    # iterate ancestors and remove all child nodes that are not THAT child
    child = copy.deepcopy(element)
    for anc in element.iterancestors():
        c_anc = copy.deepcopy(anc)
        for c in c_anc.iterchildren():
            c_anc.remove(c)
        c_anc.append(child)
        child = c_anc

    # get root of tree and create new iso_tree
    iso_tree = etree.ElementTree(c_anc)

    # delete root attribs
    if delete_root_attr:
        root = iso_tree.getroot()
        attribs = root.keys()
        for att in attribs:
            root.attrib.pop(att, None)

    return iso_tree


def map_UID_item(mapping_dict, tree, xpath, print_details=True):
    """
    This function uses the mapping dictionary to map the UID-item to a UID-element and return all UID-elements that
    correspond to the mapped path.

    :param mapping_dict:
    :param tree:
    :param xpath:
    :return: list of mapped UID-elements
    """

    # make sure that xpath is string
    assert isinstance(xpath, basestring), "xpath argument must be string."

    # get mapped UID-element path
    searchNode = None
    if xpath in mapping_dict:
        searchNode = mapping_dict[xpath]
        return search_elements_in_tree(tree, searchNode)

    else:
        if print_details:
            print "WARNING: UID-item (link) path not found in Mapping-Dict: {}".format(xpath)
            print "WARNING: UID-item (link) path not found in Mapping-Dict: {}".format(xpath)

    return


def map_UID_element(mapping_dict, tree, xpath):
    """
    This function uses the mapping dictionary to map the UID-element to a UID-item (basically, reverse mapping) and
    returns all UID-items that correspond to the mapped path.

    :param mapping_dict:
    :param tree:
    :param xpath:
    :return: list of mapped UID-items
    """

    # make sure that xpath is string
    assert isinstance(xpath, basestring), "xpath argument must be string."

    # get mapped UID-item paths (multiple UID-items can refer to UID-element)
    searchPaths = []
    if xpath in mapping_dict.values():
        for k,v in mapping_dict.iteritems():
            if xpath == v:
                searchPaths.append(k)
    else:
        print "WARNING: UID-element {} not found in Mapping-Dict.".format(xpath)

    # search for mapped UID-item in tree
    uid_items = []
    for path in searchPaths:
        foundItems = search_elements_in_tree(tree, path)
        if foundItems:
            uid_items += foundItems

    return uid_items


def search_elements_in_tree(tree, xpath):
    """
    This function searches the provided tree for elements that correspond to the xpath. Returns found elements in list.

    :param xpath:
    :type basestring
    :return: elementsFound: list of elements that correspond to xpath; if none found, empty list
    :rtype list
    """

    # make sure that xpath is string
    assert isinstance(xpath, basestring), "xpath argument must be string."

    # turn node path into search path; find all elements according to searchP path
    searchPath = xpath_to_searchpath(xpath)
    elementsFound = [el for el in tree.findall(searchPath) if el is not None]

    return elementsFound


def copy_toolspecific_elements_to_tree(target_tree, source_tree, element, **kwargs):
    """
    This function copies the provided toolspecific element to the target tree. If 'overwrite_if_exist' is set to True, an
    existing child node will be overwritten; missing nodes are always added to the target tree.

    :param target_tree: Tree to copy elements to
    :type etree._ElementTree
    :param source_tree: Tree to copy elements from
    :type etree._ElementTree
    :param element: name of toolspecific element
    :type string
    :param overwrite_if_exist: Determines whether elements are overwritten in target tree or not, default: False
    :type boolean
    :return: target_tree: Tree to copy elements to
    :rtype etree._ElementTree
    """

    overwrite_if_exist = False
    if "overwrite_if_exist" in kwargs:
        overwrite_if_exist = kwargs['overwrite_if_exist']

    nodes_valued = False
    if "nodes_valued" in kwargs:
        nodes_valued = kwargs['nodes_valued']

    # define toolspecific search path
    TOOLSPEC = "toolspecific"

    # check arguments
    assert isinstance(element, basestring), 'Argument must be of type string.'
    assert isinstance(overwrite_if_exist, bool), 'Argument must be boolean.'

    # perform element search in source tree
    elemFound = source_tree.find(".//{}/{}".format(TOOLSPEC, element))

    # check if elements found
    if elemFound is None:
        print "WARNING: 'toolspecific' element {} was not found in source tree.".format(element)
        return target_tree

    # make sure nodes have value
    if nodes_valued:
        for node in elemFound.iter():
            if not node.getchildren():
                if not node.text:
                    msg = "\nWARNING: Node '{}' does not have a value, please set:".format(source_tree.getpath(node))
                    usr = prompting.user_prompt_string(message=msg)
                    node.text = usr

    # get element copy to insert into basefile
    elemCopy = copy.deepcopy(elemFound)

    # if "toolspecific" node '/cpacs/toolspecific' does not exist in baseTree, add it
    if target_tree.find('.//{}'.format(TOOLSPEC)) is None:
        root_target = target_tree.getroot()
        root_target.insert(-1, etree.Element('{}'.format(TOOLSPEC)))

    # get relevant target elements
    toolspec_target = target_tree.find('.//{}'.format(TOOLSPEC))
    toolnode_target = target_tree.find('.//{}/{}'.format(TOOLSPEC, elemCopy.tag))

    # insert element into "toolspecific"
    if toolnode_target is None:  # simply insert if not exist
        toolspec_target.insert(0, elemCopy)
    else:
        # replace or add missing child elements to existing node
        toolnodeChildren_target = [child.tag for child in toolnode_target.iterchildren()]
        for child in elemCopy.iterchildren():
            if child.tag not in toolnodeChildren_target:
                toolnode_target.insert(0, child)
            else:
                if overwrite_if_exist:
                    toolnode_target.remove(target_tree.find(".//{}/{}/{}".format(TOOLSPEC, elemCopy.tag, child.tag)))
                    toolnode_target.insert(0, child)

    return target_tree


def get_xpaths_in_element_tree(tree, apply_modes=None, ignore_uids=True, leaf_nodes=False):
    """
    This function collects all node xpaths of an XML tree in a set. Filter options enable to only apply the relevant
    execution modes or to ignore indeces in the path.

    :param tree: element tree whose nodes are collected
    :type etree._ElementTree
    :param apply_modes: container of modes that are applied to nodes
    :type None or iterable (not string)
    :param ignore_uids: If True, xpath indeces are ignored
    :type bool
    :return: nodeSet
    :rtype set
    """

    # assert inputs
    assert isinstance(tree, etree._ElementTree), "Argument must be element tree."
    assert isinstance(ignore_uids, bool), "Argument must be boolean."
    if apply_modes is not None:
        assert hasattr(apply_modes, "__iter__"), "Argument must be iterable."
    assert isinstance(leaf_nodes, bool), "'leaf_nodes'-argument must be boolean."

    # loop through tree and add node path to set
    nodeSet = set([])
    for elem in tree.iter():
        try: # if applied modes do not match, return to outer loop (do not add node to set)

            # if set to True, only get leaf nodes
            if leaf_nodes:
                if elem.getchildren():
                    continue

            # if set, only allow nodes that are used in execution mode
            if apply_modes is not None:

                # if modes present in node or ancestors, check if mode in applied modes
                if 'modes' in elem.attrib:
                    elemModes = elem.attrib['modes'].split()
                    if set(apply_modes).isdisjoint(elemModes):
                        raise Continue
                for anc in elem.iterancestors():
                    if 'modes' in anc.attrib:
                        ancModes = anc.attrib['modes'].split()
                        if set(apply_modes).isdisjoint(ancModes):
                            raise Continue

            # remove all indeces and add path to set
            if ignore_uids:
                elemPath = xpath_to_clean_xpath(tree.getpath(elem))
            else:
                elemPath = xpath_to_uid_xpath(tree.getpath(elem), elem)
            nodeSet.add(elemPath)

        except Continue: # continue looping nodes
            pass

    return nodeSet


def filter_tree_by_modes(tree, modes):
    """
    This function removes all nodes that are not applied to the provided execution modes, returns tree.

    :param tree:
    :param modes:
    :return:
    """

    # copy tree
    ctree = copy.deepcopy(tree)

    # get all relevant path in tree (filtered by modes)
    treePaths = get_xpaths_in_element_tree(ctree, modes, ignore_uids=False)

    # loop tree and check whether path in set of tree paths
    removeElements = set([])
    for elem in ctree.iter():
        if xpath_to_uid_xpath(ctree.getpath(elem), elem) not in treePaths:
            removeElements.add(elem)

    # remove elements form tree
    remove_elements_from_tree(*removeElements)

    return ctree


def filter_tree_by_xpaths(tree, xpaths):
    """
    This function filters the tree by the provided xpaths. All elements that are not found in list of xpaths are
    removed from tree.

    :param tree:
    :param xpaths:
    :return:
    """


    # create tree copy for item removal
    cTree = copy.deepcopy(tree)

    # iterate tree and check if their paths are in 'xpaths'; if not, add to remove
    removeElems = []
    for elem in cTree.iter():
        if xpath_to_clean_xpath(cTree.getpath(elem)) not in xpaths:
            removeElems.append(elem)

    # remove elements
    remove_elements_from_tree(*removeElems)

    return cTree


def make_clean_xml_tree(root_node):
    """
    This function creates a clean element tree using the provided root node string.

    :param root_node: root node of tree
    :type basestring
    :return: element tree
    """

    return etree.ElementTree(etree.Element(str(root_node)))



def add_nodes_to_tree(mapping_dict, tree, node_paths, use_case_dir_path, refUIDs = {}):
    """
    In this function, the user is asked to either add nodes manually or automatically. Manual addition of nodes requires
    the user to fill out a template, whereas the automatic addition will search exisiting nodes in other KB files, and
    add these to the tree.

    The added nodes are always written to a template file so that the user can access the appropriate file in order to
    perform manual changes before adding the nodes.

    :param mapping_dict
    :type dict
    :param tree:
    :type element tree
    :param node_paths:
    :type list
    :param use_case_dir_path:
    :type basestring
    :param refUIDs: dictionary containing {path: [reference uids],...}
    :type dict
    :return:
    """
    METHODS = ["Manual", "Full-Auto", "Select from Repository (not implemented)", "Match Node Structure Only (not implemented)"]
    """
    Manual - manual addition of nodes via template
    Full-Auto - look for existing nodes and UID matches in other Use Cases, add first found matches
    Semi-Auto - look for existing nodes and UID matches in other Use Cases, let user pick which ones to add
    Bolt-Action - get existing nodes in other Use Cases, let user pick, adapt UIDs to match
    """

    # HARDCODE
    TEMPLATE_DIR = "TEMPLATES"

    # add new template directory if it does not yet exist in KB dir
    templ_dir_path = os.path.join(use_case_dir_path, TEMPLATE_DIR)
    if not os.path.exists(templ_dir_path):
        os.makedirs(templ_dir_path)

    # repeat until missing nodes filled in
    missing_nodes = node_paths
    templ_tree = make_clean_xml_tree("cpacs")
    while True:

        # ask user whether to provide nodes manually or not
        msg = "The following methods are available to fill in the missing nodes in the Basefile:"
        printing.print_indexed_list(*METHODS, message=msg)
        mssg = "Please pick one from the list above:"
        sel = prompting.user_prompt_select_options(*METHODS, message=mssg, allow_empty=False, allow_multi=False)
        option = next(iter(sel))

        if option == "Manual":
            # execute function to manually select nodes
            out_tree, addedNodes = get_nodes_by_xpaths_manual(missing_nodes, templ_dir_path, refUIDs)

        elif option == "Full-Auto":
            out_tree, addedNodes = get_nodes_by_xpaths_full_auto(missing_nodes, use_case_dir_path, templ_dir_path, refUIDs)

        elif option == "Semi-Auto":# user selects use-case
            print "NOT YET IMPLEMENTED, PICK A DIFFERENT METHOD"
            continue

        elif option == "Bolt-Action": # user changes uids/values when not found
            print "NOT YET IMPLEMENTED, PICK A DIFFERENT METHOD"
            continue

        # print added nodes; continue if no added
        if addedNodes:
            if len(addedNodes[0])>2:
                header = ["Xpath", "Value", "Basefile"]
            else:
                header = ["Xpath", "Value"]
            print "\nThe following nodes were added to the Basefile:"
            printing.print_in_table(addedNodes, headers=header, print_indeces=True)
        else:
            print "\nNOTE: No nodes were added."
            continue

        # if elements in output_tree are not filled in, nodes are added to new "missing" list and refUID-dict
        # user can then decide whether to repeat node addition with only missing nodes, or complete restart
        missing = []
        missing_refUIDs = {}
        for elem in out_tree.iter():
            if not elem.getchildren() and not elem.text:
                elemPath = xpath_to_clean_xpath(out_tree.getpath(elem))
                missing.append(elem)

                #  get missing referenced uIDs
                for anc in elem.iterancestors():
                    if anc.get("uID"):
                        ancPath = xpath_to_clean_xpath(out_tree.getpath(anc))
                        if ancPath in missing_refUIDs:
                            missing_refUIDs[ancPath].add(anc.get('uID'))
                        else:
                            missing_refUIDs[ancPath] = set([anc.get('uID')])

                # if UID refrences added in tree, they are considered here
                missing_refUIDs = get_applied_uids_by_path(mapping_dict, out_tree, elemPath, missing_refUIDs)

        # if missing nodes, ask user whether to keep current elems or restart with original
        if missing:

            # print missing nodes
            miss_paths = [xpath_to_uid_xpath(out_tree.getpath(el), el) for el in missing]
            print "\nWARNING: The following nodes are still missing:\n---\n{}\n---".format("\n".join(miss_paths))

            # prompt user whether to keep or dismiss elements
            sel_msg = "Would you like to keep all added elements?"
            sel = prompting.user_prompt_yes_no(message=sel_msg)

            # if elements kept, only missing elements are returned for addition
            if sel:
                missing_nodes = [xpath_to_clean_xpath(xpath) for xpath in miss_paths]
                refUIDs = missing_refUIDs

                # remove missing elements from added tree
                for miss in missing:
                    remove = remove_element_ancestry(miss)
                remove_elements_from_tree(*remove)

                # merge tree
                templ_tree = merge_XML_trees(templ_tree, out_tree)
                continue
            else:
                print "\nNOTE: Nodes are dismissed."
                continue
        else:
            # ask user if continue with added nodes
            msg = "Continue with the added nodes?"
            usr_sel = prompting.user_prompt_yes_no(message=msg)

            if not usr_sel:
                missing_nodes = node_paths
                templ_tree = make_clean_xml_tree("cpacs")
                continue

            templ_tree = merge_XML_trees(templ_tree, out_tree)
            break

    # merge completed template tree into execution tree
    compl_tree = merge_XML_trees_by_UID(tree, templ_tree)

    return compl_tree


def get_nodes_by_xpaths_full_auto(xpaths, use_case_dir_path, templ_dir_path, refUIDs={}):
    """
    This function searches the provided xpaths in other Basefiles in the knowledge base and checks whether the found
    elements have the referenced UIDs in their ancestry. If they do, they are added to a template tree and returned.

    :param xpaths:
    :param use_case_dir_path:
    :param: templ_dir_path
    :param refUIDs:
    :return:
    """

    # get subdirectories
    spec_kb_dir_path = os.path.dirname(use_case_dir_path)
    subdirs = [os.path.join(spec_kb_dir_path, sub) for sub in os.listdir(spec_kb_dir_path) if
               os.path.isdir(os.path.join(spec_kb_dir_path, sub))]  # get immediate subdirs

    # get each basefile in subdirectories
    basefile_paths = [os.path.join(dir, file) for dir in subdirs for file in os.listdir(dir) if
                      file.endswith("-base.xml")]

    # loop through basefiles, parse them
    baseTrees = {}
    for path in basefile_paths:
        baseTrees[path] = etree.parse(path)  # TODO: try except parse error

    # make a copy, since uids are deleted from set when added to tree
    refUIDs = copy.deepcopy(refUIDs)

    # create tree and add xpaths
    templ_tree = etree.ElementTree(etree.Element('cpacs'))
    for xpath in xpaths:
        templ_tree = add_xpath_to_tree(templ_tree, xpath)

    # apply uids to tree
    templ_tree = apply_uids_to_tree(templ_tree, refUIDs)

    # loop through leaf elements in tree and compare them to mapped elements in each base tree
    # if uid-xpaths match, value is applied to leaf element
    addedElements = []
    for elem in templ_tree.iter():
        if not elem.getchildren():
            elemPath = xpath_to_uid_xpath(templ_tree.getpath(elem), elem)
            try:
                # get searchpath
                cleanPath = xpath_to_clean_xpath(elemPath)
                searchPath = xpath_to_searchpath(cleanPath)

                # loop through basetrees and check whether nodes are found using searchpath
                for baseTreePath, baseTree in baseTrees.iteritems():

                    # check whether there is a found node whose path carries all referenced uids
                    for node in baseTree.findall(searchPath):
                        nodePath = xpath_to_uid_xpath(baseTree.getpath(node), node)

                        # if match, add value and continue with next element
                        if nodePath == elemPath:
                            elem.text = node.text
                            addedElements.append((elemPath, elem.text, os.path.basename(baseTreePath)))
                            raise Continue # continue with next element
                        else: # continue looking for match
                            continue

            except Continue:  # continue exception to continue outermost loop
                pass

    # write template to dir
    templ_file_path = get_unique_file_path(os.path.join(templ_dir_path, "template_full-auto.xml"))
    write_xml_tree_to_file(templ_tree, templ_file_path)
    print"\nNOTE: Nodes are written to template {}.".format(templ_file_path)

    # if nothing found, notify user
    if not addedElements:
        print "\nNOTE: No matching elements found in database."

    return templ_tree, addedElements


def get_nodes_by_xpaths_manual(xpaths, templ_dir_path, refUIDs = {}):
    """
    This function creates a template for the user to manually fill in the missing nodes for tool execution. Once the
    template is filled in, the user continues the function and the template is merged into the existing tree.

    The current version of this function now adds UIDs to elements when NESTED. This means that UID elements
    are accounted for if any appear in the ancestry of another UID element. The difficulty with this is to delegate
    as little work as possible to the user and automate the assignment of UIDs to elements, or duplicate elements before
    UID assignment, while keeping the file valid and logical.

    The code in this function contains many nested if, for, and while loops and could possibly be simplified if time
    was not a constraint. I tried to document as much as possible, and found that this implementation works best given
    the complexity.

    :param xpaths: xpaths that must be present in tree; added to template
    :param use_case_dir_path:
    :param refUIDs: dict with {path: set(reference UIDs)}
    :type dict
    :return:
    """
    # HARDCODE
    FILL_IN = "fill_in_here"

    # create tree and add xpaths
    templ_tree = etree.ElementTree(etree.Element('cpacs'))
    for xpath in xpaths:
        templ_tree = add_xpath_to_tree(templ_tree, xpath)

    print "\nConstructing template..."

    # ask user if to add referenced UIDs to template
    msg = "Would you like to add referenced uID's to template?"
    sel = prompting.user_prompt_yes_no(message=msg)

    # make a copy, since uids are deleted from set when added to tree
    refUIDs = copy.deepcopy(refUIDs)

    # if selected, UIDs are added to the template
    if sel:
        templ_tree = apply_uids_to_tree(templ_tree, refUIDs)

    # add "fill in" to leaf nodes
    for elem in templ_tree.iter():
        if not elem.getchildren():
            elem.text = FILL_IN

    # write tree to template dir; make sure path unique
    templ_file_path = get_unique_file_path(os.path.join(templ_dir_path, "template_manual.xml"))
    write_xml_tree_to_file(templ_tree, templ_file_path)

    # let user fill out template
    usr_msg = "A template XML-tree has been written to {}. Please fill it in and continue with [1].".format(templ_file_path)
    usr_sel = prompting.user_prompt_yes_no(message=usr_msg)
    if not usr_sel:
        print "WARNING: Template completion has been cancelled."
        return etree.ElementTree(etree.Element("cpacs")), [] # return empty tree, list


    # parse filled out template to tree
    templ_compl = etree.parse(templ_file_path)
    # templ_compl = etree.parse(r"C:\Users\aMakus\Desktop\emwet-templ.xml") # TODO: DEMO

    # remove "FILL_IN" if present
    for elem in templ_compl.iter():
        if not elem.getchildren() and elem.text == FILL_IN:
            elem.text = ""

    # print added nodes
    addedNodes = []
    for elem in templ_compl.iter():
        if not elem.getchildren() and elem.text:
            addedNodes.append((xpath_to_uid_xpath(templ_compl.getpath(elem), elem), elem.text))

    return templ_compl, addedNodes


def apply_uids_to_tree(tree, refUIDs={}):
    """
    This function iterates the element tree and applies the UIDs stored in "refUIDs" to the appropriate element.
    Intended for use on "naked" trees without any assigned UIDs. If multiple UIDs are stored under one path, additional
    nodes are created.

    refUIDs must have structure:
    refUIDs = {path:set([uid1, uid2,...]), ...}

    :param tree:
    :param refUIDs:
    :return:
    """

    # while loop is need to restart iteration of tree when nodes/uids are added to it
    while True:
        try:  # this serves as "return point" for exception "Continue"

            # iterate through tree breadth-wise (direct children first)
            for element in breadth_first(tree.getroot()):
                cleanPath = xpath_to_clean_xpath(tree.getpath(element))

                # if element is UID-element that is being referred to
                if cleanPath in refUIDs and refUIDs[cleanPath]:

                    # get path of element and search tree for same path
                    searchPath = xpath_to_searchpath(cleanPath)
                    foundElements = tree.findall(searchPath)
                    uidSet = refUIDs[cleanPath]

                    # get predecessors of elements in order to see where to add the created elements
                    par = foundElements[0].getparent()
                    parPath = xpath_to_clean_xpath(tree.getpath(par))
                    predSearchPath = xpath_to_searchpath(parPath)
                    preds = tree.findall(predSearchPath)
                    predPaths = [xpath_to_uid_xpath(tree.getpath(pred), pred) for pred in preds]

                    # check whether elements have no UID yet
                    if any(el.get('uID') is None for el in foundElements):

                        """First Check"""  # go through found elements and apply UIDs
                        for found in foundElements:
                            if found.get('uID'):  # continue this loop if UID present
                                continue

                            # if more than one UID for this element path, let user choose which one to add to element
                            if len(uidSet) > 1:

                                # if only one predecessor, dont bother user to select which element to assign UID to (result the same)
                                if len(preds) == 1:
                                    uid = next(iter(uidSet))
                                    found.set('uID', uid)
                                    uidSet.remove(uid)
                                else:  # if multiple predecessors, user must choose
                                    foundPath = xpath_to_uid_xpath(tree.getpath(found), found)
                                    mssg = "The following 'uIDs' can be assigned to element '{}'".format(foundPath)
                                    printing.print_indexed_list(*uidSet, message=mssg)
                                    sel_msg = "Please select one 'uID' from the list above:"
                                    sel_uid = next(iter(
                                        prompting.user_prompt_select_options(*uidSet, message=sel_msg, allow_empty=False,
                                                                             allow_multi=False)))
                                    found.set('uID', sel_uid)
                                    uidSet.remove(sel_uid)

                            # if exactly one uid in set, pick that uid for the element
                            elif len(uidSet) == 1:
                                uid = next(iter(uidSet))
                                found.set('uID', uid)
                                uidSet.remove(uid)

                            # if no uids present, remove the element
                            else:
                                found.getparent().remove(found)

                        # start another tree iteration after adding UIDs
                        raise Continue

                    else:  # if all elements already have UIDs

                        """Second Check"""  # go through leftover UIDs and create elements at approriate parent
                        # iterate through leftover UIDs and add to appropriate predecessor
                        removeUIDs = []
                        for uid in uidSet:
                            copyElem = copy.deepcopy(next(iter(foundElements)))
                            copyElem.set('uID', uid)

                            if len(preds) > 1:  # let user select from list of possible parents to add element to
                                uidTag = "{}[{}]".format(copyElem.tag, uid)
                                msg = "Element '{}' can be appended to the following parents:".format(uidTag)
                                printing.print_indexed_list(*predPaths, message=msg)
                                par_msg = "Please select a parent :".format(uidTag)
                                par_sel = prompting.user_prompt_select_options(*predPaths, message=par_msg, allow_empty=False,
                                                                               allow_multi=False)
                                p_sel = next(iter(par_sel))
                                p = preds[predPaths.index(p_sel)]
                                p.append(copyElem)

                            else:  # get only parent in list and append element
                                p = next(iter(preds))
                                p.append(copyElem)

                            # remove UID after iteration
                            removeUIDs.append(uid)

                        # remove UIDs from set
                        for uid in removeUIDs:
                            uidSet.remove(uid)
                        raise Continue

            break  # if no elements to be assigned, while loop is broken

        except Continue:  # raised execption to repeat while loop when new UIDs/elements added
            pass

    return tree


def breadth_first(tree,children=iter):
    """
    RETRIEVED FROM: http://code.activestate.com/recipes/231503-breadth-first-traversal-of-tree/
    Traverse the nodes of a tree in breadth-first order.
    The first argument should be the tree root; children
    should be a function taking as argument a tree node and
    returning an iterator of the node's children.
    """
    yield tree
    last = tree
    for node in breadth_first(tree,children):
        for child in node.getchildren():
            yield child
            last = child
        if last == node:
            return


def merge_XML_files(write_to_path, *args):
    """
    Function to merge XML files into one.

    :param write_to_path: path to resulting (merged) file
    :type basestring
    :param args: files to merge; must be existing paths
    :type basestring
    :return:
    """

    # path to XML merger script
    PATH_TO_MEGRER = r"C:\Users\aMakus\Programming\Repositories\kadmos\kadmos\packages\XML-merger\XML-merger.py"

    # ensure all file paths exist
    for file in args:
        assert os.path.exists(file), "File path {} does not exist.".format(file)

    # combine files to string
    merge_files = ' '.join(args)

    # execute merger script
    exec_comm = 'python {} {} --path {}'.format(PATH_TO_MEGRER, merge_files , write_to_path)
    os.system(exec_comm)

    return


def merge_XML_trees(*args):
    """
    This function merges the provided element trees and returns the combined tree. Because it used a pre-written function
    using the Python xml library, the tree has to be converted by printing to a string and loading from it to define the
    lxml element tree object.

    NOTE: If the same elements appear in multiple trees, the XML merger keeps the elements in the first tree and gets
    rid of the merging tree elements.

    :param args:
    :return:
    """

    # combine trees using xml merger (xml library in python is used)
    res = XMLCombiner(args).combine()

    # convert xml tree object to lxml tree object using tostring and fromstring methods
    tree_string = xml.etree.ElementTree.tostring(res.getroot(), encoding="utf-8", method="xml")
    tree = etree.ElementTree(etree.fromstring(tree_string))

    return tree


def merge_XML_trees_by_UID(*args):
    """
    This function merges the provided element trees and returns the combined tree. Because it used a pre-written function
    using the Python xml library, the tree has to be converted by printing to a string and loading from it to define the
    lxml element tree object.

    NOTE: If the same elements appear in multiple trees, the XML merger keeps the elements in the first tree and gets
    rid of the merging tree elements.

    :param args:
    :return:
    """

    # combine trees using xml merger (xml library in python is used)
    res = XMLCombiner_UID(args).combine()

    # convert xml tree object to lxml tree object using tostring and fromstring methods
    tree_string = xml.etree.ElementTree.tostring(res.getroot(), encoding="utf-8", method="xml")
    tree = etree.ElementTree(etree.fromstring(tree_string))

    return tree




def write_xml_tree_to_file(tree, path_to_file):
    """
    This function takes the XML-tree and writes it to a file in the provided directory. If the same filename already
    exists in the directory, it will be overwritten. No warnings are given.

    :param tree: XML-tree
    :type etree._ElementTree
    :param path_to_file: Full path to the file
    :type basestring
    :return:
    """

    with open(path_to_file, "a+") as f:
        f.seek(0)
        f.truncate()
        tree.write(f, xml_declaration=True, encoding='utf-8', pretty_print=True)

    return


def get_unique_file_path(path):
    """
    This function takes the filepath and returns a new filepath is it alrady exists. The new filename will be made
    unique by append and index to the old filename before extension.

    Example:
    "/path/to/file.xml" --> "/path/to/file[1].xml"

    :param path:
    :return: uniquepath
    """

    assert isinstance(path, basestring), "Argument must be string."

    idx = 0
    dirPath, file = os.path.split(path)
    spl = file.split(".")
    uniquePath = path
    while True:
        idx += 1
        if os.path.exists(uniquePath):
            uniquePath = os.path.join(dirPath, "{}[{}].{}".format(spl[0], idx, spl[1]))
        else:
            return uniquePath


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


def remove_elements_from_tree(*removeElements):
    """
    This function removes elements from their XML-tree. Tree does not have to be specifically
    indicated, as per lxml package.

    :param removeElements: Iterable of elements to remove from their tree
    :return:
    """

    for elem in removeElements:
        try:
            elem.getparent().remove(elem)
        except:
            AttributeError
