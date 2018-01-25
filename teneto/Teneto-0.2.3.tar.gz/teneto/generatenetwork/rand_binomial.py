"""
generatenetwork.rand_binomial
"""

import numpy as np
from teneto.utils import graphlet2contact


def rand_binomial(size, prob, netrep='graphlet', nettype='bu', initialize='zero', netinfo=None):
    """

    Creates a random binary network following a binomial distribution.

    **PARAMETERS**

    :size: number of nodes and number of time points.

        :format: 2-tuple, list of size 2 or array of size 2. Can also be of length 3 (node x node x time) but number of nodes in 3-tuple must be identical.

    :prob: Probability of edge present. Two possibilities.

        :integer: the same probabability for each node becoming active (equal for all nodes).
        :tuple/list of size 2: different probabilities for edges to become active/inactive.

            The first value is "birth rate". The probability of an absent connection becoming present.

            The second value is the "death rate". This dictates the probability of an edge present remaining present.

            :example: (40,60) means there is a 40% chance that a 0 will become a 1 and a 60% chance that a 1 stays a 1.

    :netrep: network representation: 'graphlet' or 'contact'.
    :nettype: string 'bu' or 'bd' (accepts 'u' and 'd' as well as b is implicit)
    :initialize: optional variable for option2 of prob. Follwoing options:

        :'zero': all nodes start deactivated
        :integer: states percentage of nodes that should active when t=1 (determined randomly).
    :netinfo: dictionary for contact representaiton information


    **OUTPUT**

    :net: generated network.

        :format: either graphlet (numpy) or contact (dictionary), depending on netrep input.

    **NOTES**

    Option 2 of the "prob" parameter can be used to create a small autocorrelaiton or make sure that, once an edge has been present, it never disapears.

    **SEE ALSO**

    **READ MORE**
    There is some work on the properties on the graphs with birth/death rates (called edge-Markovian Dynamic graphs) as described here. Clementi et al (2008) Flooding Time in edge-Markovian Dynamic Graphs *PODC*

    **HISTORY**

    :Created: Dec 16, WHT

    """

    size = np.atleast_1d(size)
    prob = np.atleast_1d(prob)
    if len(size) == 2 or (len(size) == 3 and size[0] == size[1]):
        pass
    else:
        raise ValueError('size input should be [numberOfNodes,Time]')
    if len(prob) > 2:
        raise ValueError('input: prob must be of len 1 or len 2')
    if prob.min() < 0 or prob.max() > 1:
        raise ValueError('input: prob should be probability between 0 and 1')
    if nettype[-1] == 'u' or nettype[-1] == 'd':
        pass
    else:
        raise ValueError('nettype must be u or d')

    network_size = size[0]
    nr_time_points = size[-1]
    connmat = network_size * network_size
    if len(prob) == 1:
        net = np.random.binomial(1, prob, connmat * nr_time_points)
        net = net.reshape(network_size * network_size, nr_time_points)
    if len(prob) == 2:
        net = np.zeros([connmat, nr_time_points])
        if initialize == 'zero':
            pass
        else:
            edgesat0 = np.random.randint(
                0, connmat, int(np.round(initialize * (connmat))))
            net[edgesat0, 0] = 1
        for t_ind in range(0, nr_time_points - 1):
            edges_off = np.where(net[:, t_ind] == 0)[0]
            edges_on = np.where(net[:, t_ind] == 1)[0]
            update_edges_on = np.random.binomial(1, prob[0], len(edges_off))
            update_edge_off = np.random.binomial(1, prob[1], len(edges_on))
            net[edges_off, t_ind + 1] = update_edges_on
            net[edges_on, t_ind + 1] = update_edge_off
    # Set diagonal to 0
    net[np.arange(0, network_size * network_size, network_size + 1), :] = 0
    # Reshape to graphlet
    net = net.reshape([network_size, network_size, nr_time_points])
    # only keep upper left if nettype = u
    # Note this could be made more efficient by only doing (network_size*network_size/2-network_size) nodes
    # in connmat and inserted directly into upper triangular.
    if nettype[-1] == 'u':
        unet = np.zeros(net.shape)
        ind = np.triu_indices(network_size)
        unet[ind[0], ind[1], :] = np.array(net[ind[0], ind[1], :])
        unet = unet + np.transpose(unet, [1, 0, 2])
        net = unet
    if netrep == 'contact':
        if not netinfo:
            netinfo = {}
        netinfo['nettype'] = 'b' + nettype[-1]
        net = graphlet2contact(net, netinfo)
    return net
