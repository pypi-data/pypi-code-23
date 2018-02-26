# -*- coding: utf-8 -*-
"""
Created on Sat Feb  6 21:09:50 2016

@author: Trunil

Reads and build model from csv.
Note 2Jul2016: this program reads csv model into stoichiometric matrix with
               list of rxns and metabolites

"""

from inspect import currentframe
import sys
from copy import deepcopy

'''********************************'''


def get_linenumber():
    '''
    Get line number in the code. Usefull to find which line of the code
    this function occurrs.
    '''

    cf = currentframe()
    return cf.f_back.f_lineno


def read_mfa_model(filename):
    '''
    Import and read csv file.
    Returns the model in lists that separate columns
    '''

    # import numpy as np
    file = open(filename)
    labels = file.readline()  # reads first column only

    lines = file.readlines()  # f2 has list of different lines

    # read the reactions
    rxnID = []
    formulae = []
    atm_trans = []
    rates = []
    rxnType = []
    basis = []
    deviation = []
    excludedMetabolites = []
    inputSubstrates = []
    measuredIsotopes = []
    mids = [[], [], []]

    c = 1
    for line in lines:
        if line[-1] == '\n':
            line = line[0:-1]
        line_split = line.split(',')
        if line_split[1] == '':
            continue
        elif line_split[1] == 'rxnEq':
            c = 1
        elif line_split[1] == 'excludedMetabolites':
            c = 2
        elif line_split[1] == 'inputSubstrates':
            c = 3
        elif line_split[1] == 'measuredIsotopes':
            c = 4
        elif line_split[1] == 'measurements':
            c = 5
        elif c == 1:
            rxnID.append(line_split[0])

            formula = line_split[1].split(' ')
            if '=' in formula:
                ind = formula.index('=')
                formula[ind] = '->'
                formula_string = ' '.join(formula)
                formulae.append(formula_string)
            elif '=>' in formula:
                ind = formula.index('=>')
                formula[ind] = '->'
                formula_string = ' '.join(formula)
                formulae.append(formula_string)
            else:
                formulae.append(line_split[1])


            # replace all arrow type to '->'
            trans = line_split[2].split(' ')
            if '=' in trans:
                ind = trans.index('=')
                trans[ind] = '->'
                trans_string = ' '.join(trans)
                atm_trans.append(trans_string)
            elif '=>' in trans:
                ind = trans.index('=>')
                trans[ind] = '->'
                trans_string = ' '.join(trans)
                atm_trans.append(trans_string)
            else:
                atm_trans.append(line_split[2])

            rates.append(line_split[3])
            rxnType.append(line_split[4])
            basis.append(line_split[5])

            if line_split[7] == '*':
                prime_basis = float(line_split[5])

            deviation.append(line_split[6])

        elif c == 2 and line_split[0] == '#':
            excludedMetabolites.append(line_split[1])
        elif c == 3 and line_split[0] == '#':
            inputSubstrates.append(line_split[1])
        elif c == 4 and line_split[0] == '#':
            measuredIsotopes.append(line_split[1])

        elif c == 5 and line_split[0] == '#':
            mids[1].append(line_split[1])
            mids[2].append(line_split[2])

        mids[0] = measuredIsotopes

    # separate these reactions into metabolite model and isotopomer model
    model_metabolite = [[], [], [], [], [], [], []]
    model_isotope = [[], [], [], [], [], []]

    for i in range(len(rxnID)):
        if (rxnType[i] == 'F' or rxnType[i] == 'FR' or
                rxnType[i] == 'R' or rxnType[i] == 'B' or
                rxnType[i] == 'BR' or rxnType[i] == 'BRR'):
            # metabolites balnce needed
            model_metabolite[0].append(rxnID[i])
            model_metabolite[1].append(formulae[i])
            model_metabolite[2].append(rates[i])
            model_metabolite[3].append(basis[i])
            model_metabolite[4].append(deviation[i])
            model_metabolite[5].append(rxnType[i])
    model_metabolite[6].append(prime_basis)

    for i in range(len(rxnID)):
        if (rxnType[i] == 'F' or rxnType[i] == 'FR' or
                rxnType[i] == 'R' or rxnType[i] == 'S' or
                rxnType[i] == 'SF'):

            model_isotope[0].append(rxnID[i])
            model_isotope[1].append(formulae[i])
            model_isotope[2].append(atm_trans[i])
            model_isotope[3].append(rates[i])
            model_isotope[4].append(basis[i])
            model_isotope[5].append(deviation[i])

    model_isotope.append(measuredIsotopes)  # form model_isotope[6]

    file.close()

    # ***********************************************************************
    # sort model_metabolite in appropriate order
    print(len(model_metabolite), len(model_metabolite[0]))
    print(model_metabolite[3])

    dc = {'FR': 1, 'F': 2, 'B': 3, 'BR': 1.5, 'R': 6, 'X': 4, 'Basis': 5}
    model_tmp = []
    for j in range(len(model_metabolite[0])):
        # print(model_metabolite[5])
        if model_metabolite[3][j] == '':  # is not measured basis
            ln_tmp = [dc[model_metabolite[5][j]]]
        elif model_metabolite[3][j] == 'X':  # choosen as free flux by user
            ln_tmp = [dc['X']]
            model_metabolite[3][j] = ''
        else:
            ln_tmp = [dc['Basis']]

        ln_tmp.append(model_metabolite[0][j])
        ln_tmp.append(model_metabolite[1][j])
        ln_tmp.append(model_metabolite[2][j])
        ln_tmp.append(model_metabolite[3][j])
        ln_tmp.append(model_metabolite[4][j])
        ln_tmp.append(model_metabolite[5][j])
        model_tmp.append(ln_tmp)

    model_tmp = sorted(model_tmp)

    model_metabolite = model_metabolite = [[], [], [], [], [], [], []]
    model_metabolite[6].append(prime_basis)

    for k in model_tmp:
        model_metabolite[0].append(k[1])
        model_metabolite[1].append(k[2])
        model_metabolite[2].append(k[3])
        model_metabolite[3].append(k[4])
        model_metabolite[4].append(k[5])
        model_metabolite[5].append(k[6])

    return model_metabolite, model_isotope, excludedMetabolites, \
        inputSubstrates, mids


