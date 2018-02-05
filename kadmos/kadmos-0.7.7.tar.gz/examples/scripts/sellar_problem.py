# Imports
import logging

from collections import OrderedDict

import networkx as nx

from kadmos.graph import RepositoryConnectivityGraph, FundamentalProblemGraph, load
from kadmos.utilities.general import get_mdao_setup


# Settings for logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

# List of MDAO definitions that can be wrapped around the problem
mdao_definitions = ['unconverged-MDA-J',    # 0
                    'unconverged-MDA-GS',   # 1
                    'unconverged-DOE-GS',   # 2
                    'unconverged-DOE-J',    # 3
                    'converged-DOE-GS',     # 4
                    'converged-DOE-J',      # 5
                    'converged-MDA-J',      # 6
                    'converged-MDA-GS',     # 7
                    'unconverged-OPT-J',    # 8
                    'unconverged-OPT-GS',   # 9
                    'MDF-GS',               # 10
                    'MDF-J',                # 11
                    'IDF']                  # 12

# Settings for scripting
mdao_definitions_loop_all = True     # Option for looping through all MDAO definitions
mdao_definition_id = 9                # Option for selecting a MDAO definition (in case mdao_definitions_loop_all=False)

# Settings for saving
pdf_dir = 'sellar_problem/(X)DSM'
cmdows_dir = 'sellar_problem/CMDOWS'
kdms_dir = 'sellar_problem/KDMS'
vistoms_dir = 'sellar_problem/VISTOMS'


print 'Scripting RCG...'

# A new repository connectivity graph is defined to describe the general problem
rcg = RepositoryConnectivityGraph(name='Sellar problem graph')
# A description is added to the graph
rcg.graph['description'] = 'Repository graph of tools where a subset can be used to solve the Sellar problem'
# All function nodes are defined
rcg.add_node('A', category='function')
rcg.add_node('D1', category='function')
rcg.add_node('D2', category='function')
rcg.add_node('D3', category='function')
rcg.add_node('F1', category='function')
rcg.add_node('F2', category='function')
rcg.add_node('G1', category='function')
rcg.add_node('G2', category='function')
# All variable nodes are defined
rcg.add_node('/data_schema/settings/a', category='variable', label='a')
rcg.add_node('/data_schema/settings/c', category='variable', label='c')
rcg.add_node('/data_schema/analyses/f', category='variable', label='f')
rcg.add_node('/data_schema/analyses/g1', category='variable', label='g1')
rcg.add_node('/data_schema/analyses/g2', category='variable', label='g2')
rcg.add_node('/data_schema/geometry/x1', category='variable', label='x1')
rcg.add_node('/data_schema/analyses/y1', category='variable', label='y1')
rcg.add_node('/data_schema/analyses/y2', category='variable', label='y2')
rcg.add_node('/data_schema/geometry/z1', category='variable', label='z1')
rcg.add_node('/data_schema/geometry/z2', category='variable', label='z2')
# The edges between the nodes are defined
rcg.add_edge('A', '/data_schema/settings/c')
rcg.add_edge('D1', '/data_schema/analyses/y1')
rcg.add_edge('D2', '/data_schema/analyses/y2')
rcg.add_edge('D3', '/data_schema/geometry/x1')
rcg.add_edge('D3', '/data_schema/geometry/z1')
rcg.add_edge('D3', '/data_schema/geometry/z2')
rcg.add_edge('F1', '/data_schema/analyses/f')
rcg.add_edge('F2', '/data_schema/analyses/f')
rcg.add_edge('G1', '/data_schema/analyses/g1')
rcg.add_edge('G2', '/data_schema/analyses/g2')
rcg.add_edge('/data_schema/settings/a', 'A')
rcg.add_edge('/data_schema/settings/c', 'D1')
rcg.add_edge('/data_schema/settings/c', 'D2')
rcg.add_edge('/data_schema/geometry/x1', 'D1')
rcg.add_edge('/data_schema/geometry/x1', 'F1')
rcg.add_edge('/data_schema/geometry/x1', 'F2')
rcg.add_edge('/data_schema/analyses/y1', 'D2')
rcg.add_edge('/data_schema/analyses/y1', 'D3')
rcg.add_edge('/data_schema/analyses/y1', 'F1')
rcg.add_edge('/data_schema/analyses/y1', 'G1')
rcg.add_edge('/data_schema/analyses/y2', 'D1')
rcg.add_edge('/data_schema/analyses/y2', 'D3')
rcg.add_edge('/data_schema/analyses/y2', 'F1')
rcg.add_edge('/data_schema/analyses/y2', 'G2')
rcg.add_edge('/data_schema/geometry/z1', 'D1')
rcg.add_edge('/data_schema/geometry/z1', 'D2')
rcg.add_edge('/data_schema/geometry/z1', 'F2')
rcg.add_edge('/data_schema/geometry/z2', 'D1')
rcg.add_edge('/data_schema/geometry/z2', 'D2')
rcg.add_edge('/data_schema/geometry/z2', 'F1')
rcg.add_edge('/data_schema/geometry/z2', 'F2')

