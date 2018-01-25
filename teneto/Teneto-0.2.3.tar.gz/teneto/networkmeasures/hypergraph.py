
import numpy as np
import scipy.stats as sps
import teneto
from teneto.misc import corrcoef_matrix, correct_pvalues_for_multiple_testing
def hypergraph(netIn,threshold='yes',alpha=0.05):

    """
    Currently under construction

    If binary, jaccard index is used. Gives probabalistic interpretation and all edges are kept.

    If weighted, pearson correlation coeeficienty is used.

    If threshold = yes (weighted only). 'Benjamini-Hochberg' FDR procedure is used

    Only unidrirected networks

    alpha = 0.05 (FDR corrected threshold)

    **NOTE**
    Tenetos

    **HISTORY**

    Created. Jan17, WHT

    **READ MORE**
    - Bassett, D. S., Wymbs, N. F., Porter, M. A., Mucha, P. J., & Grafton, S. T. (2013). Cross-Linked Structure of Network Evolution. http://doi.org/10.1063/1.4858457
    - Davison, E. N., Schlesinger, K. J., Bassett, D. S., Lynall, M.-E., Miller, M. B., Grafton, S. T., & Carlson, J. M. (2015). Brain Network Adaptability across Task States. PLoS Computational Biology, 11(1). http://doi.org/10.1371/journal.pcbi.1004029


    """

    G,netInfo = teneto.utils.process_input(netIn,['C','G','TO'])
    #Get input type (C, G, TO)


    ind=np.triu_indices(G.shape[0],k=1)
    G[ind[0],ind[1],:]
    eoi=G[ind[0],ind[1],:]
    newNodeN = int((netInfo['netshape'][0]*netInfo['netshape'][1]-netInfo['netshape'][0])/2)

    #Xut = [upper trianglular of the $\Xi{i,j}$=R(i,j), i, j]
    if netInfo['nettype'][0] == 'b':
        nettypeHypergraph = 'bh'
        Xut=[]
        for a in range(0,eoi.shape[0]):
            for b in range(0,eoi.shape[0]):
                if a<b:
                    JI=np.sum(eoi[a,:]+eoi[b,:]==2)/(np.sum(eoi[a,:]==1)+np.sum(eoi[b,:]==1)-np.sum(eoi[a,:]+eoi[b,:]==2))
                    Xut.append([JI,a,b])
        Xut = np.array(Xut)

    elif netInfo['nettype'][0] == 'w':

        nettypeHypergraph = 'wh'
        X = corrcoef_matrix(eoi)
        xind=np.triu_indices(X[0].shape[0],k=1)

        Xut = np.array([X[0][xind[0],xind[1]],xind[0],xind[1]]).transpose()
        p_Xut = X[1][xind[0],xind[1]]

        if threshold == 'yes':
            p_Xut_fdr = correct_pvalues_for_multiple_testing(p_Xut)
            Xut=np.delete(Xut,np.where(p_Xut_fdr>alpha),axis=0)


    coev={}
    coev['dimord'] = 'node,node'
    coev['valLab'] = 'coevolution'
    coev['netshape'] = (newNodeN,newNodeN)
    coev['nettype'] = nettypeHypergraph
    coev['contacts'] = Xut[:,1:].astype(int)
    coev['values'] = Xut[:,0]
    coev['nLabs'] = list(zip(*ind))

    #Note some parts of the commnity detection still need to be improved.
    X=np.zeros(coev['netshape'])
    X[coev['contacts'][:,0],coev['contacts'][:,1]]=coev['values']
    hyperedgeclusters=teneto.communitydetection.static.traag_bruggeman(X)
    print(hyperedgeclusters)
    he = np.empty(len(set(hyperedgeclusters)))
    for i,n in enumerate(set(hyperedgeclusters)):
        he[i]=np.array(coev['nLabs'])
    coev['hyperedges']=he
    return coev
