# -*- coding: utf-8 -*-
"""
Solves the elementory metabolite unit networks.
   
Solves mids for only one set of flux_distribution

Created on Fri Jul 15 10:57:23 2016

@author: Trunil

"""

import numpy as np
from fluxpyt.utility import split_rxn
from scipy.signal import convolve
from copy import deepcopy 


def solve_mid_networks(rxnId_networks,rxn_networks,substrate_mids,rates,flux_dist):
    
 
    
    #make matrices and solve. 
    known_mids = deepcopy(substrate_mids) #initialize before testing each individual set of fluxes

#    f = open('tmp.txt','w')
#    f.close()
    for i in range(len(rxn_networks)): 
        
       
        emu_net = rxn_networks[i]
        rxn_ids = rxnId_networks[i]
      
        
        cal_mids = solve_network(rxn_ids,emu_net,known_mids,rates,flux_dist)
        
        if cal_mids == None:
            return None
        else:
            known_mids = append_mids(known_mids,cal_mids)

    return known_mids
        
     

def solve_network(rxn_ids,emu_net,known_mids,rates,flux_dist):

    #rearrange fluxdist and rates
    fluxes = [[],[]] # [ids,values]
    for i in range(len(rxn_ids)):
        r = rxn_ids[i]
       
        if r in flux_dist[0]:
            ind = flux_dist[0].index(r) 
            fluxes[0].append(r)
            fluxes[1].append(flux_dist[1][ind])
        elif r in rates[0]:
            ind = rates[0].index(r)
            fluxes[0].append(r)

            fluxes[1].append(float(rates[1][ind]))

#    get number of known and unknown mids and sort them
    known = []
    unknown = []
    dim_known = 0
    dim_unknown = 0

    for i in range(len(rxn_ids)):
        rxn = emu_net[i]
        rxn_split = split_rxn(rxn)
        coeff = rxn_split[0::2]
        rxn_split = rxn_split[1::2]
    
        
        if len(rxn_split) == 2: #linear reactions
            for el in rxn_split:
                if el in known_mids[0] and el not in known: #if a known mid but not added yet
                    
                    known.append(el)
                    dim_known += 1
                elif el not in unknown and el not in known: #not a known mid but not added in unknown || added on 18Apr2017
                    unknown.append(el)
                    dim_unknown += 1 
        else: #convolutions
            reac = rxn_split[0:-1]
            prod = rxn_split[-1]
#            print('\n\n\nprod: ',prod)
            if prod in known_mids[0] and prod not in known:#check product
                known.append(prod)
                dim_known += 1
            elif prod not in unknown and prod not in known: #part after and was added on 18Apr2017
                unknown.append(prod)
                dim_unknown += 1  
            con_val = [1]     
            for el in reac: #check reactant
                if el not in known_mids[0]:
                    add_to = 'unknown'
                    break
                elif el in known_mids[0]:
                    add_to = 'known'
                    ix = known_mids[0].index(el)
                    con_val = convolve(con_val,known_mids[1][ix])
                        
                        
            if add_to == 'unknown':
                unknown.append(reac) #appended as whole list in form of string
                dim_unknown += 1
                
            elif add_to == 'known':
                known.append(reac) #appended as whole list
                known_mids[0].append(reac)
                
                known_mids[1].append(list(con_val))
                dim_known +=1
 
    #create matrices:    AB = CD
    #initialize
    '''where,
        A = square matrix with combination of reaction rates as elements
        B = unknown emus to be solved for
        C = matrix (num_unknown X emusize+1) matrix
        D = known emus'''
    
    #if there is no known mid in network
    if len(known) == 0:
        return None
        
    
    A = np.zeros((dim_unknown,dim_unknown))
    C = np.zeros((dim_unknown,dim_known))
    D = [] #this would be just set of known/previously calculated mids
    for k in known:
        k_ind = known_mids[0].index(k)
       
        D.append(known_mids[1][k_ind])
    D = np.array(D)
    
  
    
    #fill the matrices with values
    for i in range(len(rxn_ids)):
        rid = rxn_ids[i]
        rxn_ind = fluxes[0].index(rid) #indice of reaction in flux list
        rxn_split = split_rxn(emu_net[i]) #fluxes[0] = rxn_ids
        coeff = rxn_split[0::2]
        rxn_split = rxn_split[1::2]
        
        if len(rxn_split) > 2:
            convolve_tag = True