# Add some (optional) equations
rcg.add_equation_labels(rcg.get_function_nodes())
rcg.add_equation('A', 'a', 'Python')
rcg.add_equation('A', 'a', 'LaTeX')
rcg.add_equation('A', '<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>a</mi></math>', 'MathML')
rcg.add_equation('G1', 'y1/3.16-1', 'Python')
rcg.add_equation('G1', 'y1/3.16-1', 'LaTeX')
rcg.add_equation('G1', '<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>y</mi><mn>1</mn><mo>/</mo><mn>3</mn><mo>.</mo><mn>16</mn><mo>-</mo><mn>1</mn></math>', 'MathML')
rcg.add_equation('G2', '1-y2/24.0', 'Python')
rcg.add_equation('G2', '1-y2/24.0', 'LaTeX')
rcg.add_equation('G2', '<math xmlns="http://www.w3.org/1998/Math/MathML"><mn>1</mn><mo>-</mo><mi>y</mi><mn>2</mn><mo>/</mo><mn>24</mn><mo>.</mo><mn>0</mn></math>', 'MathML')
rcg.add_equation('F1', 'x1**2+z2+y1+exp(-y2)', 'Python')
rcg.add_equation('F1', 'x1^2+z2+y1+e^{-y2}', 'LaTeX')
rcg.add_equation('F1', '<math xmlns="http://www.w3.org/1998/Math/MathML"><mi>x</mi><msup><mn>1</mn><mn>2</mn></msup><mo>+</mo><mi>z</mi><mn>2</mn><mo>+</mo><mi>y</mi><mn>1</mn><mo>+</mo><msup><mi>e</mi><mrow><mo>-</mo><mi>y</mi><mn>2</mn></mrow></msup></math>', 'MathML')
# Add some (optional) organization information
contacts = [{'attrib': {'uID': 'ivangent'}, 'name': 'Imco van Gent', 'email': 'i.vangent@tudelft.nl', 'company': 'TU Delft'},
            {'attrib': {'uID': 'lmuller'}, 'name': 'Lukas Muller', 'email': 'l.muller@student.tudelft.nl', 'company': 'TU Delft'}]
architects = [{'contactUID': 'ivangent'}, {'contactUID': 'lmuller'}]
integrators = [{'contactUID': 'lmuller'}]
rcg.graph['organization'] = OrderedDict([('contacts', contacts),
                                         ('organigram', {'architects': architects,
                                                         'integrators': integrators})])
# Add some (optional) ranges
rcg.adj['/data_schema/geometry/z1']['D1']['valid_ranges'] = {'limit_range': {'minimum': -5, 'maximum': 5.},
                                                              'list_range': [('list_range_item', 7.5), ('list_range_item', 8)]}
