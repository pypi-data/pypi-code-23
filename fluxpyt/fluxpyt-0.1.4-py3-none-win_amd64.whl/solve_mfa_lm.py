# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 10:55:41 2017

Function to solve MFA problem using lmfit package

@author: Trunil
"""

from lmfit import Parameters, fit_report, Minimizer
import numpy as np
import random
from copy import deepcopy
from fluxpyt.utility import space
from fluxpyt.mid_corr import mid_correct
import sympy as sp
from fluxpyt.free_flux_null import get_null_mat


def solve_mfa_problem(stoich_matrix, model_metabolite, rxnId_networks,
                      rxn_networks, measured_mids, substrate_mids,
                      rates, bounds, initial_sol, userInput,
                      optimal_flux_dist=[], extra_params=[], **kws):

    random.seed(0)
    write_opt_data = True

    import pickle
    from scipy.stats import chi2

    stoich_matrix_g = deepcopy(stoich_matrix)
    model_metabolite_g = deepcopy(model_metabolite)
    rxnId_networks_g = deepcopy(rxnId_networks)
    rxn_networks_g = deepcopy(rxn_networks)
    measured_mids_g = deepcopy(measured_mids)
    substrate_mids_g = deepcopy(substrate_mids)
    rates_g = deepcopy(rates)
    bounds_g = deepcopy(bounds)
    fixed_flux = extra_params

    if len(fixed_flux) != 0:
        write_opt_data = False

    # Read correction file
    filename = 'corr_file.csv'
    file = open(filename)
    lines = file.readlines()
    corr_data = []
    for line in lines:
        line = line[0:-1]
        data = line.split(',')
        corr_data.append(data)

#    global corrFlag
    if userInput == 'Y' or userInput == 'y':
        corrFlag = True
    elif userInput == 'N' or userInput == 'n':
        corrFlag = False
    else:
        corrFlag = False
        print('\nNo input given, correction of mids will not be performed.')

    f = open('corr_data_pickle.pckl', 'wb')
    corr_data_pickle = [corrFlag, corr_data]
    pickle.dump(corr_data_pickle, f)
    f.close()
    del corr_data_pickle

    # free flux through nullspace()
    [null_mat, free_ind] = get_null_mat(stoich_matrix, model_metabolite)

    rxn_ids = model_metabolite[0]
    free_ind = [x for x in free_ind]
    flux_dist_g = [rxn_ids, initial_sol]
    basis = model_metabolite[3]
    std_dev = model_metabolite[4]
    p_basis = model_metabolite[6][0]

    if len(optimal_flux_dist) != 0:
        measurements = deepcopy(measured_mids[0])
        error = deepcopy(measured_mids[1])
        fcn_kws = {'optimal_flux_dist': optimal_flux_dist,
                   'rxnId_networks': rxnId_networks,
                   'rxn_networks': rxn_networks,
                   'substrate_mids': substrate_mids,
                   'rates': rates, 'null_mat': null_mat,
                   'measured_mids': measured_mids, 'flux_dist_g': flux_dist_g,
                   'fixed_flux': fixed_flux, 'corrFlag': corrFlag,
                   'corr_data': corr_data,
                   'measurements': measurements, 'error': error}
        measurements = deepcopy(measured_mids[0])
        error = deepcopy(measured_mids[1])
        res = residual(fixed_flux, optimal_flux_dist=optimal_flux_dist,
                       rxnId_networks=rxnId_networks,
                       rxn_networks=rxn_networks,
                       substrate_mids=substrate_mids,
                       rates=rates, null_mat=null_mat,
                       measured_mids=measured_mids, flux_dist_g=flux_dist_g,
                       fixed_flux=fixed_flux, corrFlag=corrFlag,
                       corr_data=corr_data, measurements=measurements,
                       error=error)
        return sum(res)

    else:
        # decide number of iterations

        try:
            numIter = int(kws['numIter'])
            if numIter == '':
                numIter = 10
        except:
            numIter = 10

        iteration = 0
        rejection = 0
        chi2_v = sum([10**22] * len(measured_mids_g[1]))

        while iteration < numIter:
            print('\n\n\nIteration: ', iteration + 1)

            measurements = deepcopy(measured_mids[0])
            error = deepcopy(measured_mids[1])

            try:
                params = kws['prev_params']
                write_opt_data = False

                if len(fixed_flux) != 0:
                    if fixed_flux[0] == 'conf_int_flag':
                        # when calculating confidence interval
                        sel_key = fixed_flux[1]
                        params[sel_key].value = fixed_flux[2]
                        params[sel_key].vary = False

            except:
                params = Parameters()

                for i in free_ind:

                    rxn = rxn_ids[i] + '_' + str(i)
                    lbb = bounds[i][0]
                    ubb = bounds[i][1]
                    val = random.uniform(lbb, ubb)

                    if basis[i] == '':
                        params.add(rxn, value=val, vary=True,
                                   min=0, max=p_basis*15)
                    else:
                        basis_val = float(basis[i])
                        if std_dev[i] == '':
                            params.add(rxn, value=basis_val, vary=False)
                        else:
                            std_dev_i = float(std_dev[i])
                            params.add(rxn, value=basis_val+std_dev_i, vary=True,
                                       min=basis_val - 3 * std_dev_i,
                                       max=basis_val + 3 * std_dev_i)
                            
            #measurements = deepcopy(measured_mids[0])
            #error = deepcopy(measured_mids[1])

            global best_par

    ##########################################################################

            fcn_kws = {'optimal_flux_dist': optimal_flux_dist,
                       'rxnId_networks': rxnId_networks,
                       'rxn_networks': rxn_networks,
                       'substrate_mids': substrate_mids, 'rates': rates,
                       'null_mat': null_mat, 'measured_mids': measured_mids,
                       'flux_dist_g': flux_dist_g,
                       'fixed_flux': fixed_flux, 'corrFlag': corrFlag,
                       'corr_data': corr_data,
                       'measurements': measurements, 'error': error}

            mini = Minimizer(residual, params, fcn_kws=fcn_kws,
                             iter_cb=iter_cb)
            out = mini.minimize(method='least_squares', max_nfev=10000)

    #########################################################################
            df = out.nfree
            chi2_cutoff = chi2.isf(0.05, df)
            print('Iteration No.: ', iteration + 1,
                  '  Chi-square: ', out.chisqr)

            if out.chisqr >= sum([10**10] * len(measured_mids_g[1])):
                rejection += 1
            else:
                rejection = 0
                iteration += 1

            if rejection >= 100:
                print('Minimization terminated.')
                continue

            # check if this is best solution and select
            if out.chisqr < chi2_v and out.chisqr > 0:
                # and sum_rxn_fluxes < min_sum_fluxes:
                chi2_v = deepcopy(out.chisqr)
                best_param = deepcopy(out.params)
                best_out = deepcopy(out)

        flx = []
        for key in best_param.keys():

            flx.append(best_param[key].value)

        flx = deepcopy(sp.Matrix(flx))
        sol = null_mat * flx
        fluxes = [z for z in sol]
        optimal_flux_dist = [[], []]
        for n in range(len(rxn_ids)):
            optimal_flux_dist[0].append(rxn_ids[n])
            optimal_flux_dist[1].append(fluxes[n])

        if write_opt_data is True:
            space()
            print('*' * 40)
            print('\nBest Solution is:\n\n')
            f4 = open('optimal_solution.csv', 'w')

            optimal_flux_dist = [[], []]
            for n in range(len(rxn_ids)):
                optimal_flux_dist[0].append(rxn_ids[n])
                optimal_flux_dist[1].append(fluxes[n])
                f4.write(rxn_ids[n])
                f4.write(',')
                fl = '{:0.2f}'.format(fluxes[n])
                f4.write(str(fl))
                f4.write('\n')
                print(rxn_ids[n], '\t', fluxes[n])

            f4.write('\n\n\nSSR:, ')
            f4.write(str(best_out.chisqr))
            f4.write('\n\nChi2 cutoff, ')
            f4.write(str(chi2_cutoff))
            print('\n\nbest_out.chisqr: ', best_out.chisqr)
            print('chi2 cutoff: ', chi2_cutoff)
            f4.close()

            space()
            print(fit_report(best_out))

            if corrFlag is True:
                corrFlag = 'y'
            else:
                corrFlag = 'n'

            optimization_data = [best_out, null_mat, stoich_matrix_g,
                                 model_metabolite_g,
                                 rxnId_networks_g, rxn_networks_g,
                                 measured_mids_g, substrate_mids_g, rates_g,
                                 bounds_g, userInput, best_out,
                                 optimal_flux_dist, initial_sol]
            f = open('optimization_data.pckl', 'wb')
            pickle.dump(optimization_data, f)
            f.close()
            del optimization_data

            optimization_data = [mini, best_out]
            import pickle
            f = open('optimization_data_cf.pckl', 'wb')
            pickle.dump(optimization_data, f)
            f.close()
            del optimization_data

            # for writing calculated mids in a file
            f1 = open('calculated_mids.pckl', 'rb')
            cal = pickle.load(f1)
            f1.close()
            f = open('calulated_mids.txt', 'w')
            f.write('Calculated mids\n')
            for value in cal:
                vl = '{:0.4f}'.format(value)
                f.write(str(vl) + '\n')
            f.close()

            # plot
            import matplotlib.pyplot as plt
            diff_mids = []
            for k in range(len(cal)):
                diff_mids.append(cal[k] - measured_mids[0][k])
            x = np.array(range(1, len(cal) + 1))
            y = np.array(diff_mids)
            fig = plt.figure()
            ax1 = fig.add_subplot(111)
            ax1.bar(x, y, label='calculated mids - measured mids', width=0.1)
            ax1.spines['left'].set_position('zero')
            ax1.spines['bottom'].set_position('zero')
            ax1.spines['right'].set_color('none')
            ax1.spines['top'].set_color('none')
            ax1.set_ylim([min(y) * 1.5, max(y) * 1.5])
            ax1.set_xticks([])
            plt.legend(loc='upper left')
            plt.savefig('mid_dev.png', format='png', dpi=400)
            plt.show()

        return rxn_ids, optimal_flux_dist, best_out


def prob_func(x):
    from scipy.stats import chi2
    print('\n\n', locals())
    return chi2.pdf(x, 1)


def residual(params, **kws):  # (params,x,data,error)

    rxnId_networks_g = kws['rxnId_networks']
    optimal_flux_dist_g = kws['optimal_flux_dist']
    rxn_networks_g = kws['rxn_networks']
    substrate_mids_g = kws['substrate_mids']
    rates_g = kws['rates']
    null_mat = kws['null_mat']
    measured_mids_g = kws['measured_mids']
    flux_dist_g = kws['flux_dist_g']
    fixed_flux = kws['fixed_flux']
    corrFlag = kws['corrFlag']
    corr_data = kws['corr_data']
    measurements = kws['measurements']
    error = kws['error']

    import math
    from fluxpyt.solve_mid_networks import solve_mid_networks

    if len(optimal_flux_dist_g) != 0:  # when calculating flux estimates

        flux_dist_g[1] = deepcopy(optimal_flux_dist_g[1])
        ind = int(params[0].split('_')[1])
        flux_dist_g[1][ind] = params[1]

    else:
        flx = []
        for key in params.keys():
            flx.append(params[key].value)

        flx = deepcopy(sp.Matrix(flx))

        sol = null_mat * flx
        fluxes = [z for z in sol]

        infeasible = np.array([10 ** 10] * len(measured_mids_g[1]))
        check_neg = [z for z in fluxes if z < 0.0]

        if len(check_neg) > 0:
            return infeasible

        # get flux ditribution

        flux_dist_g[1] = deepcopy(fluxes)  # write the flux values

        if len(fixed_flux) != 0:
            if fixed_flux[0] == 'conf_int_flag':
                # when calculating confidence interval

                ind_conf = int(fixed_flux[1].split('_')[1])
                flux_dist_g[1][ind_conf] = fixed_flux[2]

    cal_mids = solve_mid_networks(rxnId_networks_g, rxn_networks_g,
                                  substrate_mids_g, rates_g, flux_dist_g)

    if cal_mids is None:
        return infeasible

    # correct mids for natural abundance if applicable

    corrected_mids = correct_mids(cal_mids, measured_mids=measured_mids_g,
                                  corrFlag=corrFlag, corr_data=corr_data,
                                  measurements=measurements)

    cc = []
    for x in corrected_mids:
        if math.isnan(float(x)):
            cc.append(0.0)
        else:
            cc.append(x)

    corrected_mids = deepcopy(cc)

    msrd = np.array(deepcopy(measurements))
    cal = np.array(deepcopy(corrected_mids))
    erd = np.array(deepcopy(error))

    diff = abs(cal - msrd)
    dev = (diff/(erd ** 2) * diff) ** 0.5

    # store calculated mids for writing in file later
    import pickle
    f = open('calculated_mids.pckl', 'wb')
    pickle.dump(cal, f)
    f.close()

    return dev


def iter_cb(params, iter, resid, **kws):  # params, iter, resid, *args, **kws

    if iter % 100 is 0:
        print('nfev =', iter, '\tSSR =', sum(resid**2))


def correct_mids(cal_mids, **kws):

    measured_mids = kws['measured_mids']
    # meas_mid_list = kws['measured_mids'][0]
    # err_list = kws['measured_mids'][1]
    corrFlag = kws['corrFlag']
    corr_data = kws['corr_data']
    # measurements = kws['measurements']
    cal_mid_list = []

    # select and arrange calculated mids according to measured mids
    for i in range(len(measured_mids[2])): #iterate over measured emus
        meas_emu = measured_mids[2][i]

        assert meas_emu in cal_mids[0], '%s not found in calculated emus'

        if corrFlag is True:

            meas_emu = corr_data[i][0]
            mol_formula = corr_data[i][1]
            num_obs = int(corr_data[i][2])
            max_obs = int(corr_data[i][3])
        else:
            num_obs = int(corr_data[i][2])

        for j in range(len(cal_mids[0])):  # iterate over calculated emus
            cal_emu = cal_mids[0][j]
            mid = cal_mids[1][j]

            if cal_emu == meas_emu:

                if corrFlag is True:

                    corr_mid = mid_correct(meas_emu, mol_formula,
                                           num_obs, max_obs, mid)
                    tmp = []

                    for ar in corr_mid:
                        tmp.append(list(ar)[0])

                else:
                    corr_mid = mid[0:num_obs]
                    tmp = []

                    for ar in corr_mid:
                        tmp.append(ar)

                corr_mid = deepcopy(tmp)
                cal_mid_list += list(corr_mid)
                break

    return cal_mid_list


def make_objective(rxnId, rxnList):
    ind = rxnList.index(rxnId)
    nc = np.zeros(len(rxnList))
    nc[ind] = 1
    c = deepcopy(nc)
    return c
