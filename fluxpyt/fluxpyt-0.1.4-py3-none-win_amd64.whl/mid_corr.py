# -*- coding: utf-8 -*-
"""
Created on Wed Mar  8 12:03:26 2017

Adapted from function corrMatGen in Openflux

@author: Trunil
"""


import numpy as np
from scipy.signal import convolve



def corrMatGen(output_size, input_size=0, molecularFormula = '' ):
    
    '''
    function CM = corrMatGen(output_size, input_size, molform)
	
    Returns correction matrix.
	
    example: outputMDV = CM * inputMDV
	
	Inputs:
		output_size: int. length of output MDV (truncated length) (number of values in measured MID
							e.g. pyruvate has 3 carbons (ideally 4 mids) but only three are measured or detected.)
							
		input_size: int. lenght of input MDV (carbon backbone + 1)
		
		molform: molecular formula without carbon backbone.
	'''
    
    from fluxpyt.mid_vec_gen import mid_vec_gen as mvg 
    
    if molecularFormula == '':
        CM = np.eye(output_size,input_size)
        return CM
        
    else:
        
        
        # Natural isotope distribution. ref: van winden (2002), BnB
        C_dist = [0.9893, 0.0107]
        H_dist=[0.999885, 0.000115]
        N_dist=[0.99632, 0.00368]
        O_dist=[0.99757, 0.00038, 0.00205]
        Si_dist=[0.922297, 0.046832, 0.030872]
        S_dist=[0.9493, 0.0076, 0.0429, 0.0002]
        
        #extract molecules and coefficients from formula    
        pos = isletter(molecularFormula)
        atom = getAtoms(pos,molecularFormula)
        coeff = getCoefficients(pos,molecularFormula)
        #atom = atom.remove(atom[-1]) #for checking assert statement that follows this line
        
        assert len(coeff) == len(atom), "Error in molecular formula. Number of molecules not equal to number of coefficients."
        
        atoms = []
        for k in range(len(atom)):
            tmp = atom[k] + '_dist,' + coeff[k]
            atoms.append(tmp)
        
         
        CM = [1]
        
        for at in atoms:
        
            bb = eval('mvg('+at+')')

            CM = convolve(CM,eval('mvg('+at+')'))

        CM = stepCV(CM,input_size)

        #check if CM is matrix
        l = len(CM[0])
        for i in range(len(CM)):
           
            assert len(CM[i]) == l, 'CM is not a matrix'
            
        
        if output_size <= input_size:
            t_cm = []
            
            for i in range(len(CM)):
                t1 = CM[i][0:output_size]
                t_cm.append(t1)
                
        
        CM = np.array(t_cm)
        
       
                
                
    return np.transpose(CM)      
 
