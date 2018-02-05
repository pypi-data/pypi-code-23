import os
import datetime
import json
from lxml import etree
import matlab.engine as ME

import mapping as MU
import prompting as PRO
import printing as PRI


def parse_schematic_io_files(graph, tool_sequence, schema_files_dir_path):
    """
    Function to load and parse schematic input and output files for each tool in tool sequence.

    :return:
    """

    # save schema in dict in order to avoid reloading tree
    schemaTreeDict = {}
    for func in tool_sequence:

        # get tool name and execution mode
        tool = graph.node[func]['name']
        mode = graph.node[func]['mode']

        # get schema files for tools; assert schema file/tree present
        if (tool, mode) not in schemaTreeDict:
            schemaTreeDict[(tool, mode)] = {}

            # loop through files in schema dir and find relevant -info.xml to retrieve file info
            for file in os.listdir(schema_files_dir_path):
                if file.endswith("-info.json"):
                    with open(os.path.join(schema_files_dir_path, file)) as info:
                        infoData = json.load(info)
                        if infoData['general_info']['name'] == tool:
                            inFile = os.path.join(schema_files_dir_path, infoData['general_info']['schema_input'])
                            outFile = os.path.join(schema_files_dir_path,
                                                   infoData['general_info']['schema_output'])
                            schemaTreeDict[(tool, mode)]['input'] = MU.filter_tree_by_modes(etree.parse(inFile),
                                                                                            [mode])
                            schemaTreeDict[(tool, mode)]['output'] = MU.filter_tree_by_modes(etree.parse(outFile),
                                                                                             [mode])
                            break
        assert schemaTreeDict[(tool, mode)], "Something went wrong! Could not parse schematic XMLs for {}[{}]!".format(
            tool, mode)

    return schemaTreeDict


def load_mapping_dict(schema_files_dir_path, schemaTreeDict):
    """
    This function loads and checks the mapping dict for completeness. If any UID-items (link-nodes) in the schematic
    tree is not present in the dict, user is asked to provide mapping.

    Note: Only inputs are checked at the moment!

    :param: schema_files_dir_path: path to schematic files directory
    :param: schemaTreeDict
    :return: MAPPING_DICT: dictionary containing all mappings
    """

    # HARDCODE
    MAPPING_FILE = '-map.json'  # file ending of mapping dict

    # load mapping file
    mapfile = None
    for file in os.listdir(schema_files_dir_path):
        if file.endswith(MAPPING_FILE):
            mapfile = file
            break
    assert mapfile, "Could not find '{}'-file in '{}'.".format(MAPPING_FILE, schema_files_dir_path)

    # Load and parse mapping dict
    mapping_file_path = os.path.join(schema_files_dir_path, mapfile)
    assert os.path.exists(mapping_file_path)

    print "\nChecking mapping-dict for completeness..."

    # loop through trees and check if all nodes UID-item paths in mapping-dict
    missingNodes = set([])
    while True:
        with open(mapping_file_path) as mData:
            MAPPING_DICT = json.load(mData)['MAPPING_DICT']
            mData.close()

        for tool_mode in schemaTreeDict:
            for io in ["input","output"]:
                schematicTree = schemaTreeDict[tool_mode][io]
                missingNodes = missingNodes.union(mapping_dict_missing_nodes(MAPPING_DICT, schematicTree))

        # print warning
        if missingNodes:
            msg = "WARNING - The following link paths are not present in 'mapping dict': "
            PRI.print_indexed_list(*missingNodes, message=msg)

            mssg = "Reload?"
            sel = PRO.user_prompt_yes_no(message=mssg) #TODO:DEMO
            # sel = 0

            if sel:
                continue
            else:
                break
        else:
            print "NOTE - All links present in mapping dict."
            break


    return MAPPING_DICT


