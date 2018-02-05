# Imports
import os
import logging

from collections import OrderedDict

from kadmos.graph import FundamentalProblemGraph, load
from kadmos.utilities.general import get_mdao_setup


# Settings for logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# List of MDAO definitions that can be wrapped around the problem
mdao_definitions = ['MDF-GS',              # 0
                    'MDF-J',               # 1
                    'IDF']                 # 2

# Settings for scripting
mdao_definitions_loop_all = True      # Option for looping through all MDAO definitions
mdao_definition_id = 2                # Option for selecting a MDAO definition (in case mdao_definitions_loop_all=False)

# Settings for creating the CMDOWS files
create_rcg_cmdows = True              # Option for creating the RCG CMDOWS file, set to False to save time

# Settings for creating visualizations
create_vis = True                     # Create visualisations
create_rcg_vis = True                 # Create RCG visualizations, set to False after first execution to save time

# Settings for loading and saving
kb_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../knowledgebases')
pdf_dir = 'ssbj/(X)DSM'
cmdows_dir = 'ssbj/CMDOWS'
kdms_dir = 'ssbj/KDMS'
vistoms_dir = 'ssbj/VISTOMS'

print 'Loading repository connectivity graph...'

rcg = load(os.path.join(kb_dir, 'ssbj', 'ssbj_toolrepo_cmdows.xml'), io_xsd_check=True)

print 'Scripting RCG...'

# A name and a description are added to the graph
rcg.graph['name'] = 'RCG'
rcg.graph['description'] = 'Repository of the super-sonic business jet test case optimization problem'

# Add some (optional) organization information
contacts = [{'attrib': {'uID': 'ivangent'}, 'name': 'Imco van Gent', 'email': 'i.vangent@tudelft.nl', 'company': 'TU Delft'},
            {'attrib': {'uID': 'lmuller'}, 'name': 'Lukas Muller', 'email': 'l.muller@student.tudelft.nl', 'company': 'TU Delft'}]
architects = [{'contactUID': 'ivangent'}, {'contactUID': 'lmuller'}]
integrators = [{'contactUID': 'lmuller'}]
rcg.graph['organization'] = OrderedDict([('contacts', contacts),
                                         ('organigram', {'architects': architects,
                                                         'integrators': integrators})])

# Add the objective
rcg.add_node('objective', category='function')
rcg.add_node('/data_schema/aircraft/other/objective', category='variable', label='obj')
rcg.add_edge('/data_schema/aircraft/other/R', 'objective')
rcg.add_edge('objective', '/data_schema/aircraft/other/objective')
rcg.add_equation_labels(rcg.get_function_nodes())
rcg.add_equation('objective', '-R', 'Python')
rcg.add_equation('objective', '-R', 'LaTeX')

# Define function order for visualization (otherwise the functions will be placed randomly on the diagonal)
functions = ['structure[main][1][1.0]',
             'aerodynamics[main][1][1.0]',
             'propulsion[main][1][1.0]',
             'performance[main][1][1.0]',
             'objective']

# Create a DSM and a VISTOMS visualization of the RCG
if create_vis and create_rcg_vis:
    rcg.create_dsm('RCG', include_system_vars=True, function_order=functions,
                   destination_folder=pdf_dir)
    rcg.vistoms_create(vistoms_dir, function_order=functions)

# Save CMDOWS file
if create_rcg_cmdows:
    rcg.save('RCG',
             file_type='cmdows',
             description='RCG CMDOWS file of the super-sonic business jet test case optimization problem',
             creator='Lukas Mueller',
             version='0.1',
             destination_folder=cmdows_dir,
             pretty_print=True,
             integrity=True)


# On to the wrapping of the MDAO architectures
# Get iterator (all or single one)
if not mdao_definitions_loop_all:
    mdao_definitions = [mdao_definitions[mdao_definition_id]]

