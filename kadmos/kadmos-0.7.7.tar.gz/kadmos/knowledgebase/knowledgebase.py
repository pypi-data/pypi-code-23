import inspect
import json
import networkx as nx
import os
import logging
import re
from lxml import etree

from kadmos.graph import KadmosGraph, RepositoryConnectivityGraph


# Settings for the logger
logger = logging.getLogger(__name__)


class KnowledgeBase(object):
    """
    Class that imports the data stored in a knowledge base. This is a start point for graph visualizations.
    """

    # TODO: ADD DETAILED CLASS DESCRIPTION

    def __init__(self, kb_dir_path, knowledge_base, ignoreFunctions = None):
        """
        Standard class __init__ function. Includes input checks and hardcoded values.

        :param knowledge_base: name of the folder that contains the knowledge base
        :param ignoreFunctions: list of functions to ignore from knowledge base
        """
        logger.error('Deprecation warning! The KnowledgeBase class will soon be deprecated. Use load function instead.')
        self.kb_dir = kb_dir_path # path to kb
        self.use_sensitivities = False
        self.name = knowledge_base
        if ignoreFunctions is None: ignoreFunctions = []
        self.ignoreFunctions = ignoreFunctions
        self.circularConnections = {}

        # Hardcoded values and naming convention
        self.EXEC_INFO = ["mode", "description", "precision"] # prescribed execution info
        # TODO: add option for info file checks: "fidelity", "runtime", "prog_env", "toolspecific",
        self.GEN_INFO = ["name", "version", "creator", "description"] # prescribed general info
        # TODO: add option for info file checks: , "schema_input", "schema_output"

        self.IGNORE_VALID = ['toolspecific'] # nodes to ignore in basefile validation
        self.FILEPATTERN = "(-input.xml)$|(-output.xml)$|(-info.json)$|(-sensitivities.xml)$"  # file patterns for matching
        self.BSPATTERN = "(-base.xml)$|(.xsd)$" # base and schema pattern for matching
        self.BRACKETPATTERN = re.compile('\[.*?\]') # compile bracketpattern once for faster checks of xpaths

        # check if knowledge base exists, get all files in kb directory
        self._check_knowledge_base()

        # Get the data schema in knowledge base, save in instance
        self._get_data_schema()

        # Get input and output files, save in instance
        self._get_function_files()

        # Get base file, save in instance
        self._get_base_file()

        # validate base file against provided xml schema
        #self._validate_base_against_schema(self.IGNORE_VALID)

        # validate all input and output files versus the base file
        #self._validate_function_files()

        # get all data from the input and output files, and save in instance
        self._get_function_data()

        # get graphs for all functions and save them in instance
        self.get_kb_graphs()

        # TODO: when scanning for files, make sure that filename only exists once! Check for uniqueness in name and info:name

    def _check_knowledge_base(self):
        """
        (PRIVATE) This method checks for the existence of the specified knowledge base and returns a list of all present files.
        :return: kbFiles: list of all files found in specified knowledge base directory
        """
        # assert that KnowledgeBase() input are valid
        assert isinstance(self.name, basestring), "The specified knowledge base must be a string."
        assert isinstance(self.ignoreFunctions, list), 'If specified, ignoreFunctions argument must be a list of strings.'
        assert os.path.exists(self.kb_dir), 'KNOWLEDGE_BASE directory {} does not exist!'.format(self.kb_dir)
        if self.ignoreFunctions:
            assert all([isinstance(i, basestring) for i in self.ignoreFunctions]), 'Every element in list of argument ignoreFunctions must be a string.'

        kbPath = os.path.join(self.kb_dir, self.name)

        assert os.path.exists(kbPath), 'The specified knowledge "{}" base can not be found in the knowledge base directory!'.format(kbPath)
        self.path = kbPath
        logger.info("Knowledge base '{}' found.".format(self.name))

        # Read files in the KB
        logger.info('Reading files in the knowledge base... ')
        # self.kb_files = [f for f in os.listdir(kbPath) if os.path.isfile(os.path.join(kbPath, f))]

        self.kb_files, ignoredFunctions = [], [] # initiate list of kb files, list of ignored funcs

        for file in os.listdir(kbPath): # TODO: input/output files should be indicated in info file (info becomes pivot and must be always checked)
            if os.path.isfile(os.path.join(kbPath, file)):
                match = re.search(self.FILEPATTERN, file)
                if match:
                    func = file[:-len(match.group(0))]
                    if func in self.ignoreFunctions:
                        ignoredFunctions.append(func)
                    else:
                        self.kb_files.append(file)
                else:
                    self.kb_files.append(file)

        logger.info('Successfully read the files in the knowledge base.')

        if ignoredFunctions:
            logger.info("(" + ", ".join(set(ignoredFunctions)) + ")-files are ignored from the knowledge base.")
        else:
            logger.info("All files in the knowledge base are included.")

        return

    # TODO: ensure that info file is filled in properly (syntax errors will be picked up when parsed; later need to except syntax errors)

    def _get_data_schema(self):
        """
        (PRIVATE) This function retrieves the data schema (.xsd) file from the KB folder and stores filename in instance.
        :return:  self.dataSchema
        """

        schemaPattern = "(.xsd)$"

        # Determine name of XML Schema file
        xsd_schema_found = False
        for file_name in self.kb_files:
            match = re.search(schemaPattern, file_name)
            if match and not xsd_schema_found:
                self.dataSchema = file_name
                xsd_schema_found = True
            elif match and xsd_schema_found:
                raise IOError('Multiple XML Schemas (.xsd files) found in the knowledge base ({}). '
                              'Only one .xsd file is allowed per knowledge base.'.format(self.name))
        if not xsd_schema_found:
            raise IOError('No XML Schemas (.xsd files) found in the knowledge base ({}). '
                          'One .xsd file is required per knowledge base.'.format(self.name))
        else:
            logger.info("XML Schema '{}' found.".format(self.dataSchema))

        return

    def _get_function_files(self):
        """
        (PRIVATE) This function reads input and output XML files and info json files, and saves them in self.function_files.
        It ensures that all names are according to convention.

        :return: self.function_files: dictionary containing lists of function files according to input, output, and info
        :return: self.number_of_tools: amount of tools provided in the knowledge base
        """
        # TODO: define naming convention!

        # Read input and output XML files and info json files, save them in self.function_files
        self.function_files = dict(input=[], output=[], info=[])
        if self.use_sensitivities:
            self.function_files['sensitivities'] = []


        # setup pattern for matching
        typePattern = "-[a-zA-Z]*."

        # loop through files, save them in instance, and assert naming conventions and completeness
        for file in self.kb_files:
            matchEnding = re.search(self.FILEPATTERN, file)  # match name ending
            if matchEnding:
                matchType = re.search(typePattern, matchEnding.group())
                self.function_files[matchType.group()[1:-1]].append(file)
            else:
                if not re.search(self.BSPATTERN, file):
                    logger.warning("Could not match {}, please make sure files adhere to naming conventions".format(file))


        # assert that the correct function files present, not just amount
        inout_list = ['input', 'output']
        if self.use_sensitivities:
            inout_list.append('sensitivities')

        for inout in inout_list:
            inOutfuncs = [file[:-len('-' + inout + '.xml')] for file in self.function_files[inout]]
            for file in self.function_files['info']:
                functionName = file[:-len('-info.json')]
                assert functionName in inOutfuncs, "Can not find function {0}-{1}.xml! Please check for correct spelling of info, input and output files!".format(functionName, inout)

        assert len(self.function_files['input']) == len(self.function_files['output']), 'Amount of function input and output XML files does not match.'
        assert len(self.function_files['input']) == len(self.function_files['info']), 'Amount of function input XML files and info json files does not match.'

         # check info files for name and type
        for file in self.function_files["info"]:
            with open(os.path.join(self.path, file)) as info:
                infoData = json.load(info)

        # name assertion in infoData; tool name must be string of one or more characters
        if not isinstance(infoData["general_info"]["name"], basestring):
            raise TypeError("Function name in {} must be a string.".format(file))
        if len(infoData["general_info"]["name"]) < 1:
            raise ValueError("Function name in {} must be non-empty string.".format(file))

        # save amount of tools in instance
        self.number_of_tools = len(self.function_files['info'])

        logger.info('Knowledge base files are in order.')

        if self.use_sensitivities:
            return self.number_of_tools
        else:
            return

    #TODO: check for unique function names in KB directory and info files! SHOULD BE THE SAME IN BOTH CASES? >> string.lower() should be the same >> always use the name in info-file!

    def _get_base_file(self):
        """
        (PRIVATE) This function finds the CPACS base (read-write) file and saves it to instance.
        :return: self.baseFile
        """

        # define tool file pattern for name matching, save basefile to instance
        basePattern = r"(-base.xml)$"
        self.baseFile = None
        foundBaseFile = False
        for file in self.kb_files:
            matchObj = re.search(basePattern, file)
            if matchObj and foundBaseFile == False:
                self.baseFile = file
                foundBaseFile = True
                logger.info("Base file {} found.".format(file))
            elif matchObj and foundBaseFile == True:
                raise IOError("Multiple '-base.xml' files found! Please ensure only one file present.")

        assert self.baseFile is not None, "No '-base.xml' found! Please provide a '-base.xml' file."

        return

    def _validate_base_against_schema(self, ignoreNodes=None):
        """
        (PRIVATE) Check the read-write XML file in the knowledge base against the XML Schema.
        Argument is list/tuple of nodes to ignore in validation. Root node can not be ignored.

        :param: ignoreNodes: iterable of nodes to be ignored in validation (must be list or tuple)
        :rtype: Error
        """

        # Parse the XML Schema
        xmlschema_doc = etree.parse(os.path.join(self.path, self.dataSchema))
        xmlschema = etree.XMLSchema(xmlschema_doc)

        # Parse the Read-Write File
        tree = etree.parse(os.path.join(self.path, self.baseFile))

        if ignoreNodes is not None:

            # making sure that input is iterable list or tuple, not basestring
            assert isinstance(ignoreNodes, (list, tuple)), 'Argument "ignoreNodes" not list or tuple.'

            # Remove nodes that should not be validated
            root = tree.getroot()
            for ignoreNode in ignoreNodes:
                for elem in root.iter():
                    if (elem.tag == ignoreNode) and (elem.tag != root.tag): #make sure root can not be removed
                        parent = elem.getparent()
                        parent.remove(elem)

        # TODO check TIXI validation
        # Validate XML file against the given schema
        # xmlschema.assertValid(tree) # TODO: Need to make sure that valid file is presented >> VERY IMPORTANT!!!
        # print '\n XML files successfully validated against schema. \n'

        # TODO: REMOVE THIS ONE WHEN VALIDATION WORKED OUT
        baseFileValid = xmlschema.validate(tree)
        if baseFileValid:
            print 'The base file is valid!'
        else:
            print 'Could not validate base file!'

        return

    def _validate_function_files(self):
        """
        (PRIVATE) Class method that validates all present input and output XML files by comparing each child node for
        equvalence in base file.

        :return: IOError
        """
        # TODO: this could be by simply replacing all indeces with UIDs, create sets containing ALL paths, and simply comparing the sets


        leafNodesMissing = {}
        baseTree = etree.parse(os.path.join(self.path, self.baseFile))

        print "Validating input and output XML files...",

        fileType = ['input', 'output']  #

        if self.use_sensitivities:
            fileType.append('sensitivities')

        for type in fileType:
            for xml_file in self.function_files[type]:
                fileTree = etree.parse(os.path.join(self.path, xml_file))
                for el in fileTree.iter():
                    if not el.getchildren():
                        nodeIsEquivalent = False
                        findNode = './/' + str(el.tag)
                        foundNodes = baseTree.findall(findNode)
                        if foundNodes:
                            for elem in foundNodes:
                                # compare all ancestor tags and attributes
                                nodeIsEquivalent = self._ensure_equivalent_ancestors(el, elem)
                                if nodeIsEquivalent:
                                    break

                        # add missing nodes to dict by xml file
                        if not nodeIsEquivalent:
                            if not leafNodesMissing.get(xml_file):
                                leafNodesMissing[xml_file] = []
                            leafNodesMissing[xml_file].append(fileTree.getpath(el))

        self._print_nodes(leafNodesMissing)
        assert len(leafNodesMissing) == 0, "There are missing nodes in the base file!"
        print "Complete."

    def _ensure_equivalent_ancestors(self, treeNode, baseNode):
        """
        (PRIVATE) Class method that compares all ancestors for two given nodes for tag and attribute equivalence.
        Nodes must ElementTree objects.

        :param treeNode
        :param baseNode
        :return True/False
        """

        eq = False

        # check if ancestor count is the same
        treeAnc = [i for i in baseNode.iterancestors()]
        baseAnc = [i for i in treeNode.iterancestors()]
        if len(treeAnc) != len(baseAnc):
            return eq

        # check if node tags and attributes of ancestors match; only 'uID' attribute is matched
        for i in range(len(treeAnc)):
            tagC = (baseAnc[i].tag == treeAnc[i].tag)
            attC = (baseAnc[i].attrib.get('uID') == treeAnc[i].attrib.get('uID'))
            if not tagC or not attC:
                return eq

        eq = True
        return eq

    def _print_nodes(self, obj):
        """
        (PRIVATE) Helper function to print dictionary or list hierarchically.

        :param obj: dict tor list
        """

        if type(obj) == dict:
            for k, v in obj.items():
                if hasattr(v, '__iter__'):
                    print k
                    self._print_nodes(v)
                else:
                    print '%s : %s'.format(k,v)
        elif type(obj) == list:
            for v in obj:
                if hasattr(v, '__iter__'):
                    self._print_nodes(v)
                else:
                    print v
        else:
            print obj

    def _get_function_data(self):
        """"
        (PRIVATE) This function adds a new attribute functionData to the class instance that contains all information in the knowledge base.

        functionData = [
            {
                "info": {
                                "general_info": {"name": str, "type": str, "version": float, "creator": str, "description": str},
                                "execution_info": [{"mode": str, "runtime": int, "precision": float, "fidelity": str}, ... ]
                        }
                        ,
                "input": 	{
                                "leafNodes": 	[ {"xpath": str, "tag": str, "attributes": dict, "value": str, "level": int}, ...] # list of all input leafNodes
                                "completeNodeSet": [] # list of ALL nodes (for convenience)
                                "leafNodeSet": [] # list of all leaf nodes (for convenience)
                            },
                "output": 	{
                                "leafNodes": 	[ {"xpath": str, "tag": str, "attributes": dict, "value": str, "level": int}, ...], # list of all output leafNodes
                                "completeNodeSet": [] # list of ALL nodes (for convenience)
                                "leafNodeSet": [] # list of all leaf nodes (for convenience)

                            }
            }, # tool1
            ...
        ]

        :return self.function_data
        """

        self.function_data = []

        for file in self.function_files["info"]:
            # initiate a dict for each function
            funcDict = {'info': {'general_info': {}, 'execution_info': [] }}

            with open(os.path.join(self.path, file)) as info:
                infoData = json.load(info)

            for ex in ["execution_info", "general_info"]:
                assert ex in infoData, "{}-key is missing in {}. Please check for spelling errors.".format(ex, file)

            # add function info from file to funcDict
            for inf in self.GEN_INFO: # looping through general info

                if inf == 'name':
                    # make sure that function name and type is defined, is string
                    funcName = infoData["general_info"].get(inf)
                    assert isinstance(funcName, basestring), "Function name in {} must be non-empty string!".format(file)
                    assert len(funcName)>0, "Function name in {} must be non-empty string!".format(file)

                # add info if given
                try: funcDict['info']['general_info'][inf] = infoData["general_info"].get(inf)
                except KeyError:
                    logger.warning("Function {} was not found for {} and not added to knowledge base.".format(inf, funcName))

            exInfo = infoData["execution_info"]
            assert isinstance(exInfo, list), "'execution_info' in info-file for {} must be a list.".format(funcName)
            assert len(exInfo)>0, "The {} 'execution_info' must have at least one defined mode. Please add a function mode to the info-file.".format(funcName)

            for n, modeDict in enumerate(exInfo): # looping through execution info

                assert isinstance(modeDict, dict), "Each element in 'execution_info'-list in {} must be dictionary.".format(file)

                #add mode dict to exec info
                funcDict['info']['execution_info'].append({})

                # make sure mode name is defined
                mode = modeDict["mode"]
                assert isinstance(mode, basestring), "Execution mode names in {} must be defined string(s) in the info-file.".format(file)
                assert re.match("^[a-zA-Z0-9_]+$", mode), "Execution mode name in {} must be non-empty string of alphanumeric characters (and underscore).".format(file)

                # add execution info by mode to function dictionary (if that information is provided)
                for inf in self.EXEC_INFO:
                    if inf in modeDict:
                        funcDict['info']['execution_info'][n][inf] = modeDict[inf]  # add the information to dictionary
                    else:
                        pass
                        #raise KeyError, "'{}'-information for mode {} of {} is not available in the info-file!".format(inf, mode, funcName)

            # get input and output data
            for inOut in ['input', 'output']:
                funcDict[inOut] = self._get_in_out_data(file, inOut, funcDict)

            # add function dictionary to list of function data
            self.function_data.append(funcDict)

            # check if circular coupling exists for this function
            outputSet = set(funcDict['output']['leafNodeSet'])
            for nodeDict in funcDict['input']["leafNodes"]:
                nodePath = nodeDict["xpath"]
                if nodePath in outputSet:
                    self.circularConnections[funcName] = []
                    self.circularConnections[funcName].append(nodePath)

        if self.use_sensitivities:
            return self.function_data
        else:
            return


    def print_circular_connections_in_log(self):
        """
        This function prints the circular connections present in the graph.

        :param: self.circularConnections: Dict with circular connections per tool
        :return: print to console
        """
        # TODO: this needs to be made more specific; take modes into account!!!
        cDict = self.circularConnections
        if cDict:
            print "\nWARNING: These circular connections were found: "
            for funcNode in cDict:
                print "\n{}: \n{} \n".format(funcNode, "-" * len(funcNode + ":")) + "\n".join(cDict[funcNode])
        else:
            print "No circular connections were found in knowledge base."

        return


    def _get_in_out_data(self, file, inOut, functionDict):
        """
        (PRIVATE) This helper function writes the information on all leaf nodes from the input and output XML files to a dictionary. \
        If XML file is empty, it empty dict is returned. The element paths are checked for uniqueness.

        :param file: info-file corresponding to the analyzed function
        :param inOut: must be "input" or "output"
        :param functionDict:
        :return: dataDict: dictionary containing all XPaths and leaf nodes
        """
        # initiate data dictionary
        dataDict = {"leafNodes": [], "completeNodeSet": [], "leafNodeSet": []}

        func = file[:-10] # remove -info.json to get file name
        kbFile = "{}-{}.xml".format(func, inOut)
        parseFile = os.path.join(self.path, kbFile)

        # if XML file is empty, return empty dict, else parse file
        if os.stat(parseFile).st_size == 0: # check size of file
            return dataDict
        else:
            tree = etree.parse(parseFile)

        # remove comments from tree
        comments = tree.xpath("//comment()")
        for c in comments:
            p = c.getparent()
            p.remove(c)

        # iterate through tree and add data to dict, only touch leaf nodes
        leafNodesList = []
        completeNodeList = []
        for el in tree.iter():
            data = {}
            path = tree.getpath(el)

            # add uids to xpath
            path = self._add_uids_to_xpath(path, el)

            # append path to list of all nodes
            completeNodeList.append(path)

            if not el.getchildren(): # if leaf node

                # append path to list of leaf nodes
                leafNodesList.append(path)

                # add element data to function dict
                data['xpath'] = path
                data['tag'] = el.tag
                data['attributes'] = el.attrib
                data['level'] = path.count('/') - 1
                data['value'] = el.text  # adding None if empty

                # add 'modes' attribute if it does not exist
                data['modes'] = self._get_execution_modes_for_element(el, tree, kbFile, functionDict)

                # # add 'modes' attribute if it does not exist
                # if 'modes' not in data['attributes']:
                #     data['attributes']['modes'] = '' #if 'modes' exists, it's a string, otherwise empty string
                #     # TODO: check parents iteratively to check if they have modes attribute >> will take a lot of time/iterations!

                # remove whitespace from start/end of string, or add None
                if el.text is not None:
                    data['value'] = el.text.strip()
                else:
                    data['value'] = el.text  # adding None if empty

                # some sensitivities stuff (ASK MENCO SCHUURMAN)
                if inOut == 'sensitivities':
                    data['xpath_output'] = tree.getpath(el.getparent().getparent()).replace("sensitivities", "analyses")

                # add element data to data dict
                dataDict['leafNodes'].append(data)

        # add complete list of input/output nodes (for convenience, performance later on)
        dataDict["leafNodeSet"] = set(leafNodesList)

        # add list of ALL nodes to dictionary
        dataDict["completeNodeSet"] = set(completeNodeList)

        # check if toolspecific nodes found in file
        if any("toolspecific" in node for node in dataDict["leafNodeSet"]):
            logger.warning("'toolspecific' nodes found in {}".format(kbFile))

        return dataDict


    def _get_execution_modes_for_element(self, element, tree, file, functionDict):
        """
        (PRIVATE) This function retrieves the modes attribute of the child node or of its ancestors. If multiple modes
        are defined in its ancestry, a warning is given and only the lowest modes definition is returned. Ancestry is
        checked for 'modes' attributes regardless of whether it is present in it leaf-node or not.
        Once the modes are retrieved, they are checked for validity (present in info-file) and "negativity" (mode
        attributes can either be positive or negative). NOTE: If no modes are given in a leaf-node, this node is applied
        to ALL function modes.

        :param element: xml element, leaf-node
        :param tree: element tree of the current element
        :param file: file that is currently analyzed
        :param functionDict: data dict containing execution and info data
        :return: execModes: string containing all function modes applied to this element
        """
        # get element xpath
        elementPath = tree.getpath(element)

        # get function modes from info file and assert that they are unique
        funcModes = [execDict['mode'] for execDict in functionDict['info']['execution_info']]
        execModes = '' # NOTE: if no modes indicated, all modes are applied to node
        modesFound = False

        if 'modes' in element.attrib and re.search("[^\s]", element.attrib['modes']): # if 'modes' key present and has characters
            assert isinstance(element.attrib['modes'], basestring), "If provided, modes-attribute of elemeent {} in {} must be of type string.".format(elementPath, file)
            execModes = element.attrib['modes']
            modesFound = True

        for anc in element.iterancestors():
            if 'modes' in anc.attrib  and re.search("[^\s]", anc.attrib['modes']):
                if not modesFound:
                    modesFound = True
                    execModes = anc.attrib['modes']
                else:
                    print "WARNING: Multiple 'modes' attributes found in ancestry of element {} in {}; lowest one is applied.".format(elementPath, file)
                    break

        if re.search("[^\s]", execModes):  # if contains any characters

            # get all modes
            modesList = execModes.split()

            # check if modes negative (all either negative or positive)
            modesNegative = False
            negPattern = "^-"
            if any(re.search(negPattern, mode) for mode in modesList):
                modesNegative = True

                assert all(re.search(negPattern, mode) for mode in modesList), \
                    "Either all or none of the 'modes'-attributes of element {} in {} must be negative!".format(elementPath, file)

            # check if each mode is valid (use its positive if modesNegative)
            for mode in modesList:
                if modesNegative:
                    assert mode[1:] in funcModes, "Execution mode '{}' of node {} (or its ancestor) in {} was not found in the info-file. Please check spelling or alter info-file.".format(mode[1:], elementPath, file)
                else:
                    assert mode in funcModes, "Execution mode '{}' of node {} (or its ancestor) in {} was not found in the info-file. Please check spelling or alter info-file.".format(mode, elementPath, file)

        return execModes


    def _add_uids_to_xpath(self, xpath, element):
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

        # get elements in xpath and reverse list for easier operation with ancestors
        path_elems = xpath.split('/')[1:]
        rev_path_elems = list(reversed(path_elems))

        # if element has UID attribute, add it to xpath element
        if element.get('uID'):

            # remove existing index-bracket, if present; add uid to element
            cleanElem = self.BRACKETPATTERN.sub("", rev_path_elems[0])
            rev_path_elems[0] = '{}[@uID="{}"]'.format(cleanElem, element.get('uID'))

        # loop through ancestors, check for uid attribute
        for idx, anc in enumerate(element.iterancestors()):

            # if uid attribute present, add to appropriate element
            if anc.get('uID') is not None:

                # remove any existing index-brackets; add uid to element
                cleanElem = self.BRACKETPATTERN.sub("", rev_path_elems[idx+1])
                rev_path_elems[idx+1] = '{}[@uID="{}"]'.format(cleanElem, anc.get('uID'))

        # join elements to uid-xpath
        uid_xpath = "/" + "/".join(reversed(rev_path_elems))

        return uid_xpath


    def _replace_indeces_in_element_xpath(self, xpath, element):
        """
        (PRIVATE) This function takes a CPACS xpath and replaces its indeces with UIDs. The search-pattern
        matches all integers between squared brackets. If matched on a given node, that node is searched for a UID
        using etree.iterancestors() and self._get_element_uID(), and its index is replaced by the found UID in the xpath.
        If no UID is found, the index is not replaced.

        :param xpath: Argument must be a CPACS xpath (string)
        :param element: Argument must be lxml etree element
        :return:
        """

        # check if xpath has indeces, e.g. ".../wing[1]/...", replace them w/ UIDs
        indexPattern = ('\[[0-9]+\]')
        match = re.search(indexPattern, xpath)
        loopCount = 0 # to prevent overflow
        precedingPathLen = 0  # changes during loop, different for each re.search()

        """
        This while loop iterates through the provided xpath and replaces the LEFTMOST index match in each iteration,
        as dictated by re.search(). In the following iteration, the matching proceeds from the end of the previous
        match-index in the string.
        """
        while match:
            elUID = match.group(0)[1:-1] # matched index to replace if UID is found
            matchStart = precedingPathLen + match.start(0)
            matchEnd = precedingPathLen + match.end(0)

            # count "/" to check how many ancestors to iterate through
            childCount = xpath[matchEnd:].count("/")

            # get UID of matched parent node
            if childCount < 1:  # if leaf node
                UIDfound = self._get_element_uID(element)
                if UIDfound is not None:
                    elUID = UIDfound
                else:
                    allElemUIDsProvided = False
            else:
                ancCount = 0
                for anc in element.iterancestors():
                    ancCount += 1
                    if ancCount == childCount:
                        UIDfound = self._get_element_uID(anc)
                        if UIDfound is not None:
                            elUID = UIDfound
                        else:
                            allElemUIDsProvided = False
                        break

            idxReplace = "[{}]".format(elUID)
            xpath = xpath[:matchStart] + idxReplace + xpath[matchEnd:]

            """
            >>  precedingPathLen implemented b/c re.search() will always show first match; if index can not be
                replaced by UID (because identifier not provided), it will always be returned by re.search().
            >>  string matching starts where last match ended!
            """

            # perform re.search() from replaced index onwards
            precedingPathLen = len(xpath[:matchStart]) + len(idxReplace)
            match = re.search(indexPattern, xpath[precedingPathLen:])

            # just in case to prevent an overflow
            loopCount += 1
            if loopCount > 30:
                break

        return xpath

    def _get_element_uID(self, element):
        """
        (PRIVATE) This function takes an element and returns its UID attribute, or the value of a child UID-element (a child-node containing "UID" in its tag).
        Most CPACS nodes with multiplicity have a UID attribute, however some carry UID-information in a child element.
        The "IDENT_KEYWORDS"-list contains the attributes that are checked for the UID-string. The node element is checked for
        UID-info in the order of the attribute in that list. If a UID is found, it is immediately returned. Otherwise, None is returned.

        :param element: Argument must be lxml etree element
        :return: UID-string or None: If a UID is found, it is returned. Otherwise, None.
        """

        IDENT_KEYWORDS = ["uID","name"]

        if any(kw in element.attrib for kw in IDENT_KEYWORDS):
            for attr in IDENT_KEYWORDS:
                try:
                    attribute = element.attrib[attr]
                    return attribute
                except KeyError:
                    continue
        else:
            for child in element.iterchildren(): # TODO: This should not apply normally/legally
                if "UID" in child.tag.upper():
                    attribute = child.text
                    return attribute

        return


    def get_kb_graphs(self):
        """
        This class method generates all graphs for all present functions in the knowledge base.

        :return: self.functionGraphs
        """
        # get list of all functions in KB
        funcList = [self.function_data[i]['info']["general_info"]['name'] for i in range(len(self.function_data))]

        #initiate list of function graphs and add graphs to it
        graphList = []
        for func in funcList:
            graphList.append(self.get_function_graph(func))

        self.functionGraphs = graphList
        return


    def get_function_graph(self, funcName, inOut=None):
        """
        This function builds a directed graph (KadmosGraph object) for the specified function using the "networkx" package. If inOut
        argument is specified, only the input or output of the function will be included in the graph, otherwise both.

        :param: funcName: function name for which the graph is generated; must be present in knowledge base.
        :param: inOut: default = None; if specified, must be "input" or "output" string. Specification of this argument enables the generation of the function graph with only input or output variables.
        :return: functionGraph
        """

        """
        LIST OF ASSERTIONS
        >> Function name must be string.
        >> Input/Output-variable must be string, spelled correctly.
        >> "modes" attribute in node must be string.
        >> All given modes in "modes" attribute must be either positive or negative.
        >> All given modes must be in each node must be in provided in execution_info in XXX-info.json
        >>
        """

        assert isinstance(funcName, basestring), 'Provided function name must be a string!'

        # assert funcName exists and get index of function in self.function_data list
        funcIndex = None
        for idx, funcDict in enumerate(self.function_data):
            if funcDict['info']['general_info']['name'] == funcName:
                funcIndex = idx #funcIndex is index of the function in list
                break
        assert funcIndex is not None, "The provided function name can not be found in knowledge base."

        # assert inOut, if defined, is string and either input or output
        if inOut is not None:
            assert isinstance(inOut, basestring), "inOut argument must be a string if specified."
            assert inOut.lower() in ["input", "output"], "inOut argument must be either 'input' or 'output'."
        else:
            inOut = ["input", "output"]

        # initiate directed graph and list of edges
        DG, edgeTpls = KadmosGraph(), []

        # get all execution modes for the function from function info
        funcModes = set([infoDict['mode'] for infoDict in funcDict['info']['execution_info']])

        for io in inOut:

            for nodeDict in funcDict[io]['leafNodes']:
                modesAttr = nodeDict['modes']
                node = nodeDict['xpath']

                assert isinstance(modesAttr, basestring), "The 'modes' attribute of the {}-node {} of {} must be a string.".format(io, node, funcName)

                if re.search("[^\s]", modesAttr): #if contains any characters

                    # get all modes
                    nodeModes = modesAttr.split()

                    # check if modes negative (all either negative or positive)
                    modesNegative = False
                    negPattern = "^-"
                    if any(re.search(negPattern, mode) for mode in nodeModes):
                        modesNegative = True
                        assert all(re.search(negPattern, mode) for mode in nodeModes), "Either all or none of the modes in the {} {}-node {} must be negative!".format(funcName, io, node)

                        # make sure that all modes in list "positive" for later processing; remove minus sign
                        # (modesNegative ensures that modes are still regarded as negative)
                        for i, mode in enumerate(nodeModes):
                            nodeModes[i] = mode[1:]

                    # check if modes are valid
                    for mode in nodeModes:
                        assert mode in funcModes, "The execution mode '{}' as used in the {} {}-node {} was not found in the info-file. Please check spelling or alter info-file.".format(mode, funcName, io, node)

                    # add node to the indicated nodes
                    if modesNegative:
                        # add to all modes but the ones indicated
                        addModes = [mode for mode in funcModes if not mode in nodeModes]
                    else:
                        # add to all modes the ones indicated
                        addModes = list(set(nodeModes) & set(funcModes))

                else:
                    # add to all modes!
                    addModes = list(funcModes)

                # add edge tuple for the node and function
                edgeTpls += self._create_edge_tuples(funcName, funcModes, io, node, addModes)

        DG.add_edges_from(edgeTpls)

        # add node attributes to graph
        self._add_node_attribs(funcDict, funcName, funcModes, DG)

        DG.name = funcName
        DG.graph['kb_path'] = self.path

        return DG

    def get_function_dependencies(self, funcName, mode, inOut=None):
        """
        This function builds a directed graph (KadmosGraph object) for the specified function using the "networkx" package. If inOut
        argument is specified, only the input or output of the function will be included in the graph, otherwise both.

        :param: funcName: function name for which the graph is generated; must be present in knowledge base.
        :param: inOut: default = None; if specified, must be "input" or "output" string. Specification of this argument enables the generation of the function graph with only input or output variables.
        :return: functionGraph
        """

        """
        LIST OF ASSERTIONS
        >> Function name must be string.
        >> Input/Output-variable must be string, spelled correctly.
        >> "modes" attribute in node must be string.
        >> All given modes in "modes" attribute must be either positive or negative.
        >> All given modes must be in each node must be in provided in execution_info in XXX-info.json
        >>
        """

        assert isinstance(funcName, basestring), 'Provided function name must be a string!'

        # assert inOut, if defined, is string and either input or output
        if inOut is not None:
            assert isinstance(inOut, basestring), "inOut argument must be a string if specified."
            assert inOut.lower() in ["input", "output"], "inOut argument must be either 'input' or 'output'."
        else:
            inOut = ["input", "output"]

        # get all execution modes for the function from function info
        funcDict = dict()
        funcDict[inOut] = self._get_in_out_data(file, inOut, funcDict)

        for io in inOut:
            funcDict[io] = []
            funcDict[io]['leafNodes'] = []

            for nodeDict in funcDict[io]['leafNodes']:
                modesAttr = nodeDict['modes']
                node = nodeDict['xpath']

                assert isinstance(modesAttr, basestring), "The 'modes' attribute of the {}-node {} of {} must be a string.".format(io, node, funcName)

                if re.search("[^\s]", modesAttr): #if contains any characters

                    # get all modes
                    nodeModes = modesAttr.split()

                    # check if modes negative (all either negative or positive)
                    modesNegative = False
                    negPattern = "^-"
                    if any(re.search(negPattern, mode) for mode in nodeModes):
                        modesNegative = True
                        assert all(re.search(negPattern, mode) for mode in nodeModes), "Either all or none of the modes in the {} {}-node {} must be negative!".format(funcName, io, node)

                        # make sure that all modes in list "positive" for later processing; remove minus sign
                        # (modesNegative ensures that modes are still regarded as negative)
                        for i, mode in enumerate(nodeModes):
                            nodeModes[i] = mode[1:]

                    # check if modes are valid
                    for mode in nodeModes:
                        assert mode in funcModes, "The execution mode '{}' as used in the {} {}-node {} was not found in the info-file. Please check spelling or alter info-file.".format(mode, funcName, io, node)

                    # add node to the indicated nodes
                    if modesNegative:
                        # add to all modes but the ones indicated
                        addModes = [mode for mode in funcModes if not mode in nodeModes]
                    else:
                        # add to all modes the ones indicated
                        addModes = list(set(nodeModes) & set(funcModes))

                else:
                    # add to all modes!
                    addModes = list(funcModes)

                # add edge tuple for the node and function
                edgeTpls += self._create_edge_tuples(funcName, funcModes, io, node, addModes)

        DG.add_edges_from(edgeTpls)

        # add node attributes to graph
        self._add_node_attribs(funcDict, funcName, funcModes, DG)

        DG.name = funcName
        DG.graph['kb_path'] = self.path

        return DG

    # TODO: assert that modes attr is string
    # TODO: ensure that modes are unique! (info-file)
    # TODO: functionality to ignore certain running modes; similar to ignoreList function
    # TODO: ensure that execution info in info file is provided according to self.EXECINFO and in the right format

    def _create_edge_tuples(self, funcName, funcModes, inOut, node, addModes):
        """
        (PRIVATE) This helper function creates a list of edge tuples in order to generate a graph.

        :param funcIndex: index of function in list of tool dicts in self.function_data
        :param inOut: specified whether input or output nodes, None adds all to graph
        :return: graphEdges: list of edges to build graph
        """
        # initiate list of tuples
        tpls = []

        for mode in addModes:

            # if more than one mode, use mode in brackets
            if len(funcModes) > 1:
                funcLabel = '{}[{}]'.format(funcName, mode)
            else:
                funcLabel = funcName

            # determine whether input or output node
            if inOut.lower() == 'input':
                tpl = (node, funcLabel)
            else:
                tpl = (funcLabel, node)

            tpls.append(tpl)

        return tpls

    def _add_node_attribs(self, funcDict, funcName, funcModes, G):
        """
        (PRIVATE) Function that adds node attributes to the nodes of the graph.

        :param funcIndex: index of function in list of tool dicts in self.function_data
        :param G: Graph w/o attribs
        :return: G: Graph w/ attribs
        """

        for node in G.nodes():
            if re.match(funcName, node): # if node matches function name

                # add attributes to node
                G.node[node]['category'] = 'function'
                G.node[node]['label'] = node
                G.node[node]['name'] = funcName
                # For now the creator is ignored. This should be done when the KB can read CMDOWS files
                # creator = funcDict.get('info', {}).get('general_info', {}).get('creator', '')
                # G.node[node]['general_info'] = {'creator': {'contact': {'name': creator}}}
                G.node[node]['general_info'] = {}

                # check if node has brackets to retrieve mode
                modePattern = "\[.+\]"
                match = re.search(modePattern, node)
                if match:
                    fMode = match.group(0)[1:-1] # take matching string and remove brackets
                    assert fMode in funcModes, 'Something went wrong! Could not find execution mode {} for {} in list of execution modes.'.format(fMode, funcName)
                else:
                    fMode = next(iter(funcModes)) # get only element in set

                # loop over execution modes of function
                for execMode in funcDict['info']['execution_info']:
                    if fMode == execMode['mode']:

                        # loop over execution info and add the provided information to node; raise error if info missing
                        for info in self.EXEC_INFO:
                            if info in execMode:
                                G.node[node][info] = execMode[info]
                            else:
                                pass
                                #raise KeyError, "{} information for mode {} of {} is not available in knowledgebase-object!".format(info, execMode, funcName)

            else: # otherwise variable node # TODO: add elif node in [list of leafnodes]

                # add attributes to node
                G.node[node]['category'] = 'variable'
                G.node[node]['label'] = node.split('/')[-1]
                G.node[node]['level'] = node.count('/') - 1
                G.node[node]['execution_time'] = 1 # TODO: this is not really needed for nodes

        return G

    def get_rcg(self, name='RCG'):
        """
        Function to create Maximal Connectivity Graph (Pate, 2014) by composing a list of graphs.

        :return: maximal connectivity graph (RCG)
        """

        logger.error('Deprecation warning! The KnowledgeBase class will soon be deprecated. Use load function instead.')

        functionGraphs = self.functionGraphs

        MCG = RepositoryConnectivityGraph()  # initialize RCG

        logger.info('Composing RCG...')
        for g in functionGraphs:
            MCG = nx.compose(MCG, g)
        logger.info('Successfully composed RCG.')

        # Add kb_path attribute
        MCG = RepositoryConnectivityGraph(MCG, kb_path=self.path, name=name) # TODO: check why this is necessary!
        MCG = RepositoryConnectivityGraph(MCG, kb_path=self.path)
        MCG.name = "{}-Graph".format(self.name)

        # Move some elements in the node dictionary
        # TODO: In the end the information should be in the right location in the KB files already
        for function_node in MCG.get_function_nodes():
            MCG.node[function_node]['general_info'].update({'description': MCG.node[function_node].get('description')})
            try:
                del MCG.node[function_node]['description']
            except KeyError:
                pass

        return MCG