#      \n*************************\nconvolution'
        else:
            convolve_tag = False
#      \n###########################\nlinear'
        inds_unknown = []
        coeff_unknown = []
        inds_known = []
        coeff_known = []
              
        if convolve_tag == False:
            
            for p in range(len(rxn_split)): #find indices of emus in known or unknown list
                el = rxn_split[p]
                
                if el in unknown: #for matrix A
                    inds_unknown.append(unknown.index(el))
                    coeff_unknown.append(float(coeff[p]))
                elif el in known:
                    inds_known.append(known.index(el))
                    coeff_known.append(float(coeff[p]))
                    
            u_rxn = rxn_split.copy()
                
        if convolve_tag == True:
            conl = [rxn_split[0:-1]] #all reactants
            conl.append(rxn_split[-1])
          
            for el in conl:
                if el in unknown:
                    inds_unknown.append(unknown.index(el))
                    coeff_unknown.append(1) #have to figure if convolution reactions have diff coefficients
                elif el in known:
                    inds_known.append(known.index(el))
                    coeff_known.append(1)
            u_rxn = conl.copy()
        

        if len(inds_unknown) == len(u_rxn): #both molecules have unknown mids
           
            A[inds_unknown[1]][inds_unknown[1]] += fluxes[1][rxn_ind]*(-coeff_unknown[1])
            A[inds_unknown[1]][inds_unknown[0]] += fluxes[1][rxn_ind]*coeff_unknown[1]

        elif u_rxn[1] in unknown: #product has unknown mids or reactant has known mids

            A[inds_unknown[0]][inds_unknown[0]] += fluxes[1][rxn_ind]*(-coeff_unknown[0])
            C[inds_unknown[0]][inds_known[0]] += fluxes[1][rxn_ind]*(-coeff_known[0])

    #############################
    #write matrices if necessary
#    print(A.shape)
#    print(np.linalg.det(A))
#    f = open('tmp.txt','a')
#    for k in A:
#        for l in k:
#            w = str(l)+','
#            f.write(w)
#        f.write('\n')
#    f.close()
#    #sys.exit()
#    #############################

    if np.linalg.det(A) == 0:
        print('\n\nnp.linalg.det(A) == 0')
        return None

    #solve matrices
    CdotD = np.dot(C,D)
    B = np.linalg.solve(A,CdotD)
    
    nm = [list(x) for x in B]   
  
    cal_mids = [unknown,nm]
    
    
    return cal_mids
    
  
                           
def append_mids(mids1,mids2):
    '''used when we have two lists of mids. Joins these two ''' 

    for i in range(len(mids2[0])):
        emu = mids2[0][i]
        mid = mids2[1][i]
        if not(emu in mids1[0]):
            mids1[0].append(emu)
            mids1[1].append(mid)
    return mids1



    
def update_mids(rxnIds,rxns,mids):
    from collections import Counter
    
    
    #check known mids and derive mids of emus of linear reactions
    productList = []
    for rxn in rxns:
        productList.append(rxn.split()[-1])
        
    emuFreq = Counter(productList) #stores the number of times an emu is formed in the emu reactions
   
    for rxn in rxns:
        rxn_split = rxn.split()
        rxn_split.remove('->')
        if len(rxn_split) > 2:
            rxn_split.remove('+')
        
#        print('rxn_split',rxn_split,'\n\n')
        product = rxn_split[-1]
                           
        if len(rxn_split) == 2 and product in mids[0] and emuFreq[product] == 1: 
            '''if products mid is known, 
            occurs only one in emu reaction,
            and not involved in convolution reaction
            Its reactant will have same mid'''
        
            ind = mids[0].index(product)
#            print('\nproduct is found in linear reaction')
            mids[0].append(rxn_split[0])
            mids[1].append(mids[1][ind])
            
            '''This code is invcomplete and does not include convolution reactions'''

    return mids

def get_mids(mids):
    '''arranges mid values and emus in list'''
    modified_mids = [[],[]]
    measured_emus = mids[0]
    i = 0
    while i < len(mids[1]):
    
        
        vals = float(mids[1][i])
        err = float(mids[2][i])
        
        modified_mids[0].append(vals)
        modified_mids[1].append(err)
        
        i+=1
    
    modified_mids.append(measured_emus)
    return modified_mids
            