for mdao_definition in mdao_definitions:

    print 'Scripting ' + str(mdao_definition) + '...'

    # Reset FPG
    fpg = FundamentalProblemGraph(rcg)
    fpg.graph['name'] = rcg.graph['name'] + ' - ' + mdao_definition + ' - FPG'
    fpg.graph['description'] = 'Fundamental problem graph to solve the super-sonic business jet test case optimization problem using the strategy: ' \
                               + mdao_definition + '.'

    # Determine the three main settings: architecture, convergence type and unconverged coupling setting
    mdao_architecture, convergence_type, allow_unconverged_couplings = get_mdao_setup(mdao_definition)

    # Define settings of the problem formulation
    fpg.graph['problem_formulation'] = dict()
    fpg.graph['problem_formulation']['function_order'] = functions
    fpg.graph['problem_formulation']['mdao_architecture'] = mdao_architecture
    fpg.graph['problem_formulation']['convergence_type'] = convergence_type
    fpg.graph['problem_formulation']['allow_unconverged_couplings'] = allow_unconverged_couplings

    # Depending on the architecture, different additional node attributes have to be specified. This is automated here
    # to allow direct execution of all different options.
    if mdao_architecture in ['IDF', 'MDF']:
        fpg.nodes['/data_schema/aircraft/other/objective']['problem_role'] = 'objective'
        fpg.nodes['/data_schema/aircraft/geometry/tc']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/aircraft/reference/h']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/reference/M']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/aircraft/geometry/AR']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/aircraft/geometry/Lambda']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/aircraft/geometry/Sref']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/aircraft/geometry/lambda']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/aircraft/geometry/section']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/aircraft/other/Cf']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/aircraft/other/T']['problem_role'] = 'design variable'
        #fpg.nodes['/data_schema/aircraft/geometry/Theta']['problem_role'] = 'design variable'
        #fpg.nodes['/data_schema/aircraft/other/L']['problem_role'] = 'design variable'
        #fpg.nodes['/data_schema/aircraft/weight/WE']['problem_role'] = 'design variable'
        #fpg.nodes['/data_schema/aircraft/weight/WT']['problem_role'] = 'design variable'
        #fpg.nodes['/data_schema/reference/ESF']['problem_role'] = 'design variable'
        #fpg.nodes['/data_schema/aircraft/other/D']['problem_role'] = 'design variable'
        fpg.nodes['/data_schema/aircraft/other/DT']['problem_role'] = 'constraint'
        fpg.nodes['/data_schema/aircraft/other/sigma']['problem_role'] = 'constraint'
        fpg.nodes['/data_schema/aircraft/other/dpdx']['problem_role'] = 'constraint'
        fpg.nodes['/data_schema/reference/Temp']['problem_role'] = 'constraint'

    # Search for problem roles
    fpg.add_function_problem_roles()

    # Create a DSM visualization of the FPG
    fpg.create_dsm(file_name='FPG_' + mdao_definition, function_order=functions, include_system_vars=True,
                   destination_folder=pdf_dir)
    # Create a VISTOMS visualization of the FPG (and add it to the existing directory)
    fpg.vistoms_add(vistoms_dir, function_order=functions)

    # Save the FPG as kdms
    fpg.save('FPG_' + mdao_definition, destination_folder=kdms_dir)
    # Save the FPG as cmdows (and do an integrity check)
    fpg.save('FPG_' + mdao_definition, file_type='cmdows', destination_folder=cmdows_dir,
             description='FPG CMDOWS file of the super-sonic business jet test case optimization problem',
             creator='Imco van Gent',
             version='0.1',
             pretty_print=True,
             integrity=True)

    # Get Mdao graphs
    mpg = fpg.get_mpg(name='mpg Sellar problem')
    mdg = fpg.get_mdg(name='mdg Sellar problem')
    mdg.graph['name'] = rcg.graph['name'] + ' - ' + mdao_definition + ' - Mdao'
    mdg.graph['description'] = 'Solution strategy to solve the super-sonic business jet test case optimization problem using the strategy: ' \
                               + str(mdao_architecture) + (
                               '_' + str(convergence_type) if convergence_type else '') + '.'

    # Create a DSM visualization of the Mdao
    mdg.create_dsm(file_name='Mdao_' + mdao_definition, include_system_vars=True, destination_folder=pdf_dir,
                   mpg=mpg)
    # Create a VISTOMS visualization of the Mdao (and add it to the existing directory)
    mdg.vistoms_add(vistoms_dir, mpg=mpg)

    # Save the Mdao as kdms
    mdg.save('Mdao_' + mdao_definition, destination_folder=kdms_dir, mpg=mpg)
    # Save the Mdao as cmdows (and do an integrity check)
    mdg.save('Mdao_' + mdao_definition, file_type='cmdows', destination_folder=cmdows_dir,
             mpg=mpg,
             description='Mdao CMDOWS file of the super-sonic business jet test case optimization problem',
             creator='Imco van Gent',
             version='0.1',
             pretty_print=True,
             integrity=True
             )

print 'Done!'