def mapping_dict_missing_nodes(mapping_dict, tree):
    """
    This function checks whether all UID-items in the tree are present in mapping_dict.

    :param mapping_dict:
    :param tree:
    :return: True; missingItems (list of paths missing)
    """

    # iterate tree and check whether all UID-items can be found in mapping dict
    missingItems = []
    for elem in tree.iter():
        if MU.element_is_UID_item(elem):
            elemPath = MU.xpath_to_clean_xpath(tree.getpath(elem))
            if elemPath not in mapping_dict:
                missingItems.append(elemPath)

    return missingItems



def execute_tool(tool_name, execution_mode, exec_element_tree):
    """
    This function calls the appropriate execution function according to the execution environment (PYTHON, MATLAB, etc).

    :param tool_name:
    :param execution_mode:
    :param exec_element_tree:
    :return:
    """

    # define tool exec environments
    MATLAB_TOOLS = ['Q3D','EMWET']
    PYTHON_TOOLS = ['HANGAR', 'OBJ', "GACA", "SCAM", "SMFA", "MTOW", "CNSTRNT"]

    # check if execution in matlab or python; call function according to outcome
    output_file_path = None
    if tool_name in MATLAB_TOOLS:
        output_file_path = execute_tool_in_matlab(tool_name, execution_mode, exec_element_tree, connect_to_engine=None)
    elif tool_name in PYTHON_TOOLS:
        output_file_path = execute_tool_in_python(tool_name, execution_mode, exec_element_tree)
    else:
        print 'WARNING: Could not find tool {} in any execution environment. Please define or add tool to existing one.'.format(tool_name)

    return output_file_path


def execute_tool_in_matlab(tool, execution_mode, exec_element_tree, connect_to_engine=None):
    """
    In this function, the MATLAB tool is executed. First, a shared matlab engine is connected to, or created if no
    connection possible. The XML tree for tool execution is written to the corresponding input file in the relevant
    directory.

    :param tool:
    :param mode:
    :param input_file_path:
    :return: output file path
    """

    # define tool working_dir on machine
    TOOL_WORKING_DIR = {'Q3D': r'C:\Users\aMakus\Programming\Repositories\agile_tools\agile-programs\RCE_Q3D_tool',
                      'EMWET': r'C:\Users\aMakus\Programming\Repositories\agile_tools\agile-programs\RCE_EMWET_tool'}

    EXEC_FILE = {'Q3D':'WF_Q3D_RCE.m', 'EMWET':'WF_EMWET_RCE.m'}

    INPUT_FILE = {'EMWET': 'tool_in.xml', "Q3D": "tool_in.xml"}

    OUTPUT_FILE = {'EMWET': 'tool_out.xml', 'Q3D': 'tool_out.xml'}

    SETTINGS = "settings.m"

    # assert arguments
    if connect_to_engine is not None:
        assert isinstance(connect_to_engine(), basestring), "Argument must be of type string."

    # get tool working_dir and exec file
    working_dir = TOOL_WORKING_DIR[tool]
    exec_file = EXEC_FILE[tool]  # execution file must be present in working_dir directory

    # change settings file for execution
    settingsFile = os.path.join(working_dir, SETTINGS)
    searchLine = "TSI.toolmode"
    replaceline = "TSI.toolmode = '{}';\n".format(execution_mode)
    replace_lines_in_file(settingsFile, searchLine, replaceline)

    # write execution tree to input file
    input_file_path = os.path.join(TOOL_WORKING_DIR[tool], INPUT_FILE[tool])
    MU.write_xml_tree_to_file(exec_element_tree, input_file_path)

    # assert that exec file exists in working_dir
    assert os.path.exists(os.path.join(working_dir, exec_file)), 'Execution file {} not found in {}.'.format(exec_file, working_dir)

    # launch/connect to matlab engine
    eng = connect_to_matlab_engine(connect_to_engine)
    assert eng is not None, "Python failed to connect to MATLAB engine. Launch MATLAB and type 'matlab.engine.shareEngine' for safe connect."

    # change into working dir (should be done before every execution)
    eng.cd(working_dir)

    # execution command; note that 'eng' is the connected matlab engine var
    exec_comm = 'eng.{}(nargout=0)'.format(exec_file.split('.')[0])  # exec_file must be w/o '.m'
    exec(exec_comm)  # execute tool

    return os.path.join(TOOL_WORKING_DIR[tool], OUTPUT_FILE[tool])


