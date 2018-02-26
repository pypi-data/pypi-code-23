# -*- coding: utf-8 -*-
"""
Created on Wed Jul 12 11:35:14 2017

@author: Trunil
"""

from fluxpyt.utility import split_rxn
from copy import deepcopy
import sys

def make_networks(mol_rxnIDs, elementary_rxn_list, measured_emus, known_mids):

    print('\n\nmeasured emus: ',measured_emus)

    # sort measured mids in decreasing order of size.
    sz_m_list = []
    for m in measured_emus:
        atoms = m.split(':')[1]
        sz_m = sum([int(x) for x in atoms])
        sz_m_list.append([sz_m, m])
    mea2 = sorted(sz_m_list, reverse=True)
    mea1 = [x[1] for x in mea2]

    # make id,rxn tuple
    tuple_rxns = []
    for i in range(len(mol_rxnIDs)):
        tuple_rxns.append((mol_rxnIDs[i], elementary_rxn_list[i]))

    visited = []
    emu_rxn_networks = []
    emu_id_networks = []
    added_rx = []

    while mea1:
        mea = [mea1.pop(0)]
        emu_rxn_networks_1 = []
        emu_id_networks_1 = []

    #   mea = [measured_emus[1]]
        while mea:
            m_emu = mea.pop(0)
            que = [m_emu]

            net = []
            id_net = []
            new_mea = []
            while que:
                mol = que.pop(0)
                visited.append(mol)
                sz = sum([int(x) for x in mol.split(':')[1]])
                for i in range(len(tuple_rxns)):
                    tpl = tuple_rxns[i]
                    rxn_i = tpl[1]
                    id_i = tpl[0]
                    rxn_i_split = split_rxn(rxn_i)[1::2]

                    if rxn_i_split[-1] == mol:
                        reactant_i = rxn_i_split[0:-1]

                        if len(reactant_i) > 1 and tpl not in added_rx: #convolution
                            net.append(rxn_i)
                            id_net.append(id_i)
                            added_rx.append(tpl)
                            for rc in reactant_i:
                                new_mea.append(rc)
                        elif len(reactant_i) == 1 and tpl not in added_rx:
                            net.append(rxn_i)
                            id_net.append(id_i)
                            added_rx.append(tpl)
                            if reactant_i[0] not in visited:
                                que.append(reactant_i[0])

            emu_rxn_networks_1.append(net)
            emu_id_networks_1.append(id_net)

            for nmea in new_mea:
                mea.append(nmea)

            ###################################################################

            # delete empty networks
            id_net_tmp = []
            rxn_net_tmp = []

            for i in range(len(emu_id_networks_1)):
                if len(emu_id_networks_1[i]) != 0:
                    id_net_tmp.append(emu_id_networks_1[i])
                    rxn_net_tmp.append(emu_rxn_networks_1[i])

            emu_id_networks_1 = deepcopy(id_net_tmp)
            emu_rxn_networks_1 = deepcopy(rxn_net_tmp)

        #sort emu networks by size:
        s = []

        for i in range(len(emu_id_networks_1)):
            r = emu_rxn_networks_1[i][0] # select one reaction in a network
            em = r.split()[-1] # product
            atoms = list(em.split(':')[-1]) # emu numbers like 011,110,111, etc.
            sz = sum([int(x) for x in atoms])
            s.append([sz, emu_id_networks_1[i], emu_rxn_networks_1[i]])
        sorted_emu_networks = sorted(s)

        for k in range(len(sorted_emu_networks)):

            emu_id_networks.append(sorted_emu_networks[k][1])
            emu_rxn_networks.append(sorted_emu_networks[k][2])

    print(len(emu_rxn_networks), len(emu_id_networks))

#############################################################################
    #    delete networks wherein all mids would be unknown when it's turn comes

    known = deepcopy(known_mids)
    j = 0
    f = 0
    for j in range(len(emu_id_networks)):
        id_net = emu_id_networks[j]
        rxn_net = emu_rxn_networks[j]
        c = 0
        emu_list = []

        for rxn in rxn_net:
            rxn_split = split_rxn(rxn)[1::2]

            for emu in rxn_split:

                if emu in known:
                    c += 1
                else:
                    emu_list.append(emu)

        if c == 0:
            emu_id_networks[j], emu_id_networks[j+1] = emu_id_networks[j+1], emu_id_networks[j]
            emu_rxn_networks[j], emu_rxn_networks[j+1] = emu_rxn_networks[j+1], emu_rxn_networks[j]
            f += 1
            print('\nf:', f)
            emu_list = []

            if f > 1000:
                relocated_rxn_net = emu_rxn_networks.pop(j)
                relocated_id_net = emu_id_networks.pop(j)

                emu_id_networks.append(relocated_id_net)
                emu_rxn_networks.append(relocated_rxn_net)
                emu_list = []
                sys.exit()
            break
        else:

            for eml in emu_list:
                known.append(eml)

    print('******************')
    for n in emu_rxn_networks:
        print('\n\n',n)

# ######################################################################
    # delete empty networks
    id_net_tmp = []
    rxn_net_tmp = []
    for i in range(len(emu_id_networks)):
        if len(emu_id_networks[i]) != 0:
            id_net_tmp.append(emu_id_networks[i])
            rxn_net_tmp.append(emu_rxn_networks[i])

    emu_id_networks = deepcopy(id_net_tmp)
    emu_rxn_networks = deepcopy(rxn_net_tmp)

    # check if all measured mids can be calculated

    meas = len(measured_emus)
    added = []
    c = 0
    for net in emu_rxn_networks:
        for rxn in net:
            mols = split_rxn(rxn)[1::2]
            for ml in mols:
                if ml in measured_emus and ml not in added:
                    c += 1
                    added.append(ml)

    return emu_id_networks,emu_rxn_networks
