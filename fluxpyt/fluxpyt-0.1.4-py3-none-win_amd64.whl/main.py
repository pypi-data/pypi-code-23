# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 12:23:46 2016

Main module of FluxPyt.

Collects user inputs.

All the modules are run through this.

@author: Trunil
"""


def main():
    """
    Main file for running FluxPyt.

    """

    import fluxpyt.build_model as bm
    import time
    import fluxpyt.create_atm_transition_equations as cae
    import fluxpyt.priliminary_fba as pf
    import fluxpyt.solve_mid_networks as smn
    import fluxpyt.input_substrate_emu as ise
    from copy import deepcopy
    from fluxpyt.solve_mfa_lm import solve_mfa_problem
    from fluxpyt.utility import space
    from fluxpyt.make_emu_networks import make_networks as mn2

    #t1 = time.time()

    # build model
    print("Enter file name: ")
    filename = input()
    filepath = filename + '.csv'

    print('\n\n\nIs data for natural isotope correction available (y/n)?')
    userInput = input()

    print('\n\n\nEnter Number of Iterations')
    numIter = input()

    [stoich_matrix, model_metabolite, model_isotope,
     mets, mids] = bm.build_model(filepath)

    measured_mids = smn.get_mids(mids)  # sorts mids in desired form
    measured_mids = deepcopy(measured_mids)

    # derive elementary reactions
    [mol_rxnIDs, elementary_rxn_list,
     moleculeList] = cae.create_atm_transition_equations(model_isotope[0],
                                                         model_isotope[1],
                                                         model_isotope[2],
                                                         model_isotope[6])
    space()
    print('\n\nlen(elementary_rxn_list): ', len(elementary_rxn_list))
    print('\n\n')
    for i in range(len(mol_rxnIDs)):
        print(mol_rxnIDs[i], ':  ', elementary_rxn_list[i])

    print('\n\nlength el rxns:',
          len(elementary_rxn_list), '\n\n',
          measured_mids[2])

    # get emu networks
    measured_emus = measured_mids[2]

    # read substrate input file
    substrate_file = 'substrate_input.csv'
    substrate_mids = ise.cal_substrate_mid(substrate_file,
                                           elementary_rxn_list)
    space()
    print('\n\nsubstrate mids...\n')
    for i in range(len(substrate_mids[0])):
        print('\n', substrate_mids[0][i], '\n', substrate_mids[1][i])
    print(len(substrate_mids[0]))

    [rxnId_networks, rxn_networks] = mn2(mol_rxnIDs, elementary_rxn_list,
                                         measured_emus, substrate_mids[0])
    space()
    print('*' * 50)

    # perform preliminary fba for getting flux variabilities
    [bounds, initial_sol] = pf.priliminary_fba(model_metabolite, stoich_matrix)
    space()
    print('Reaction bounds:')
    for i in range(len(model_metabolite[0])):
        print(model_metabolite[0][i], ': ', bounds[i])

    # solve networks
    rates = [model_isotope[0], model_isotope[3]]

    # solve mfa problem using lmfit package
    print('\n\n', substrate_mids)
    t1 = time.time()

    [rxn_ids, optimal_flux_dist,
     best_out] = solve_mfa_problem(stoich_matrix, model_metabolite,
                                   rxnId_networks, rxn_networks, measured_mids,
                                   substrate_mids, rates, bounds, initial_sol,
                                   userInput, numIter=numIter)

    print('Time taken (min): ', (time.time() - t1) / 60)

    space()
    print('Optimization completed. \n\nIs network diagram template available? \
           (y/n)')
    diagTag = input()
    diagTag = diagTag.lower()

    if diagTag == 'y':
        from fluxpyt.draw_flux_map import draw_flux_map
        draw_flux_map(filename)

    print('\n\n\nTime taken(s): ', round((time.time() - t1) / 60, 1),
          'minutes')

    space()
    print('Flux estimation completed. \n\nDo you want to perform \
          Monte Carlo analysis to estimate flux standard errors? (y/n)')
    confTag = input()

    confTag = confTag.lower()
    if confTag == 'y':

        print('\n\n\nEnter number of data sets to be generated. (default=500)')
        num_data = input()

        if num_data == '':
            print('\nNo input given. Using default value 500.')
            num_data = 500

        space()
        print('Performing Monte Carlo...')

        from fluxpyt.monte_carlo import monte_carlo
        t2 = time.time()
        monte_carlo(int(num_data))
        print('\n\n\nTime taken(s): ',
              round((time.time() - t2) / 60, 1), 'minutes')
    else:
        space()
        print('Optimization results are stored as pickle file.\n \
              You can estimate confidence intervals later.')