def connect_to_matlab_engine(connect_to_engine=None):
    """
    This function connects the python session to a shared matlab engine and returns this engine instance.

    :param connect_to_engine:
    :return:
    """

    eng = None  # init engine

    # connect to provided engine if possible
    if connect_to_engine is not None:
        try:
            eng = ME.connect_matlab(connect_to_engine)  # connects to provided engine
        except ME.EngineError:
            print 'WARNING: Cannot connect to provided MATLAB engine {}.'.format(connect_to_engine)

    # if no engine connected, find one to connect to or start another one
    # ME.connect_matlab() connects to the first shared engine it finds, or starts new shared egnine if none found
    # it is recommended to launch matlab manually and type 'matlab.engine.shareEngine' in command line to share
    if eng is None: # TODO: rewrite using find_matlab first, before trying to connect new session
        try:
            print "\nThe following shared sessions found: {}".format(ME.find_matlab())
            eng = ME.connect_matlab()  # if connect fails, start new engine
        except ME.EngineError:
            print "\nFailed to connect to found engines. Starting new shared engine..."
            eng = ME.start_matlab()

    print "\nConnected to engine 'MATLAB_{}'.\n".format(int(eng.feature('GetPid')))
    return eng


def execute_tool_in_python(tool, mode, exec_element_tree):
    """
    In this function, the Python tool is executed.

    :param tool:
    :param mode:
    :param exec_element_tree:
    :return: output file path
    """

    # define/store tool working dict, execution file
    TOOL_WORKING_DIR = {'HANGAR': r'C:\Users\aMakus\Programming\Repositories\agile_tools\agile-programs\RCE_HANGAR_tool',
                        'OBJ': r'C:\Users\aMakus\Programming\Repositories\agile_tools\agile-programs\RCE_OBJ_tool',
                        "GACA":r"C:\Users\aMakus\Programming\Repositories\agile_tools\agile-programs\RCE_GACA_tool",
                        "SCAM": r"C:\Users\aMakus\Programming\Repositories\agile_tools\agile-programs\RCE_SCAM_tool",
                        "SMFA": r"C:\Users\aMakus\Programming\Repositories\agile_tools\agile-programs\RCE_SMFA_tool",
                        "MTOW": r"C:\Users\aMakus\Programming\Repositories\agile_tools\agile-programs\RCE_MTOW_tool",
                        "CNSTRNT": r"C:\Users\aMakus\Programming\Repositories\agile_tools\agile-programs\RCE_CNSTRNT_tool"
                        }

    EXEC_FILE = {'HANGAR': 'HANGAR.py',
                 'OBJ': 'OBJ.py',
                 "GACA": 'GACA.py',
                 "SCAM": 'SCAM.py',
                 "SMFA": 'SMFA.py',
                 "MTOW": 'MTOW.py',
                 "CNSTRNT": 'CNSTRNT.py'
                 }

    INPUT_FILE = {'HANGAR': 'tool_in.xml',
                 'OBJ': 'OBJ-input.xml',
                 "GACA": 'CAGAarea-input.xml',
                 "SCAM": 'SCAM-input.xml',
                 "SMFA": 'SCAM-input.xml',
                 "MTOW": 'MTOW-input.xml',
                 "CNSTRNT": 'CNSTRNT-input.xml'
                  }

    OUTPUT_FILE = {'HANGAR': 'tool_out.xml',
                 'OBJ': 'tool_out.xml',
                 "GACA": 'tool_out.xml',
                 "SCAM": 'tool_out.xml',
                 "SMFA": 'tool_out.xml',
                 "MTOW": 'tool_out.xml',
                 "CNSTRNT": 'tool_out.xml'
                   }

    # get paths to dir and exec file
    working_dir = TOOL_WORKING_DIR[tool]
    exec_file = EXEC_FILE[tool]
    path_to_exec = os.path.join(working_dir, exec_file)

    # write execution tree to input file
    input_file_path = os.path.join(TOOL_WORKING_DIR[tool], INPUT_FILE[tool])
    MU.write_xml_tree_to_file(exec_element_tree, input_file_path)

    # assert that exec file exists in working_dir
    assert os.path.exists(path_to_exec), 'Execution file {} not found in {}.'.format(exec_file, working_dir)

    # execute tool
    exec_comm = 'python {} {}'.format(path_to_exec, input_file_path)
    print "\nRunning {} in {} mode...".format(tool, mode)
    os.system(exec_comm)

    return os.path.join(TOOL_WORKING_DIR[tool], OUTPUT_FILE[tool])