# Add some (optional) metadata
rcg.node['F2']['general_info'] = {'description': 'dummy function that is not part of the original Sellar problem'}
rcg.node['F2']['performance_info'] = {'precision': 20,
                                      'fidelity_level': 2,
                                      'run_time': 1.5}

function_order = ['A', 'D1', 'D2', 'D3', 'F1', 'F2', 'G1', 'G2']

# Create a DSM visualization of the RCG
rcg.create_dsm(file_name='RCG', function_order=function_order, include_system_vars=True, destination_folder=pdf_dir,
               keep_tex_file=False, compile_pdf=True)
# Create a VISTOMS visualization of the RCG
rcg.vistoms_create(vistoms_dir, function_order=function_order, compress=False)

# Save the RCG as kdms
rcg.save('RCG', destination_folder=kdms_dir)
# Save the RCG as cmdows (and do an integrity check)
rcg.save('RCG', file_type='cmdows', destination_folder=cmdows_dir,
         description='RCG CMDOWS file of the well-known Sellar problem',
         creator='Imco van Gent',
         version='0.1',
         pretty_print=True,
         integrity=True)


print 'Scripting initial FPG...'

# A initial fundamental problem graph is created based on the rcg
fpg_initial = rcg.deepcopy_as(FundamentalProblemGraph)
# The dummy function nodes are removed
fpg_initial.remove_function_nodes('D3', 'F2')
# A new function order is defined
function_order = fpg_initial.get_possible_function_order('single-swap')

# On to the wrapping of the MDAO architectures
# Get iterator (all or single one)
if not mdao_definitions_loop_all:
    mdao_definitions = [mdao_definitions[mdao_definition_id]]