def metabolite_list(reaction_formulae, excludedMetabolites=[]):
    '''
    Make list of metabolites from reaction formula.
    sReactions must be written in form:
        A -> 2 B
        C <- A + B
        A + B <-> C
    '''

    mets = []

    for formula in reaction_formulae:

        fr = formula.rsplit(' ')

        for el in fr:

            if not(el == '->' or el == '+' or
                   el.find('.') >= 0 or el.isnumeric()):
                if el not in mets and el not in excludedMetabolites:
                    mets.append(el)

    return mets


def modify_rxn_for_S(rxn,excludedMetabolites=[]):

    rxn_split = rxn.split()

    while '+' in rxn_split:
        rxn_split.remove('+')

    new_rxn = []
    i = 0
    while i < len(rxn_split):
        el = rxn_split[i]
        if (i != len(rxn_split) - 1) and (el.find('.') >= 0 or el.isnumeric()):
            # if coeff
            if rxn_split[i + 1] not in excludedMetabolites:
                new_rxn.append(el)
        elif el not in excludedMetabolites:
            new_rxn.append(el)

        i += 1

    return new_rxn


def make_stoich_matrix(reactions, reaction_formulae, excludedMetabolites=[]):
    """
    Stoichiometric matrix (S) from reaction formulae.

    Reactions must be written in form:
       A -> 2 B
       A + B <-> C
    """
    import numpy as np

    mets = deepcopy(metabolite_list(reaction_formulae, excludedMetabolites))

    ncol = len(reactions)
    nrow = len(mets)

    S = np.zeros([nrow, ncol])  # initialize S

    # iterate over each reaction
    r = 0  # reaction number
    for rxn in reaction_formulae:

        frtmp = modify_rxn_for_S(rxn, excludedMetabolites)

        fr = []
        for k in range(len(frtmp)):
            fs = frtmp[k]

            if fs in excludedMetabolites:
                continue

            elif fs != '':
                fr.append(fs)

        for i in range(len(fr)):
            if fr[i] == '->' or fr[i] == '<->':
                dp = deepcopy(i)  # division point
                break

        while '+' in fr:
            fr.remove('+')

        # iterate over elements in fr

        if dp == 0:
            c = 1
        else:
            c = 0  # element number
        while c < len(fr):

            if fr[c] == '+' or fr[c] == '->' or fr[c] == '<->':
                c = c + 1  # ignores + sign or

            if c < dp:
                k = -1  # multiplication factor for stoichiometric matrix element
            elif c > dp:
                k = 1
            else:
                c = c+1

            if c + 1 > len(fr):
                '''this condition was added because when there are no products
                   in equation, error was shown
                '''

                break
                # loops out of while loop as there is not element after this

            element = fr[c]

            # check if the character is stoichiometric coefficient
            # of metabolite
            if element.isnumeric() or element.find('.') >= 0:

                val = float(element)
                if c + 1 == len(fr):
                    c += 1
                else:

                    m = fr[c + 1]
                    # the metabolite will be next to the coefficient

                    met_ind = mets.index(m)

                    S[met_ind][r] = S[met_ind][r] + k * val
                    import math
                    if math.isnan(float(S[met_ind][r])):
                        print('\n Error: nan value in stoichiometric matrix.')
                        sys.exit()
                    c += 1

            else:
                val = 1
                m = fr[c]

                met_ind = mets.index(m)

                S[met_ind][r] = S[met_ind][r] + k * val
                import math
                if math.isnan(float(S[met_ind][r])):
                    print('\n Error: nan value in stoichiometric matrix.')
                    sys.exit()

            c += 1

        r += 1

    return S


def build_model(fileName):
    """Build model from csv file."""
    print('Building model from csv')
    [model_metabolite, model_isotope, excludedMetabolites,
     inputSubstrates, mids] = read_mfa_model(fileName)

    mets = metabolite_list(model_metabolite[1], excludedMetabolites)
    stoich_matrix = make_stoich_matrix(model_metabolite[0],
                                       model_metabolite[1],
                                       excludedMetabolites)

    return stoich_matrix, model_metabolite, model_isotope, mets, mids


def test_model_build():
    """Test build_model."""
    [model_metabolite, model_isotope,
     excludedMetabolites, inputSubstrates,
     mids] = read_mfa_model('glut_WT.csv')

    mets = metabolite_list(model_metabolite[1], excludedMetabolites)

    S = make_stoich_matrix(model_metabolite[0], model_metabolite[1],
                           excludedMetabolites)
