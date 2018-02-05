# Imports
import os
import logging

from kadmos.graph import load, FundamentalProblemGraph
from kadmos.utilities.general import get_mdao_setup

# Settings for logging
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.WARNING)

# List of MDAO definitions that can be wrapped around the problem
# TODO: Adjust to just seven options (MDA-seq, MDA-par, DOE-seq, DOE-par, IDF, MDF-seq, MDF-par)
# TODO: Add option to enforce unconverged strategies
mdao_definitions = ['unconverged-MDA-GS',  # 0
                    'unconverged-MDA-J',   # 1
                    'converged-MDA-GS',    # 2
                    'converged-MDA-J',     # 3
                    'unconverged-DOE-GS',  # 4
                    'unconverged-DOE-J',   # 5
                    'converged-DOE-GS',    # 6
                    'converged-DOE-J',     # 7
                    'unconverged-OPT-GS',  # 8
                    'unconverged-OPT-J',   # 9
                    'MDF-GS',              # 10
                    'MDF-J',               # 11
                    'IDF']                 # 12

# Settings for scripting
mdao_definitions_loop_all = True      # Option for looping through all MDAO definitions
mdao_definition_id = 12               # Option for selecting a MDAO definition (in case mdao_definitions_loop_all=False)

# Settings for creating the CMDOWS files
create_rcg_cmdows = False               # Option for creating the RCG CMDOWS file, set to False to save time

# Settings for creating visualizations
create_vis = True                      # Create visualisations
create_rcg_vis = False                  # Create RCG visualizations, set to False after first execution to save time

# Settings for loading and saving
kb_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../knowledgebases')
kb_name = 'tu_delft_wing_design'
cmdows_input_file = 'tu_delft_knowledge_base_cmdows.xml'
ref_vals = os.path.join(kb_dir, kb_name, 'reference_values.xml')
pdf_dir = 'tu_delft_wing_design/(X)DSM'
cmdows_dir = 'tu_delft_wing_design/CMDOWS'
kdms_dir = 'tu_delft_wing_design/KDMS'
vistoms_dir = 'tu_delft_wing_design/VISTOMS'

print 'Loading knowledge base using CMDOWS file {}...'.format(cmdows_input_file)

rcg = load(os.path.join(kb_dir, kb_name, cmdows_input_file))

print 'Scripting RCG...'

# A name and a description are added to the graph
rcg.graph['name'] = 'RCG'
rcg.graph['description'] = 'Repository of aircraft design tools from Delft University of Technology.'

# Define function order for visualization (otherwise the functions will be placed randomly on the diagonal)
functions = ['HANGAR[AGILE_DC1_WP6_wing_startpoint][1][1.0]',
             'HANGAR[AGILE_DC1_L0_MDA][1][1.0]',
             'HANGAR[AGILE_DC1_L0_wing][1][1.0]',
             'HANGAR[Boxwing_AGILE_Hangar][1][1.0]',
             'HANGAR[D150_AGILE_Hangar][1][1.0]',
             'HANGAR[NASA_CRM_AGILE_Hangar][1][1.0]',
             'HANGAR[ATR72_AGILE_Hangar][1][1.0]',
             'INITIATOR[main][1][1.0]',
             'SCAM[wing_taper_morph][1][1.0]',
             'SCAM[wing_sweep_morph][1][1.0]',
             'SCAM[wing_dihedral_morph][1][1.0]',
             'SCAM[wing_root_chord_morph][1][1.0]',
             'SCAM[wing_length_morph][1][1.0]',
             'GACA[mainWingRefArea][1][1.0]',
             'GACA[mainWingFuelTankVol][1][1.0]',
             'Q3D[VDE][1][1.0]',
             'Q3D[FLC][1][1.0]',
             'Q3D[APM][1][1.0]',
             'EMWET[main][1][1.0]',
             'SMFA[main][1][1.0]',
             'PHALANX[Full_Lookup][1][1.0]',
             'PHALANX[Full_Simple][1][1.0]',
             'PHALANX[Symmetric_Lookup][1][1.0]',
             'PHALANX[Symmetric_Simple][1][1.0]',
             'PROTEUS[main][1][1.0]',
             'MTOW[main][1][1.0]',
             'OBJ',
             'CNSTRNT_wingLoading',
             'CNSTRNT_fuelTankVolume']
# Alternatively, one could automatically determine a function order with a method
# functions = rcg.get_possible_function_order('single-swap')

