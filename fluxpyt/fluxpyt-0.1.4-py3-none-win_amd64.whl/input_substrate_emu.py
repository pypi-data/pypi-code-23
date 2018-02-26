# -*- coding: utf-8 -*-
"""
Created on Tue Aug  2 15:44:59 2016
Calculates substrate mids.
@author: Trunil
"""
from copy import deepcopy

def read_substrate_input(fileName):
    print('\n\n\nrunning read_substrate_input... ')
    file = open(fileName)
    labels = file.readline()  # reads first column only
    lines = file.readlines()  # f2 has list of different lines
    substrates = []; labeling = []; ratios = []

    for line in lines:
        line_split = line.split(',')
        substrates.append(line_split[0])
        lb = line_split[1]
        lb_split = lb.split()
        lb_split = [float(x) for x in lb_split]
        labeling.append(lb_split)

        ratios.append(line_split[2][0:-1] if line_split[2][0:-1] != '' else 1)

    ratios = [float(x) for x in ratios]
    file.close()
    substrate_info = sort_sub_input(substrates, labeling, ratios)
    print(substrate_info)

    return substrate_info

def sort_sub_input(substrates, labeling, ratios):
    from fluxpyt.utility import find

    substrate_info = [[], [], []]
    for sub in substrates:

        if sub not in substrate_info[0]:
            substrate_info[0].append(sub)
            ind = find(substrates, sub)
            mid_list = []
            ratio_list = []

            for i in ind:
                ratio_list.append(ratios[i])
                mid_list.append(labeling[i])
            substrate_info[1].append(mid_list)
            substrate_info[2].append(ratio_list)

    return substrate_info


def detect_substrate_emus(substrates, labeling):

    substrate_emus = []
    emu_len = []
    for i in range(len(substrates)):
        substrate = substrates[i]
        name = substrate + ':'
        pattern = labeling[i]
        emu_len.append(len(pattern))

        for j in range(len(pattern)):
            pat = pattern[j]
            if pat == '0.99':
                name += str(j + 1)
        substrate_emus.append(name)

    print('substrate emus are:')
    print(substrate_emus)
    return substrate_emus, emu_len

def list_network_subs_emus(elementary_rxn_list, substrates):
    print('\n\n\nnrunning list_network_subs_emus...')
    print(substrates)
    network_substrate_emus = []
    for rxn in elementary_rxn_list:
        rxn_split = rxn.split()
        rxn_split.remove('->')
        print(rxn_split)
        if len(rxn_split) > 4:
            rxn_split.remove('+')

        reactants = rxn_split[0:-1]
        for emu in reactants:
            r = emu.split(':')[0]
            if r in substrates:
                network_substrate_emus.append(emu)

    return network_substrate_emus


def genInSubEMU(substrate_info, network_substrate_emus):
    from scipy.signal import convolve
    print('\n\n\nrunning genInSubEMU')
    print(substrate_info)

    subs_mids = [[], []]
    for i in range(len(network_substrate_emus)):
        em = network_substrate_emus[i]
        EMUtoDo = em.split(':')[0]  # name of molecule
        EMUfrag = em.split(':')[1]  # e.g. 011, 111, 100 etc.

        print('EMUtoDo:', EMUtoDo)
        print(EMUfrag)

        # find selected substrate (EMUtoDo)
        for j in range(len(substrate_info[0])):  # iterate over substrates put in model
            if substrate_info[0][j] == EMUtoDo:
                break
        rowHit = j

        parts = list(EMUfrag)  # it [1,1,0] if emu = molecule:110
        parts = [int(x) for x in parts]

        fraction = substrate_info[2][rowHit]
        EMUout = [0] * (sum(parts) + 1)

        partsSub = []
        for p in range(len(parts)):
            if parts[p] == 1:
                partsSub.append(p + 1)
        parts = deepcopy(partsSub)

        listAAV = substrate_info[1][rowHit]

        for j in range(len(listAAV)):
            AAV = listAAV[j]
            a = [1]
            for k in range(len(parts)):

                b = [1 - AAV[parts[k] - 1], AAV[parts[k] - 1]]
                a = convolve(a, b)

            c = [x * fraction[j] for x in a]

            EMUout = [x + y for x, y in zip(EMUout, c)]
        subs_mids[0].append(em)

        subs_mids[1].append(EMUout)

    print('\n\n\n')
    for k in range(len(subs_mids[0])):
        print('\n\n\n', subs_mids[0][k], '\n', subs_mids[1][k])

    return subs_mids


def cal_substrate_mid(fileName, elementary_rxn_list):
    '''Calculates substrate mids.

    Note: Only 13C carbon mids can be calculated for now.

    Input:
		1. fileName: substrate input file name. (csv format file)
		2. elementary_rxn_list: list of elementary reactions.

    assumption:
        1. nat = [0.9893, 0.0107] ... naturnal carbon isotope abundance

        2. lab = [0.01,0.99]... labeled carbon abundance
    '''

    substrate_info = read_substrate_input(fileName)
    # list substrate emu in the network
    network_substrate_emus = list_network_subs_emus(elementary_rxn_list, substrate_info[0])
    subs_mids = genInSubEMU(substrate_info, network_substrate_emus)

    return subs_mids
