import teneto
import scipy as sp
import numpy as np

def louvain(G,randomseed=None):

    """

    Louvain clustering algorithm (static networks).

    Louvain clustering works in 2 phases.
    In phase 1 it attempts to move nodes into each of its neighbours and finding which reshuffle create improvement in modularity.
    The order of which nodes are shuffled is random. This is done until no improvement in modularity is found.
    In phase 2, a new network is created where each community is a node. The internal strength of a community is the diagonal.
    The two phases are repeated until there is no improvement in modularity.

    **INPUT**

        :G: 2-D Connectivity Matrix (numpy array or scipy sparse (csr) format). G should be positively weighted and binary matrices. If negative weights included, multi-layer clustering is better.
        :randomseed: Specify random seed for reproduceability

    **OUTPUT**

    C - vetctor of assignments

    **NOTE**

    Due to the randomness of the Inititialization, it is recommended to run the clustering algorithm multiple times.

    **HISTORY**

    :created: April 2017, wht

    **READ MORE**

    Blondel, V. D., Guillaume, J.-L., Lambiotte, R., & Lefebvre, E. (2008). Fast unfolding of communities in large networks. Journal of Statistical Mechanics: Theory and Experiment, 10008(10), 6. https://doi.org/10.1088/1742-5468/2008/10/P10008

    """

    #Inititialization
    np.random.seed(randomseed)
    C = teneto.communitydetection._louvain_phase1(G)
    Cnew = np.array(C)
    # If Cnew is not improved phase1 returns 'optimized', ending the while loop.
    while isinstance(Cnew,list):
        Gnew = teneto.communitydetection._louvain_phase2(Cnew)
        Cnew,C = teneto.communitydetection._louvain_phase1(Gnew,C)
    return C

def _louvain_phase2(C):
    Gnew = np.array([np.sum(G[C==i,:][:,C==j]) for i in np.unique(C) for j in np.unique(C)])
    Gnew=Gnew.reshape([int(np.sqrt(len(Gnew))),int(np.sqrt(len(Gnew)))])
    diagonalindex = np.arange(Gnew.shape[0])
    Gnew[diagonalindex,diagonalindex]=Gnew[diagonalindex,diagonalindex]/2
    Gnew=sp.sparse.csr_matrix(Gnew)
    return Gnew


def _louvain_phase1(G,Ckeep=[]):

    # Ckeep is the original the cluster assignment from previous iterations. As G is reduced in size in Phase 2, Ckeep, is a map to keep

    #Phase 1
    N = G.shape[0]
    C = np.arange(0,N)
    diagonal = G.diagonal()

    # Set diagonal (if )
    if isinstance(G,np.ndarray):
        np.fill_diagonal(G,0)
    elif sp.sparse.isspmatrix_csr(G):
        G.setdiag(0)
    else:
        raise ValueError('incompatible matrix format. Must be numpy array of sparse csr_matrix')

    m = G.sum()/2
    stopcondition = 0
    history=[]
    while stopcondition == 0:
        order=np.random.permutation(np.arange(0,N))
        Cold = np.array(C)
        for i in order:
            if isinstance(G,np.ndarray):
                Gi = G[i,:]
            elif sp.sparse.isspmatrix_csr(G):
                Gi = G[i,:].toarray().squeeze()
            fid=np.where(Gi>0)
            C_neighbours = np.unique(C[fid])
            if len(C_neighbours)>0:
                k_i = Gi.sum()

                Cnew = np.array(C)

                deltaQ = np.zeros(len(C_neighbours))
                for ci,C_try in enumerate(C_neighbours):

                    Cnew[i]=C_try
                    #Within cluster degree of node i
                    k_i_in = np.sum(Gi[Cnew==C_try])+diagonal[i]
                    if isinstance(G,np.ndarray):
                        #Within cluster degree
                        k_C_in = np.sum(G[Cnew==C_try,:][:,Cnew==C_try])/2+np.sum(diagonal[Cnew==C_try])
                        #Cluster degree - within cluster degree
                        k_C_all = np.sum(G[Cnew==C_try,:])-k_C_in+np.sum(diagonal[Cnew==C_try]) # Due to double links of the square
                    elif sp.sparse.isspmatrix_csr(G):
                        #Within cluster degree
                        k_C_in = np.sum(G[Cnew==C_try,:][:,Cnew==C_try].toarray())/2+np.sum(diagonal[Cnew==C_try])
                        #Cluster degree - within cluster degree
                        k_C_all = np.sum(G[Cnew==C_try,:].toarray())-k_C_in+np.sum(diagonal[Cnew==C_try]) # Due to double links of the square
                    #Calculate deltaQ
                    deltaQ[ci] = (((k_C_in+2*k_i_in)/(2*m))-np.power((k_C_all+k_i,)/(2*m),2))-((k_C_in/(2*m))-(np.power(k_C_all/(2*m),2))-(np.power(k_i/(2*m),2)))
                if np.max(deltaQ)>0 and C[i] != C_neighbours[np.argmax(deltaQ)]:

                    history.append([C[i],C_neighbours[np.argmax(deltaQ)]])
                    C[i]=C_neighbours[np.argmax(deltaQ)]

        if list(C) == list(Cold):
            stopcondition = 1
    if list(Ckeep) != []:
        if history == []:
            return 'optimized',Ckeep
        else:
            Ckeep[Ckeep==history[0][0]]=history[0][1]
            Ckeep=teneto.utils.clean_community_indexes(Ckeep)
            C=teneto.utils.clean_community_indexes(C)
            return C,Ckeep
    else:
        C=teneto.utils.clean_community_indexes(C)
        return C
