# -*- coding: utf-8 -*-
"""
Created on Mon Jul  4 12:46:38 2016

Generates elementary reaction list.


@author: Trunil
"""
from fluxpyt.utility import space,split_rxn,find
from copy import deepcopy

def rewrite_molecule(molecule,rxn,atm_rxn,mol_index):

    moleculeName = molecule.split(':')[0]
    mol_atoms = molecule.split(':')[1] # in the form F:1111,F:0111 etc
    atm_rxn_split = split_rxn(atm_rxn)
    rxn_split = split_rxn(rxn)
    atoms = atm_rxn_split[mol_index] # atoms of particular molecule from atom transition equation
    mod_mol = moleculeName + ':'

    for i in range(len(mol_atoms)):
        val = mol_atoms[i]
        if val == '1':
            mod_mol += atoms[i]

    return mod_mol

def insert_hash(list):

    new_list = []
    for el in list:
        new_list.append('#')
        new_list.append(el)
    return new_list

def get_coeff(rxn):

    output = [[],[]]
    rxn_split = split_rxn(rxn)
    rxn_split = insert_hash(rxn_split)

    i = 0
    while i <= len(rxn_split)-1:

        if rxn_split[i] == '#' and find(rxn_split[i+1],'.'): #is float
            output[0].append(rxn_split[i+3])
            output[1].append(rxn_split[i+1])
            i = i+4
        elif rxn_split[i] == '#' and rxn_split[i+1].isnumeric(): # if number
            output[0].append(rxn_split[i+3])
            output[1].append(rxn_split[i+1])
            i = i+4
        else: # if alphabetic
            output[0].append(rxn_split[i+1])
            output[1].append('1')
            i = i+2

    return output

def write_rxn_full(rxn):
    # rewrites reaction with coefficients even when coefficient = 1
    coeff_list = get_coeff(rxn)
    rxn1 = rxn.split('->')
    reactants = split_rxn(rxn1[0])
    if len(rxn1) > 1:
        products = split_rxn(rxn1[1])
    else:
        products = ''

    reaction = ''
    for i in range(len(reactants)):
        r = reactants[i]
        if r in coeff_list[0]:
            ind = coeff_list[0].index(r)
            coeff = coeff_list[1][ind]
            reaction = reaction + coeff + ' ' + r + ' + '
            coeff_list[0].remove(r)
            coeff_list[1].remove(coeff)
    reaction = reaction[0:-2]

    reaction = reaction + '->'
    if products != '':
        reaction = reaction + ' '
        for i in range(len(products)):
            r = products[i]
            if r in coeff_list[0]:
                ind = coeff_list[0].index(r)
                coeff = coeff_list[1][ind]
                reaction = reaction + coeff + ' ' + r + ' + '
                coeff_list[0].remove(r)
                coeff_list[1].remove(coeff)
        reaction = reaction[0:-3]

    return reaction

def get_formula(molecule,rxn,atm_rxn):
    #molecule ID should be in form 'moleculeName:atom-numbers'
    #There should be only one colon in the molecule ID

    # **********************************

    #write rxns in full coefficient forms
    rxn = write_rxn_full(rxn)
    atm_rxn = write_rxn_full(atm_rxn)

    moleculeName = molecule.split(':')[0]
    count = rxn.split('->')[1].count(moleculeName)   #only product side is relevant

   # print('\n****************************\ncount: ',moleculeName,count)
    rxn_split = split_rxn(rxn)
    atm_rxn_split = split_rxn(atm_rxn)

    mol_indices = find(rxn_split,moleculeName)

    assert moleculeName in rxn.split(), "molecule is not present in the reaction provided."
    formulae = []
    for indice in mol_indices:
        mod_mol = rewrite_molecule(molecule,rxn,atm_rxn,indice) #writes molecule in the form of moleculeName:abcd

        mol_split = mod_mol.split(':')
        reactant_atoms = atm_rxn.split('->')[0].split() #reactants from atm_rxn
        reactants = rxn.split('->')[0].split()

        mol_atoms = mol_split[1]

        mol_atoms = num_sort(mol_atoms)

        reac_list = []
        for c in range(len(reactants)):

            sel_met = reactants[c]
            sel_met_atoms = reactant_atoms[c] # contains atoms in particular molecule from atm_rxn

            ##ignore molecules whose carbon is not to be traced
            if sel_met_atoms == 'X':
                c += 1
                continue

            isrelevant = 0 #to see if atoms from reactant passes to molecule of interest
            new_atoms = ''
            for at in sel_met_atoms:
                if at in mol_atoms:
                    isrelevant = 1
                    new_atoms += '1'
                else:
                    new_atoms += '0'
            if isrelevant == 1: #means at least one atom transfers to product molecule of interest

                new_molecule = sel_met + ':' + new_atoms
                reac_list.append(new_molecule)

            c += 1

            #construct formula of elementary reaction

        formula = ''

        for j in range(len(reac_list)):
            #print('j',j)
            sel_reactant = reac_list[j]

            ix = rxn_split.index(sel_reactant.split(':')[0])

            if j == 0:
                formula = formula + rxn_split[ix-1] + ' ' + sel_reactant
                #rxn_split.remove(sel_reactant.split(':')[0])
                #formula = formula + sel_reactant
            elif j >= 0:
                formula += ' + ' + rxn_split[ix-1] + ' ' + sel_reactant

        ix = rxn_split.index(molecule.split(':')[0])

        formula += ' -> ' + rxn_split[ix-1] + ' ' + molecule

        formulae.append(formula)

    return formulae

