# -*- coding: utf-8 -*-
"""
Created on Sun Jun 25 12:36:28 2017

Monte Carlo for confidence interval estimation

@author: Trunil
"""

import fluxpyt.solve_mfa_lm as sml
import numpy as np
from fluxpyt.utility import space
import pickle
from copy import deepcopy
import sympy as sp
#from scipy.stats import truncnorm

    

#def get_truncated_normal(mean=0, std=1, low=0, upp=10):
#    '''https://stackoverflow.com/questions/36894191/how-to-get-a-normal-distribution-within-a-range-in-numpy'''
#    return truncnorm(
#        (low - mean) / std, (upp - mean) / std, loc=mean, scale=std)

def monte_carlo(num_data=500):
    
    '''
    
    num_data = number of data sets to be genrated for monte_carlo analysis
    numIter = number of iteration of least square minimazation for single data set
    '''

    np.random.seed(1)
    #read pickle file
    f = open('optimization_data.pckl', 'rb')
    obj = pickle.load(f)
    
    params = obj[0].params
    null_mat = obj[1]
    stoich_matrix = obj[2]
    model_metabolite = obj[3]
    rxnId_networks = obj[4]
    rxn_networks = obj[5]
    measured_mids = obj[6]
    substrate_mids = obj[7]
    rates = obj[8]
    bounds = obj[9]
    userInput = obj[10]
    optimal_solution = obj[12]
    f.close()

    #generate data sets based on std deviation

    #print(measured_mids)  
    data_set = []
    for i in range(len(measured_mids[0])):
        val = measured_mids[0][i]
        std = measured_mids[1][i] #val*0.4/100
        #print('kkk',num_data,type(num_data),numIter,type(numIter))
        #sys.exit()
        new_vals = list(np.random.normal(loc=val, scale=std, size=num_data))
        
        data_set.append(new_vals)

 
    #create list of empty list. Each list will store one reaction flux for all data sets
    all_fluxes = []
    SSRs = []
    for i in range(len(model_metabolite[0])):
        all_fluxes.append([])
    print(len(model_metabolite[0]))
    for data_iter in range(num_data):
        print('\n\ndata_iter',data_iter+1,'of', num_data,'data sets')
        #copy one set of measured mids
        meas = []
        for k in range(len(data_set)):
            meas.append(data_set[k][data_iter])
        
        measured_mids_new = [meas,measured_mids[1],measured_mids[2]]
        
        #generate initial solution
        flx = []
        for key in params.keys():
            flx.append(params[key].value)
            
        flx = deepcopy(sp.Matrix(flx))
        
        sol = null_mat*flx
        fluxes = np.array(sol)
        fluxes.real[abs(fluxes.real) < 0.000] = 0.0
        initial_sol = [model_metabolite[0],fluxes]
        
        [rxn_ids,fluxes,best_out] = sml.solve_mfa_problem(stoich_matrix,model_metabolite,rxnId_networks,rxn_networks,measured_mids_new,substrate_mids,rates,bounds,initial_sol,userInput,[],['CI'],numIter=1,prev_params=params)
                                               
        
        SSRs.append(best_out.chisqr)        
        for l in range(len(fluxes[1])):
            all_fluxes[l].append(fluxes[1][l])
            
    #print(all_fluxes)
    
    conf_interval = [rxn_ids,[],[],[],[],[],[]]       
    for flux_val in all_fluxes:
        sorted_flx = deepcopy(sorted(flux_val))
 #       n = len(sorted_flx)
 
       
        min_val_95 = np.percentile(sorted_flx,2.5)
        min_val_68 = np.percentile(sorted_flx,16)
        max_val_95 = np.percentile(sorted_flx,97.5)
        max_val_68 = np.percentile(sorted_flx,84)
        median_val = np.percentile(sorted_flx,50)
        min_val_68 = '{:0.2f}'.format(min_val_68)
        min_val_95 = '{:0.2f}'.format(min_val_95)
        max_val_68 = '{:0.2f}'.format(max_val_68)
        max_val_95 = '{:0.2f}'.format(max_val_95)
        median_val = '{:0.2f}'.format(median_val)
        conf_interval[1].append(min_val_95)
        conf_interval[2].append(min_val_68)
        conf_interval[3].append(median_val)
        conf_interval[4].append(max_val_68)
        conf_interval[5].append(max_val_95)
        
    #print confidence interval
    space()
    f = open('montecarlo_results.csv','w')
    f.write('Reactions,Optimal solution,2.5%P,16%P,50%P,68%P,97.5%P\n')
    for i in range(len(conf_interval[0])):
        print(conf_interval[0][i],': ',conf_interval[1][i])
        f.write(conf_interval[0][i])
        f.write(',')
        f.write(str(optimal_solution[1][i]))
        f.write(',')
        f.write(str(conf_interval[1][i]))
        f.write(',')
        f.write(str(conf_interval[2][i]))
        f.write(',')
        f.write(str(conf_interval[3][i]))
        f.write(',')
        f.write(str(conf_interval[4][i]))
        f.write(',')
        f.write(str(conf_interval[5][i]))
        f.write('\n')
    f.close()
    
    f = open('flux_std.pckl','wb')
    conf_interval_data = [rxn_ids,conf_interval,all_fluxes,SSRs]
    pickle.dump(conf_interval_data,f)
    f.close()
    
    
    #%% bootstrap
    from fluxpyt.bootstrap import bootstrap
    bootstrap(rxnList=rxn_ids)
    
    
    return conf_interval
            
        

