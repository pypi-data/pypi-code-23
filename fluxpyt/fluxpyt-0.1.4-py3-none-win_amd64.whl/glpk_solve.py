# -*- coding: utf-8 -*-
"""
Created on Sun Aug  7 12:37:26 2016

@author: Trunil
"""
from fluxpyt.utility import size
import os
from collections import namedtuple  # http://stackoverflow.com/questions/35988/c-like-structures-in-python
import sys

def glpk_solve(mat, c, b, bounds, rxnNames, maximize=False):

    if maximize is False:
        obj = 'Minimize'
    elif maximize is True:
        obj = 'Maximize'
    else:
        print('objective sense given is incorrect. \
              It should be either maximize or minimize.')
        sys.exit()

    # open file in writing mode
    with open("model.lp", "w") as model:
        # write objective
        model.write(obj + '\n')
        line = 'obj: '
        started = False

        for i in range(len(c)):
            if c[i] == 0:
                continue

            if started is False:
                line += str(c[i]) + ' ' + rxnNames[i] + ' '
                started = True
            else:
                line += '+ ' + str(c[i]) + ' ' + rxnNames[i] + ' '
            if len(line) > 220:  # max character in one line = 255. 220 selected for safety
                line += '\n'
                model.write(line)
                line = ''
        model.write(line + '\n')

        # write constraints
        model.write('Subject To \n')
        [nrows, ncols] = size(mat)
        for j in range(nrows):
            constr_name = ('c' + str(j + 1))
            vec = mat[j]
            write_constraint(constr_name, vec, rxnNames, model)

        # write bounds
        model.write('Bounds \n')
        for j in range(len(bounds)):
            lb = str(round(bounds[j][0], 4))
            ub = str(round(bounds[j][1], 4))
            model.write(lb + ' <= ' + rxnNames[j] + ' <= ' + ub + '\n')

        model.write('End')

    os.system('glpsol --cpxlp model.lp -o output.txt')

    solution = parse_output('output.txt', rxnNames)

    model.close()

    return solution


def write_constraint(constr_name, vec, rxnNames, model):
    line = constr_name + ': '
    started = False

    for i in range(len(vec)):
        if vec[i] == 0:
            continue

        if started is False:
            line += str(vec[i]) + ' ' + rxnNames[i] + ' '
            started = True
        else:
            if vec[i] > 0:
                line += '+ ' + str(vec[i]) + ' ' + rxnNames[i] + ' '
            elif vec[i] < 0:
                line += str(vec[i]) + ' ' + rxnNames[i] + ' '
        if len(line) > 220:  # max character in one line = 255. 220 selected for safety
            line += '\n'
            model.write(line)
            line = ''
    model.write(line + '= 0\n')


def parse_output(fileName, rxnNames):

    solutionStruct = namedtuple('solution', 'objective status x')

    with open(fileName, "r") as result:

        reactions = []
        fluxes = []
        for line in result.readlines():
            l = line.split()
            if 'obj' in l:
                objective = float(l[3])

            elif 'Status:' in l:
                status = l[1]

            elif len(l) > 3 and l[1] in rxnNames:
                reactions.append(l[1])
                fluxes.append(l[3])

        x = [reactions, fluxes]

        solution = solutionStruct(objective, status, x)

    result.close()
    return solution
