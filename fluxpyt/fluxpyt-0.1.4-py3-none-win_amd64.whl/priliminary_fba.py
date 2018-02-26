# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 11:50:41 2016

@author: Trunil
"""
import numpy as np
from fluxpyt.glpk_solve import glpk_solve
from copy import deepcopy


def priliminary_fba(model_metabolite, stoich_matrix):
    '''
    Checks model feasibility. Returns flux variability and initial solution.
    '''

    print(stoich_matrix)
    [mat, c, b, bounds] = create_objective(stoich_matrix, model_metabolite, maximize=False)
    rxnNames = deepcopy(model_metabolite[0])
    rxnNames.append('pseudo')

    f = glpk_solve(mat, c, b, bounds, rxnNames, maximize=False)  # for glpk

    assert f.status == 'OPTIMAL', 'No feasible solution found for the basis provided'

    solution = sort_glpk_solution(f.x, rxnNames)

    rxnList = model_metabolite[0]
    flux_var = []
    print('\nflux variabilities')

    for rxn in rxnList:
        variability = flux_range(rxn, model_metabolite, stoich_matrix, bounds)
        flux_var.append(variability)

    return flux_var,solution


def sort_glpk_solution(glpk_solution, rxnNames):

    rx = list(glpk_solution[0])
    vals = list(glpk_solution[1])

    sorted_vals = []
    for r in rxnNames:

        ind = rx.index(r)
        sorted_vals.append(float(vals[ind]))

    solution = [rxnNames, sorted_vals]
    return solution


def flux_variability(stoich_matrix, model_metabolite, bounds):

    rxnList = model_metabolite[0]
    flux_var = []
    model_metabolite[0]
    for rxn in rxnList:
        variability = flux_range(rxn, model_metabolite, stoich_matrix, bounds)
        flux_var.append(variability)

    return flux_var


def flux_range(rxnId, model_metabolite, stoich_matrix, bounds):

    rxnInd = model_metabolite[0].index(rxnId)
    [mat,c,b,bounds] = create_objective(stoich_matrix,model_metabolite,rxnInd,maximize=False)
    c_min = deepcopy(c)
    c_max = [x*-1 for x in c_min]
    minFlux =  glpk_solve(mat, c, b, bounds, model_metabolite[0], maximize=False)
    assert minFlux.status == 'OPTIMAL', 'No feasible solution found for the basis provided.'

    maxFlux =  glpk_solve(mat, c, b, bounds, model_metabolite[0], maximize=True)
    assert maxFlux.status == 'OPTIMAL', 'No feasible solution found for the basis provided.'

    variability = (minFlux.objective,maxFlux.objective)

    return variability


def create_objective(stoich_matrix, model_metabolite, rxnInd='minTotal',
                     maximize=False, boundTag=True):
    """
    Set objective as minimization of total fluxes.
       rxnInd = indice of rxn to be be made the objective.
       maximize = True if objective is to maximize the objective function.
    """

    if rxnInd == 'minTotal':

        [nrow, ncol] = np.shape(stoich_matrix)
        x = np.ones(ncol)
        y = np.zeros((nrow + 1, 1))
        mat = np.vstack((stoich_matrix, x))

        mat = np.hstack((mat, y))
        mat[-1, -1] = -1
        c = np.zeros((ncol + 1))

        if maximize is False:
            c[-1] = 1
        else:
            c[-1] = -1
        b = np.zeros(nrow + 1)
        if boundTag is True:
            bounds = make_bounds(model_metabolite, minTotal=True)
            return mat, c, b, bounds
    else:
        [nrow, ncol] = np.shape(stoich_matrix)
        c = np.zeros((ncol))
        if maximize is False:
            c[rxnInd] = 1
        else:
            c[rxnInd] = -1
        b = np.zeros(nrow)
        mat = stoich_matrix
        if boundTag is True:
            bounds = make_bounds(model_metabolite)
            return mat, c, b, bounds

    return mat, c, b

def make_bounds(model_metabolite, minTotal=False):
    """
    Create reaction bounds.
      if minTotal == True then extra bound is added to acomodate for the pseudoreaction
    """

    basis = model_metabolite[3]

    p_basis = model_metabolite[6][0]

    deviation = model_metabolite[4]
    bounds = []

    for i in range(len(basis)):
        base = basis[i]
        dev = deviation[i]
        if base == '' and (dev == '' or not(dev.isnumeric())) or base == 'X':
            if model_metabolite[5][i] != 'R':
                b = (0, p_basis * 15)
                bounds.append(b)
            elif model_metabolite[5][i] == 'BR':
                b = (-p_basis * 15, p_basis * 15)
                bounds.append(b)
            else:

                ubb = p_basis * 15
                b = (0, ubb)
                bounds.append(b)
        elif base != '' and (dev == ''):

            assert float(base), 'Error: basis entry might not be a numeral'
            base = float(base)
            b = (base, base)
            bounds.append(b)

        elif base != '' and dev != '':

            assert float(base), 'Error: basis entry might not be a numeral'
            base = float(base)
            dev = float(dev)

            assert float(dev), 'Error: deviation entry might not be a numeral'
            b = (base - dev, base + dev)
            bounds.append(b)

    if minTotal is True:
        bounds.append((0, 5000))

    return bounds