def create_cpacs_basefile(path_to_dir, file_name):
    """
    This function takes creates the "/cpacs" root and adds the header to an element tree, then writes these to a file to
    generate the cpacs base-file.

    :param path_to_dir: path to directory in which to create the base file
    :type basestring
    :param file_name: name of the base file
    :type basestring
    :return: path to base file
    :rtype basestring
    """

    # HARDCODE
    NAME = "some Name"
    VERSION = 1.0
    CPACSVERSION = 2.3
    CREATOR = "TUD"
    DESCRIPTION = "some description"

    ROOT = "cpacs"
    HEADER = "header"


    # define header info
    headerInfo = {  "name":NAME,
                    "version": unicode(VERSION),
                    "cpacsVersion":unicode(CPACSVERSION),
                    "creator":CREATOR,
                    "description": DESCRIPTION,
                    "timestamp": unicode(datetime.datetime.utcnow())
                    }

    # Create the root element
    root = etree.Element(ROOT)

    # Make a new document tree
    tree = etree.ElementTree(root)

    # add header sub element
    header = etree.SubElement(root, HEADER)

    # loop through info items and add them to header element
    for item, value in headerInfo.iteritems():
        infoItem = etree.SubElement(header, item)
        infoItem.text = value

    # make sure base file name ends with -base.xml
    baseXtension = "-base"
    suffix = ".xml"
    fname = file_name.split('.')[0] + baseXtension + suffix
    path_to_file = os.path.join(path_to_dir, fname)

    # write tree to file
    MU.write_xml_tree_to_file(tree, path_to_file)

    return os.path.join(path_to_dir, fname)


def replace_lines_in_file(filepath, linestr, replace):
    """
    This function is written to replace certain lines in the settings file of a MATLAB tool. It scans through the file
    line by line and checks whether the 'linestr' argument is found in that line. If it is, the complete line is
    replaced with the 'replace' argument.

    :param filepath:
    :param linestr:
    :param replace:
    :return:
    """

    # Read in the file
    lines = []
    with open(filepath) as infile:
        for line in infile:
            if linestr in line:
                line = line.replace(line[:], replace)
            lines.append(line)
    with open(filepath, 'w') as outfile:
        for line in lines:
            outfile.write(line)

    return



"""
The function below was my first attempt at implementing Basefile generation and input/output file extraction.
It's only kept for reference.

"""