# Create a DSM and a VISTOMS visualization of the RCG
if create_vis and create_rcg_vis:
    print 'Creating visualizations of RCG...'
    rcg.create_dsm('RCG', include_system_vars=True, summarize_vars=True, function_order=functions,
                   destination_folder=pdf_dir)
    rcg.vistoms_create(vistoms_dir, function_order=functions, reference_file=ref_vals)

# Save CMDOWS file
if create_rcg_cmdows:
    print 'Creating CMDOWS file of RCG...'
    rcg.save('RCG',
             file_type='cmdows',
             description='RCG CMDOWS file of the repository of aircraft design tools from Delft University of Technology',
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

    # Create / reset FPG
    fpg = rcg.deepcopy_as(FundamentalProblemGraph)
    fpg.graph['name'] = 'FPG ' + ' - ' + mdao_definition
    fpg.graph['description'] = 'Fundamental problem graph to solve the wing design problem using the strategy: ' \
                               + mdao_definition + '.'

    # Remove the functions from the FPG that are not needed
    fpg.remove_function_nodes('INITIATOR[main][1][1.0]', 'PROTEUS[main][1][1.0]', 'PHALANX[Symmetric_Lookup][1][1.0]',
                              'PHALANX[Full_Lookup][1][1.0]', 'PHALANX[Full_Simple][1][1.0]',
                              'PHALANX[Symmetric_Simple][1][1.0]', 'HANGAR[AGILE_DC1_L0_wing][1][1.0]',
                              'HANGAR[AGILE_DC1_L0_MDA][1][1.0]', 'HANGAR[ATR72_AGILE_Hangar][1][1.0]',
                              'HANGAR[Boxwing_AGILE_Hangar][1][1.0]', 'HANGAR[D150_AGILE_Hangar][1][1.0]',
                              'HANGAR[NASA_CRM_AGILE_Hangar][1][1.0]', 'Q3D[APM][1][1.0]')

    # Contract the FPG to the smallest graph size possible for wrapping the architectures
    # Contract SCAM function modes into one node
    fpg = fpg.merge_function_modes('SCAM', 'wing_length_morph', 'wing_taper_morph', 'wing_root_chord_morph',
                                   'wing_sweep_morph', 'wing_dihedral_morph', instance='1', version='1.0')
    if mdao_definition in ['unconverged-MDA-GS', 'unconverged-MDA-J', 'converged-MDA-GS', 'converged-MDA-J']:
        fpg.remove_function_nodes('SCAM-merged[5modes]')

    # Contract GAGA function modes into one node
    fpg = fpg.merge_function_modes('GACA', 'mainWingFuelTankVol', 'mainWingRefArea', instance='1', version='1.0')

    # Contract CNSTRNT function modes into one node
    fpg = fpg.merge_parallel_functions('CNSTRNT_fuelTankVolume', 'CNSTRNT_wingLoading', new_label='CNSTRNTs')

    # Group Q3D[APM] and SMFA
    fpg = fpg.merge_sequential_functions('Q3D[VDE][1][1.0]', 'SMFA[main][1][1.0]', new_label='Q3D[VDE]--SMFA')

    # Group Q3D[FLC] and EMWET into a service
    fpg = fpg.merge_sequential_functions('Q3D[FLC][1][1.0]', 'EMWET[main][1][1.0]', new_label='Q3D[FLC]--EMWET')

    # Find and fix problematic nodes w.r.t. HANGAR tool
    # TODO: Instead of disconnecting all, the initial guesses for convergers could be automatically connected.
    fpg.disconnect_problematic_variables_from('HANGAR[AGILE_DC1_WP6_wing_startpoint][1][1.0]')

    # Define FPG function order after function contractions and export visualizations
    function_order = ['HANGAR[AGILE_DC1_WP6_wing_startpoint][1][1.0]',
                      'SCAM-merged[5modes]',
                      'GACA-merged[2modes]',
                      'Q3D[FLC]--EMWET',
                      'Q3D[VDE]--SMFA',
                      'MTOW[main][1][1.0]',
                      'OBJ',
                      'CNSTRNTs']
    if mdao_definition in ['unconverged-MDA-GS', 'unconverged-MDA-J', 'converged-MDA-GS', 'converged-MDA-J']:
        function_order.remove('SCAM-merged[5modes]')

    # Determine the three main settings: architecture, convergence type and unconverged coupling setting
    mdao_architecture, convergence_type, allow_unconverged_couplings = get_mdao_setup(mdao_definition)

    # Determine the feedback coupling
    feedback_couplings = fpg.get_direct_coupling_nodes('Q3D[FLC]--EMWET',
                                                       'Q3D[VDE]--SMFA',
                                                       'MTOW[main][1][1.0]',
                                                       direction='backward', print_couplings=False)

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

    # Define the special_input_nodes (you can also take these from the visualizations package)
    special_input_nodes = ['/cpacs/toolspecific/sCAM/wing_length_morph/required_length',
                           '/cpacs/toolspecific/sCAM/wing_dihedral_morph/required_wing_dihedral',
                           '/cpacs/toolspecific/sCAM/wing_root_chord_morph/required_root_chord',
                           '/cpacs/toolspecific/sCAM/wing_taper_morph/required_taper1',
                           '/cpacs/toolspecific/sCAM/wing_taper_morph/required_taper2',
                           '/cpacs/toolspecific/sCAM/wing_sweep_morph/required_sweep1',
                           '/cpacs/toolspecific/sCAM/wing_sweep_morph/required_sweep2']

    # Settings of design variables
    sample_ranges = [[14.000, 16.33982, 19.000],  # required_length
                     [2.000, 6.000, 10.0000],     # required_wing_dihedral
                     [5.8, 6.3923, 6.8],          # required_root_chord
                     [0.35, 0.4251, 0.50],        # required_taper1
                     [0.13, 0.1645182485, 0.19],  # required_taper2
                     [28.0, 33.2273, 36.0],       # required_sweep1
                     [0.75, 0.884926, 0.95]]      # required_sweep2
    lower_bounds = [value[0] for value in sample_ranges]
    nominal_values = [value[1] for value in sample_ranges]
    upper_bounds = [value[2] for value in sample_ranges]

    # List special nodes
    special_output_nodes = ['/cpacs/mdodata/objectives/mtow/normalized_mtow',
                            '/cpacs/mdodata/constraints/wingLoading/latestValue',
                            '/cpacs/mdodata/constraints/fuelTankVolume/latestValue']

    qoi_nodes = ['/cpacs/vehicles[@uID="AGILE_DC1_vehicleID"]/aircraft/model[@uID="agile_v13_modelID"]/analyses/massBreakdown/mOEM/mEM/mStructure/mWingsStructure/mWingStructure/massDescription/mass',
                 '/cpacs/vehicles[@uID="AGILE_DC1_vehicleID"]/aircraft/model[@uID="agile_v13_modelID"]/analyses/massBreakdown/fuel/massDescription/mass',
                 '/cpacs/vehicles[@uID="AGILE_DC1_vehicleID"]/aircraft/model[@uID="agile_v13_modelID"]/analyses/massBreakdown/designMasses/mTOM/mass']

    # Function to check the graph for collisions and holes. Collisions are solved based on the function order and holes
    # will simply be removed.
    fpg.make_all_variables_valid()

    # Depending on the architecture, set the design variables, objective, constraints, and QOIs as expected.
    if mdao_architecture in ['unconverged-OPT', 'MDF', 'IDF', 'unconverged-DOE', 'converged-DOE']:
        # Set design variables
        fpg.mark_as_design_variables(special_input_nodes,
                                     lower_bounds=lower_bounds,
                                     nominal_values=nominal_values,
                                     upper_bounds=upper_bounds,
                                     samples=sample_ranges)
    if mdao_architecture in ['unconverged-OPT', 'MDF', 'IDF']:
        # Set objective and constraints
        fpg.mark_as_objective(special_output_nodes[0])
        fpg.mark_as_constraints(special_output_nodes[1:], '<=', reference_values=0.0)
    elif mdao_architecture in ['unconverged-MDA', 'converged-MDA', 'unconverged-DOE', 'converged-DOE']:
        # TODO: This should work for all options
        if mdao_architecture == 'unconverged-DOE':
            qoi_nodes += special_output_nodes
        else:
            qoi_nodes = special_output_nodes
        fpg.mark_as_qois(qoi_nodes)

    # For the unconverged-MDA-Jacobi remove the Q3D[FLC]-EMWET--seq function
    if mdao_definition in ['unconverged-MDA-J', 'unconverged-DOE-J', 'unconverged-OPT-J']:
        fpg.remove_function_nodes('Q3D[FLC]--EMWET')
        function_order.remove('Q3D[FLC]--EMWET')

    # Add some constraint attributes
    if mdao_architecture in ['IDF', 'MDF']:
        fpg.node['/cpacs/mdodata/constraints/fuelTankVolume/latestValue']['constraint_type'] = 'inequality'
        fpg.node['/cpacs/mdodata/constraints/wingLoading/latestValue']['constraint_type'] = 'inequality'
        fpg.node['/cpacs/mdodata/constraints/fuelTankVolume/latestValue']['constraint_operator'] = '>='
        fpg.node['/cpacs/mdodata/constraints/wingLoading/latestValue']['constraint_operator'] = '>='
        fpg.node['/cpacs/mdodata/constraints/fuelTankVolume/latestValue']['reference_value'] = 0.0
        fpg.node['/cpacs/mdodata/constraints/wingLoading/latestValue']['reference_value'] = 0.0

    # Remove all unused system outputs
    output_nodes = fpg.find_all_nodes(subcategory='all outputs')
    for output_node in output_nodes:
        if output_node not in special_output_nodes:
            fpg.remove_node(output_node)

    # Add the function problem roles (pre-coupling, coupled, post-coupling)
    fpg.add_function_problem_roles()

    # Add some more (optional) metadata
    for node in fpg.get_function_nodes():
        if 'Q3D' in node or 'MTOW' in node:
            single_or_multi = "Single" if 'unconverged-MDA' in mdao_architecture else "Multiple"
            execution_info = {
                'remote_component_info': {
                    'job_settings': {
                        'single_or_multi_execution': single_or_multi,
                        'remote_engineer': {'contact_u_i_d': 'ivangent'},
                        'job_name': 'job_' + fpg.node[node]['label'].replace(' ', ''),
                        'notification_message': 'Hi Imco, could you please run this tool ' + fpg.node[node]['label'].replace(' ', '') + ' for me for my ' + mdao_architecture + ' AGILE workflow execution. Thanks.'
                    },
                    'data_exchange_settings': {
                        'urlsite': 'https://teamsites-extranet.dlr.de/ly/AGILE/',
                        'folder': 'CMDOWS_parser_tests'
                    }
                }
            }
            fpg.node[node]['execution_info'] = execution_info

    # Create a DSM and a VISTOMS visualization of the FPG
    if create_vis:
        fpg.create_dsm(file_name='FPG_'+mdao_definition, function_order=function_order, include_system_vars=True,
                       summarize_vars=True, destination_folder=pdf_dir)
        fpg.vistoms_add(vistoms_dir, function_order=function_order, reference_file=ref_vals)

    # Save CMDOWS file
    fpg.save('FPG_' + mdao_definition,
             destination_folder=kdms_dir)
    fpg.save('FPG_' + mdao_definition,
             file_type='cmdows',
             description='WP6 TU Delft Wing Design FPG file',
             creator='Lukas Mueller',
             version='0.1',
             destination_folder=cmdows_dir,
             pretty_print=True)
    # Check integrity of CMDOWS
    fpg.check_cmdows_integrity()

    # Save the FPG as kdms
    fpg.save('FPG_'+mdao_definition, destination_folder=kdms_dir)
    # Save the FPG as cmdows (and do an integrity check)
    fpg.save('FPG_'+mdao_definition, file_type='cmdows', destination_folder=cmdows_dir,
             description='FPG CMDOWS file of the wing design problem from Delft University of Technology',
             creator='Lukas Mueller',
             version='0.1',
             pretty_print=True,
             integrity=True)

    # Get Mdao graphs
    mdg = fpg.get_mdg(name='mpg wing design')
    mpg = mdg.get_mpg(name='mpg wing design')
    mdg.graph['name'] = 'XDSM' + ' - ' + mdao_definition
    mdg.graph['description'] = 'Solution strategy to solve the wing design problem using the strategy: ' \
                               + str(mdao_architecture) + ('_' + str(convergence_type) if convergence_type else '') + '.'

    # Create a DSM and a VISTOMS visualizations
    if create_vis:
        mdg.create_dsm(file_name='Mdao_'+mdao_definition, include_system_vars=True, destination_folder=pdf_dir,
                       summarize_vars=True, mpg=mpg)
        mdg.vistoms_add(vistoms_dir, mpg=mpg, reference_file=ref_vals)

    # Save the Mdao as kdms
    mdg.save('Mdao_'+mdao_definition, destination_folder=kdms_dir, mpg=mpg)
    # Save the Mdao as cmdows (and do an integrity check)
    mdg.save('Mdao_'+mdao_definition, file_type='cmdows', destination_folder=cmdows_dir,
             mpg=mpg,
             description='Mdao CMDOWS file of the wing design problem from Delft University of Technology',
             creator='Lukas Mueller',
             version='0.1',
             pretty_print=True,
             integrity=True)

print 'Done!'
