# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 11:07:25 2017

@author: Trunil
"""

def draw_flux_map(filename):
    '''
	Input: filename of flux diagram in svg format.
	'''
    import pickle
    
    #read pickle file
    f = open('optimization_data.pckl', 'rb')
    obj = pickle.load(f)
    
    global best_params,null_mat,stoich_matrix,model_metabolite,rxnId_networks,rxn_networks
    global measured_mids,substrate_mids,rates,bounds,userInput,y1,name,optimal_flux_dist
    global initial_sol,chi2_optimal   
    best_params = obj[0].params
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
    optimal_flux_dist = obj[12]
    rxnIds = optimal_flux_dist[0]
    initial_sol = obj[13]
    chi2_optimal = obj[0].chisqr
    f.close()
    
    # find net fluxes for reversible reactions
    rev_rxn_tuple = []
    comp = [] #rows added in rev_rxn_tuple
    ST = stoich_matrix.transpose()
    num_row = ST.shape[0]
    for i in range(num_row):
        rw_i = ST[i]
        num_non_neg = len([x for x in rw_i if x != 0])
        if i not in comp and num_non_neg > 1:
            comp.append(i)
            for j in range(num_row):
                rw_j = ST[j]
                sum_row = rw_i+rw_j
                check_non_neg = [x for x in sum_row if x != 0]
                if len(check_non_neg) == 0:
                    rev_rxn_tuple.append((model_metabolite[0][i],model_metabolite[0][j]))
                    comp.append(j)
    
    #calculate net fluxes for forward reaction:
    net_flux = [[],[]]
    for tpl in rev_rxn_tuple:
        sel_rxn1 = tpl[0]
        sel_rxn2 = tpl[1]
        ind1 = rxnIds.index(sel_rxn1)
        ind2 = rxnIds.index(sel_rxn2)
        net_flux[0].append(sel_rxn1)
        v1 = optimal_flux_dist[1][ind1]
        v2 = optimal_flux_dist[1][ind2]
        vv = v1-v2
        net_flux[1].append(vv)
        
        
        
    filepath = filename + '.svg'
    f = open(filepath,'r')
    lines = f.readlines()
    f.close()
    
    
    filepath2 = filename + '_fluxMap' + '.svg'
    f1 = open(filepath2,'w')
   
    for l in lines:
        l = str(l)
        
        for rxn in rxnIds:
            found = 0
            if rxn in l:
                found = 1
                ind = optimal_flux_dist[0].index(rxn)
                p = l.split(rxn)
                if rxn in net_flux[0]:
                    ind_rxn = net_flux[0].index(rxn)
                    flux1 = net_flux[1][ind_rxn]
                    flux = '{:0.3f}'.format(flux1)
                    
                else:
                    flux = optimal_flux_dist[1][ind]
                    flux = '{:0.3f}'.format(flux)
                    
                val = str(flux)
              
                q = val.join(p)
                
                f1.write(q)
               
                break
        if found == 0:
            f1.write(l)
                   
            
    f1.close()
    print('\nFlux map drawn.\n')