# def execute_FPG_combination(FPG, tool_order, schema_files_dir_path, spec_files_dir_path, basefile_name=None, print_details=True):
#     pass
#
#     # HARDCODE
#     MAPPING_FILE = '_UID_-map.json'
#
#     # Load and pare mapping dict
#     mapping_file_path = os.path.join(schema_files_dir_path, MAPPING_FILE)
#     assert os.path.exists(mapping_file_path)
#     with open(mapping_file_path) as mData:
#         MAPPING_DICT = json.load(mData)['MAPPING_DICT']
#
#
#     ############
#
#     """[STEP 1]""" # create basefile and load all other relevant files (schema, info)
#     # create base file in specific files dir
#     if basefile_name is None:
#         basefile_name = os.path.basename(spec_files_dir_path)
#     basefile_path = create_cpacs_basefile(spec_files_dir_path, basefile_name)
#     baseTree = etree.parse(basefile_path)
#
#     # iterate through ordered combo and execute tools; read and write basefile
#     schemaTreeDict = {}  # save schema in dict in order to avoid reloading tree
#     for func in tool_order:
#
#         # get tool name and execution mode
#         tool = FPG.node[func]['name']
#         mode = FPG.node[func]['mode']
#
#         """[STEP 2]""" # get schema files for tools; assert schema file/tree present
#         if (tool, mode) not in schemaTreeDict:
#             schemaTreeDict[(tool, mode)] = {}
#
#             # loop through files in schema dir and find relevant -info.xml to retrieve file info
#             for file in os.listdir(schema_files_dir_path):
#                 if file.endswith("-info.json"):
#                     with open(os.path.join(schema_files_dir_path, file)) as info:
#                         infoData = json.load(info)
#                         if infoData['general_info']['name'] == tool:
#                             inFile = os.path.join(schema_files_dir_path, infoData['general_info']['schema_input'])
#                             outFile = os.path.join(schema_files_dir_path, infoData['general_info']['schema_output'])
#                             schemaTreeDict[(tool, mode)]['input'] = MU.filter_tree_by_modes(etree.parse(inFile), [mode])
#                             schemaTreeDict[(tool, mode)]['output'] = MU.filter_tree_by_modes(etree.parse(outFile), [mode])
#                             break
#         assert schemaTreeDict[(tool, mode)], "Something went wrong! Could not find schema XMLs in info-file!"
#
#     """[STEP 2.5]"""  # check whether all UID-items are in mapping_dict
#
#     print "\nChecking mapping-dict for completeness..."
#     # loop through trees and check if all nodes in mapping-dict
#     for tool_mode in schemaTreeDict:
#         inTree = schemaTreeDict[tool_mode]["input"]
#         while True:
#             dict_complete = mapping_dict_is_complete(MAPPING_DICT, inTree)
#             if dict_complete is True:
#                 break
#             else:
#                 tool, mode = tool_mode
#                 msg = "The following UID-items for {}[{}] are not mapped in the provided 'mapping dict': ".format(tool, mode)
#                 PRI.print_indexed_list(*dict_complete, message=msg)
#                 mssg = "Please add the missing mapping the dict and press [1] to continue."
#                 sel = PRO.user_prompt_yes_no(message=mssg)
#                 if sel:
#                     with open(mapping_file_path) as mData:
#                         MAPPING_DICT = json.load(mData)['MAPPING_DICT']
#                     continue
#                 else:
#                     return
#     print "\nNOTE: mapping-dict contains all mappings for selected tools."
#
#
#     """[STEP 3]""" # check whether input nodes are NOT produced any by tools in workflow, i.e. design variables exist
#     systemInputNodes = FPG.get_system_inputs(*tool_order, ignore_toolspecific=True) # TODO: toolspec can be enabled
#
#     # print design variables and let user decide whether to continue (may want to add tools or so)
#     if systemInputNodes:
#         print "\nThe following System Inputs have been found in the workflow:"
#         pList = list(sorted(systemInputNodes.items(), key = lambda x: x[1]))
#         PRI.print_in_table(pList, headers=["Xpath", "Tools"], print_indeces=True)
#
#         msg = "Would you like to continue? "
#         yn_sel = PRO.user_prompt_yes_no(message=msg)
#         if not yn_sel:
#             return None
#     else:
#         print "\nNOTE: No System Inputs found in graph."
#
#     # loop tools for [step 4] & [step 5], write toolspecific to Basefile, execute tools, write output to Basefile
#     for func in tool_order:
#
#         # get tool name and execution mode
#         tool = FPG.node[func]['name']
#         mode = FPG.node[func]['mode']
#         toolspec_elem = FPG.node[func]['toolspecific']
#
#         # print exection message
#         pr_execTool = "\n\nTool Execution: {}[{}]".format(tool, mode)
#         print "{} \n{}".format(pr_execTool, "-"*(len(pr_execTool)+1))
#
#
#         """[STEP 4]""" # copy toolspecific nodes from schema tree to basefile
#         inputSchemaTree = schemaTreeDict[(tool, mode)]['input']
#
#         # filter tree by modes
#         baseTree = MU.copy_toolspecific_elements_to_tree(baseTree, inputSchemaTree, toolspec_elem, overwrite_if_exist=True, nodes_valued=True)
#         MU.write_xml_tree_to_file(baseTree, basefile_path)
#
#
#         """[STEP 5]""" # ensure that base file is executable
#         while True:
#
#             # make copy of Basetree for tool execution; make execTree the new Basetree if execution is successful!
#             execTree = copy.deepcopy(baseTree)
#
#             """[STEP 5a]"""  # add missing nodes to execTree
#             # get paths in basetree and schemaTree, and retrieve node that are not in basetree
#             execTreePaths = MU.get_xpaths_in_element_tree(execTree, leaf_nodes=True)
#             schemaPaths = MU.get_xpaths_in_element_tree(inputSchemaTree, apply_modes=[mode], leaf_nodes=True)
#
#             missingSchemaNodes = [x for x in schemaPaths if x not in execTreePaths]
#             missingN = schemaPaths - execTreePaths
#
#             # if nodes are missing, add nodes for temporarily tool execution (permanently if System Input)
#             if missingSchemaNodes:
#
#                 # print missing nodes
#                 print "\nThe following nodes are missing for execution of {}[{}]:".format(tool, mode)
#                 print "-"*3
#                 for node in sorted(missingSchemaNodes):
#                     print node
#                 print "-"*3
#
#                 # let user decide whether to continue
#                 cont_msg = "Continue?"
#                 yn_sel = PRO.user_prompt_yes_no(message=cont_msg)
#                 if not yn_sel:
#                     return
#
#                 # check whether basetree has UID-items that refer to missing nodes
#                 refUIDs = {}
#                 for path in missingSchemaNodes:
#                     refUIDs = MU.get_applied_uids_by_path(MAPPING_DICT, execTree, path, refUIDs)
#
#                 # add nodes missing nodes to tree
#                 execTree = MU.add_nodes_to_tree(execTree, missingSchemaNodes, spec_files_dir_path, refUIDs)
#
#
#             """[STEP 5b]"""  # perform depndency check on nodes in Basefile
#             # check dependency on added nodes first; may not have all necessary info
#             for xpath in missingSchemaNodes:
#                 execTree = MU.check_node_dependencies(MAPPING_DICT, execTree, xpath)
#
#             #check dependency on toolspecific nodes
#             toolspec_schema_paths = [p for p in schemaPaths if "toolspecific" in p]
#             for xpath in toolspec_schema_paths:
#                 execTree = MU.check_node_dependencies(MAPPING_DICT, execTree, xpath)
#
#             # check schema leaf paths in Basefile
#             for xpath in schemaPaths: # TODO: continue here: CHECK ALL INPUT NODES
#                 execTree = MU.check_node_dependencies(MAPPING_DICT, execTree, xpath)
#             # TODO: SHOULD ALL INPUT VARS BE CHECKED OR SHOULD CORRECTNESS BE RELIED UPON BY TOOL (future implementation should check ALL nodes to assert file validity/consistency)?
#
#
#             """[STEP 6]""" # execute the tool; read/write to basefile in specific KB
#             # execute tool
#             try:
#                 output_file_path = execute_tool(tool, mode, execTree)
#                 break
#             except ME.MatlabExecutionError as err: # TODO: will error be raised here? check if placement appropriate
#                 print "The failed to execute due to the following error: \n", str(err)
#                 repeat_msg = "Would you like to repeat the process?"
#                 rep_sel = PRO.user_prompt_yes_no(message=repeat_msg)
#                 if rep_sel:
#                     continue
#                 else:
#                     return
#
#
#         """[STEP 7]""" # merge tool output file with basefile
#         # write execTree to Basefile path; written to path AFTER execution to ensure validity
#         outputTree = etree.parse(output_file_path)
#         baseTree = MU.merge_XML_trees(outputTree, execTree) # careful with sequence: 1st pos dominant?
#         MU.write_xml_tree_to_file(baseTree, basefile_path)
#
#         # print execution complete
#         print "\nTool execution completed; output successfully written to Basefile."
#
#
#     """[STEP 8]""" # generate specific input and output files; write to use-case dir
#
#     # inititate IO-file generator object
#     IOgen = IO.IO_file_generator(MAPPING_DICT, baseTree, print_details=print_details)
#
#     # loop through tools and generate input and output files
#     for func in tool_order:
#
#         # get tool name and execution mode
#         tool = FPG.node[func]['name']
#         mode = FPG.node[func]['mode']
#         toolspec_elem = FPG.node[func]['toolspecific']
#         print "\nGenerating case-specific IO-files for {}[{}]...".format(tool, mode)
#
#         for io in ["input","output"]:
#
#             # check whether info-file present in use-case dir; otherwise copy from schematic
#             info_file = "{}-info.json".format(tool)
#             info_target = os.path.join(spec_files_dir_path, info_file)
#             if not os.path.exists(info_target):
#                 info_source = os.path.join(schema_files_dir_path, info_file)
#                 shutil.copy(info_source, info_target) # copy file to target path
#
#             # get target path; check whether file already exists
#             ioFile = "{tool}-{io}.xml".format(tool=tool, io=io)
#             targetPath = os.path.join(spec_files_dir_path, ioFile)
#             targetTree = None
#             if os.path.exists(targetPath):
#                 targetTree = etree.parse(targetPath)
#
#             # get schema input or output tree
#             schemaTree = schemaTreeDict[(tool, mode)][io]
#
#             # perform file generation
#             # ioTree = IO.generate_IO_tree(MAPPING_DICT, baseTree, schemaTree, mode, toolspec_elem)
#             ioTree = IOgen._extract_io_tree(schemaTree, mode, toolspec_elem)
#
#             # if tool file already exists, merge trees
#             if targetTree:
#                 targetTree = MU.merge_XML_trees(targetTree, ioTree)
#                 # TODO: check whether tree merge overwrites the wrong tree attribs; target should be dominant
#             else:
#                 targetTree = ioTree
#
#             # iterate all schmema nodes and check if modes-attrib present
#             # if present, add modes to target tree
#             # since modes-search follows the schema-file, a simple search for corresponding elements is enough
#             # (no need to check ancestors or descendants for modes)
#             for node in schemaTree.iter():
#                 if node.get("modes") and mode in node.get("modes"):
#                     searchPath = MU.xpath_to_searchpath(schemaTree.getpath(node))
#                     foundElems = targetTree.findall(searchPath)
#
#                     # get all related elements and add mode
#                     for elem in foundElems:
#                         if elem.get("modes"): # if exists, add to existing
#                             modesList = elem.get("modes").split()
#                             if mode not in modesList:
#                                 modesList.append(mode)
#                             modesComb = " ".join(modesList)
#                             elem.set("modes", modesComb)
#                         else:
#                             elem.set("modes", mode)
#
#             # write to tree and
#             MU.write_xml_tree_to_file(targetTree, targetPath)
#
#     print "\nNOTE: Case-specific I/O-files generated and written to {}.".format(spec_files_dir_path)
#
#     # TODO: sort nodes in basefile according to standard structure >> toolspec at the bottom, header at beginning
#     return