for mdao_definition in mdao_definitions:

    print 'Scripting ' + str(mdao_definition) + '...'

    # Determine the three main settings: architecture, convergence type and unconverged coupling setting
    mdao_architecture, convergence_type, allow_unconverged_couplings = get_mdao_setup(mdao_definition)

    # Reset FPG
    fpg = fpg_initial.deepcopy()
    fpg.graph['name'] = 'FPG - ' + mdao_definition
    fpg.graph['description'] = 'Fundamental problem graph for solving the Sellar problem using the strategy: ' \
                               + mdao_definition + '.'

    # Define settings of the problem formulation
    fpg.graph['problem_formulation'] = dict()
    fpg.graph['problem_formulation']['function_order'] = function_order
    fpg.graph['problem_formulation']['mdao_architecture'] = mdao_architecture
    fpg.graph['problem_formulation']['convergence_type'] = convergence_type
    fpg.graph['problem_formulation']['allow_unconverged_couplings'] = allow_unconverged_couplings
    if mdao_architecture in ['unconverged-DOE', 'converged-DOE']:
        fpg.graph['problem_formulation']['doe_settings'] = dict()
        fpg.graph['problem_formulation']['doe_settings']['doe_method'] = 'Custom design table'
        if fpg.graph['problem_formulation']['doe_settings']['doe_method'] in ['Latin hypercube design',
                                                                              'Monte Carlo design']:
            fpg.graph['problem_formulation']['doe_settings']['doe_seed'] = 6
            fpg.graph['problem_formulation']['doe_settings']['doe_runs'] = 5
        elif fpg.graph['problem_formulation']['doe_settings']['doe_method'] in ['Full factorial design']:
            fpg.graph['problem_formulation']['doe_settings']['doe_runs'] = 5

    # Depending on the architecture, different additional node attributes have to be specified. This is automated here
    # to allow direct execution of all different options.
    if mdao_architecture in ['IDF', 'MDF', 'unconverged-OPT']:
        fpg.mark_as_objective('/data_schema/analyses/f')
        fpg.mark_as_constraints(['/data_schema/analyses/g1','/data_schema/analyses/g2'], '>=', 0.0)
        fpg.mark_as_design_variables(['/data_schema/geometry/z1','/data_schema/geometry/z2','/data_schema/geometry/x1'],
                                     lower_bounds=[-10,0.0,0.0], upper_bounds=10, nominal_values=0.0)
    elif mdao_architecture in ['unconverged-MDA', 'converged-MDA']:
        fpg.mark_as_qois(['/data_schema/analyses/f',
                         '/data_schema/analyses/g1',
                         '/data_schema/analyses/g2',
                         '/data_schema/analyses/y1',
                         '/data_schema/analyses/y2'])
    elif mdao_architecture in ['unconverged-DOE', 'converged-DOE']:
        fpg.mark_as_qois(['/data_schema/analyses/f',
                         '/data_schema/analyses/g1',
                         '/data_schema/analyses/g2'])
        if fpg.graph['problem_formulation']['doe_settings']['doe_method'] == 'Custom design table':
            fpg.mark_as_design_variable('/data_schema/geometry/z1', samples=[0.0, 0.1, 0.5, 0.75])
            fpg.mark_as_design_variable('/data_schema/geometry/z2', samples=[1.0, 1.1, 1.5, 1.75])
            fpg.mark_as_design_variable('/data_schema/geometry/x1', samples=[2.0, 2.1, 2.5, 2.75])
        else:
            fpg.mark_as_design_variable('/data_schema/geometry/z1', lower_bound=-10., upper_bound=10)
            fpg.mark_as_design_variable('/data_schema/geometry/z2', lower_bound=0., upper_bound=10.)
            fpg.mark_as_design_variable('/data_schema/geometry/x1', lower_bound=0., upper_bound=10.)
    if mdao_architecture == 'IDF':
        fpg.node['/data_schema/analyses/y1']['valid_ranges'] = {'limit_range': {'minimum': -100., 'maximum': 100.}}
        fpg.node['/data_schema/analyses/y2']['valid_ranges'] = {'limit_range': {'minimum': -100., 'maximum': 100.}}

    # Search for problem roles
    fpg.add_function_problem_roles()

    # Create a DSM visualization of the FPG
    fpg.create_dsm(file_name='FPG_'+mdao_definition, function_order=function_order, include_system_vars=True,
                   destination_folder=pdf_dir)
    # Create a VISTOMS visualization of the FPG (and add it to the existing directory)
    fpg.vistoms_add(vistoms_dir, function_order=function_order)

    # Save the FPG as kdms
    fpg.save('FPG_'+mdao_definition, destination_folder=kdms_dir)
    # Save the FPG as cmdows (and do an integrity check)
    fpg.save('FPG_'+mdao_definition, file_type='cmdows', destination_folder=cmdows_dir,
             description='FPG CMDOWS file of the well-known Sellar problem',
             creator='Imco van Gent',
             version='0.1',
             pretty_print=True,
             integrity=True)

    # Get Mdao graphs
    mdg = fpg.get_mdg(name='mdg Sellar problem')
    mpg = mdg.get_mpg(name='mpg Sellar problem')
    mdg.graph['name'] = 'XDSM - ' + mdao_definition
    mdg.graph['description'] = 'Solution strategy to solve the Sellar problem using the strategy: ' \
                               + str(mdao_architecture) + ('_' + str(convergence_type) if convergence_type else '') + '.'

    # Create a DSM visualization of the Mdao
    mdg.create_dsm(file_name='Mdao_'+mdao_definition, include_system_vars=True, destination_folder=pdf_dir, mpg=mpg)
    # Create a VISTOMS visualization of the Mdao (and add it to the existing directory)
    mdg.vistoms_add(vistoms_dir, mpg=mpg)

    # Save the Mdao as kdms
    mdg.save('Mdao_'+mdao_definition, destination_folder=kdms_dir, mpg=mpg)
    # Save the Mdao as cmdows (and do an integrity check)
    mdg.save('Mdao_'+mdao_definition, file_type='cmdows', destination_folder=cmdows_dir,
             mpg=mpg,
             description='Mdao CMDOWS file of the well-known Sellar problem',
             creator='Imco van Gent',
             version='0.1',
             pretty_print=True,
             integrity=True,
             convention=True)

print 'Done!'