def corrMatGen1(output_row, input_size=0, molecularFormula = '' ):
    
    '''
    function CM = corrMatGen(output_size, input_size, molform)
	
    Generates correction matrix. 
	
    example: outputMDV = CM * inputMDV
	
	Inputs:
	
		output_row: list of output rows i.e. masses to be calculated
							e.g. [0,1,2] will give corrected mids of M+0 , M+1 and M+2 .
							
		input_size: int. lenght of input MDV (carbon backbone + 1)
		
		molform: molecular formula without carbon backbone.
	'''
    
    from fluxpyt.mid_vec_gen import mid_vec_gen as mvg 
    
    output_size = max(output_row)
    
    
    if molecularFormula == '':
        CM = np.eye(output_size,input_size)
        return CM
        
    else:
        
        # Natural isotope distribution. ref: van winden (2002), BnB
        C_dist = [0.9893, 0.0107]
        H_dist=[0.999885, 0.000115]
        N_dist=[0.99632, 0.00368]
        O_dist=[0.99757, 0.00038, 0.00205]
        Si_dist=[0.922297, 0.046832, 0.030872]
        S_dist=[0.9493, 0.0076, 0.0429, 0.0002]
        
        #extract molecules and coefficients from formula    
        pos = isletter(molecularFormula)
        atom = getAtoms(pos,molecularFormula)
        coeff = getCoefficients(pos,molecularFormula)
        #atom = atom.remove(atom[-1]) #for checking assert statement that follows this line
        
        assert len(coeff) == len(atom), "Error in molecular formula. Number of molecules not equal to number of coefficients."
        
        atoms = []
        for k in range(len(atom)):
            tmp = atom[k] + '_dist,' + coeff[k]
            atoms.append(tmp)
        
         
        CM = [1]
        
        for at in atoms:

            bb = eval('mvg('+at+')')

            CM = convolve(CM,eval('mvg('+at+')'))
            
        CM = stepCV(CM,input_size)
        
        #check if CM is matrix
        l = len(CM[0])
        for i in range(len(CM)):
           
            
            assert len(CM[i]) == l, 'CM is not a matrix'
            
        
        s1 = output_row[0]-1
        s2 = output_row[1]
        r = range(s1,s2)
        t_cm = []
        for ls in CM:
            t_cm1 = [] 
            for n in r:
                
                t_cm1 = t_cm1 + [ls[n]]
               
            t_cm.append(t_cm1)
        
            
    CM = np.array(t_cm)
        
       
                
                
    return np.transpose(CM)


           
            
def stepCV(CV,columns):
    
    
    cm = []
    for i in range(columns):
        
        
        t1 = []
        
        t2 = [0]*i
        t1 = t1+t2

        for item in CV:
            t1.append(item)
       
        cm.append(t1)
        
    for j in range(columns):
        diff = len(cm[columns-1])-len(cm[j])
        cm[j] = cm[j] + [0]*diff
       
    
    return cm
        
    
    

  
            

def getAtoms(pos,molecularFormula):
    atom = [];
    c = 0
    atom.append('')
    for i in pos:
        
        if i == 1:
            atom[-1] = atom[-1] + molecularFormula[c]
        elif atom[-1] != '' :
            atom.append('')
            
        c += 1
    atom.remove('')
        
    
    return atom
        
def getCoefficients(pos,molecularFormula):
    coeff = [];
    c = 0
    coeff.append('')
    for i in pos:
        
        if i == 0:
            coeff[-1] = coeff[-1] + molecularFormula[c]
        elif coeff[-1] != '' :
            coeff.append('')
            
        c += 1
    
    
    return coeff
            
    
 
def isletter(molecularFormula):
    pos = []
    
    for i in molecularFormula:
        
        try:
            
            int(i)
            pos.append(0)
            
        except ValueError:
            pos.append(1)
   
    return pos
    
 
def test():
    m1 = corrMatGen1([1,4],6,'C8H30N1O2Si2')
   
    m2 = corrMatGen(6,6,'C8H30N1O2Si2')
         
    val_mid = [0.019538558,0.03824121,0.115314163,0.200789473,0.153547716,0.0]
    
    mid = np.array(val_mid)
    mid.shape = [len(mid),1]
    
    numerator = np.dot(m1,mid)
    
    denominator = sum(np.dot(m2,mid))
    
    
    corr_mid = numerator/denominator
    
    print(corr_mid)

def mid_correct(emu,mol_formula,num_obs, max_obs,mid):
#    print('********************************')
#    print('\n\ninputs:\n',emu,mol_formula,num_obs,max_obs,mid)
    
    non_zero = [x for x in mid if x!= 0]
    if len(non_zero) == 0:
        return np.zeros((num_obs,1))
    
    m1 = eval('corrMatGen1([1,num_obs],max_obs,mol_formula)')
    m2 = eval('corrMatGen(max_obs,max_obs,mol_formula)')
    mid = np.array(mid)
    
    mid.shape = [len(mid),1]
    numerator = np.dot(m1,mid)
    denominator = sum(np.dot(m2,mid))
    corr_mid = numerator/denominator

    return corr_mid
    