def get_new_molecule(rxn,moleculeList,current_molecule):


    rxn_split = split_rxn(rxn)[1::2]

    new_molecules = []
    for molecule in rxn_split:

        if molecule.split(':')[0] != current_molecule:#ignores current molecule. The atomrenaming might add unwanted molecules.

            if molecule != '+' and molecule != '->' and molecule != '<->':
                if not(molecule in moleculeList):
                    mol_split = molecule.split(':')
#                    print()
                    if not(mol_split[1] == ''):
                        new_molecules.append(molecule)

    return new_molecules



def findMolRxns(rxnIDs,molecule,rxnList,atm_transition_rxns):
    molRxnList = []
    molAtmTransList = []
    mol_rxnIDs = []
    for i in range(len(rxnList)):
        rxn = rxnList[i]
        atm_tr = atm_transition_rxns[i]
        mol_rxnID = rxnIDs[i]
        #print('rxn.split(->)',rxn.split('->'), molecule,'\n',rxnList)
        rxn_split_1 = rxn.split('->')[1]
        rxn_split_2 = rxn_split_1.split()
        if molecule in rxn_split_2:
            molRxnList.append(rxn)
            molAtmTransList.append(atm_tr)
            mol_rxnIDs.append(mol_rxnID)
    return mol_rxnIDs,molRxnList,molAtmTransList


def create_atm_transition_equations(rxnIDs,rxnList,atm_transition_rxns,moleculeList):
    '''
    Input:
        rxnList = reaction formulae in form of list
        atm_transition_rxns = respective atom transition reaction list
        moleculeList = list of molecules observed (emu types e.g. A:0111)

    Output:
        reaction list with atom transitions,
        new metabolite (emu types) list
    '''
    print(moleculeList)
    elementary_rxn_list = []
    elementary_rxnIDs = []
    added_tpl = []
    #get the molecule name:
    mol_completed = [];
    while moleculeList:
        molecule = moleculeList.pop(0)
#        print('\n\n\nmolecule: ',molecule)
        '''iterates over one molecule at a time'''
        if molecule not in mol_completed:
            moleculeName = molecule.split(':')[0]

            #find reactions in which the molecule takes part
            [mol_rxnIDs,molRxnList,molAtmTransList] = findMolRxns(rxnIDs,moleculeName,rxnList,atm_transition_rxns)

            # molRxnList are reaction in which the molecule is formed.

            for numRxn in range(len(molRxnList)):

                '''gets one reaction formula'''
                rxn = molRxnList[numRxn]  #choose one reaction in which the molecule is formed.
                Id =  mol_rxnIDs[numRxn] # its ID
                atm_trans_rxn = molAtmTransList[numRxn] #its atom transition eq

                formulae = get_formula(molecule,rxn,atm_trans_rxn) #getting the elementory reaction formula

                formulae_tmp = []
                if len(formulae) > 1:

                    visited = []
                    for frm in formulae:
                        if frm not in visited:
                            visited.append(frm)
                            cn = formulae.count(frm)

                            frm_split = frm.split()

                            frm_split[-2] = str(float(frm_split[-2])*cn)
                            frm_1 = ' '.join(frm_split)

                            formulae_tmp.append(frm_1)

                    formulae = deepcopy(formulae_tmp)

                for formula in formulae:
                    tpl = (Id,formula)

                    if not(tpl in added_tpl):
                        added_tpl.append(tpl)
                        elementary_rxn_list.append(formula)
                        elementary_rxnIDs.append(Id)
                    formula_split = formula.split()
                    #add new metabolites to metabolite list
                    new_molecule_list = get_new_molecule(formula,moleculeList,moleculeName)
                    for nml in new_molecule_list:
                        moleculeList.append(nml)

        mol_completed.append(molecule)

    return elementary_rxnIDs,elementary_rxn_list,moleculeList

def num_sort(num):
    n_list = list(num)
    n_list.sort()
    return ''.join(n_list)


def test():
    rxnIDs = ['V1','V2','V3','V4']
    rxnList = ['ACCOA + OAA -> CIT','CIT + FADH2 + NADH -> 0.5 SUC + 0.5 SUC + CO2 + CO2','SUC -> OAA + FADH2 + NADH','OAA -> PS']
    atm_transition_rxns = ['ab + cdef -> fedbac','abcdef + X + X -> 0.5 abcd + 0.5 dcba + e + f','abcd -> abcd + X + X','abcd -> abcd']
    moleculeList = ['PS:1000']

    eq = create_atm_transition_equations(rxnIDs,rxnList,atm_transition_rxns,moleculeList)
    space()
    for r in eq[1]:print(r)
    print(len(eq[1]))
