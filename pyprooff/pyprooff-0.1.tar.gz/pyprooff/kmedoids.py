import numpy as np
import random

def kMedoids(distance_matrix, k, tmax=100):
    """Clusters items according to a distance matrix

    Args:
        distance matrix: a 2-D iterable (numpy array or list of lists)
        k = number of clusters
        tmax = not sure, presumably maximum number of iterations

    Returns: tuple of:
        - array of cluster 'names', the indices of distance_matrix members
          closest to the center of the cluster
        - dict of arrays of cluster indices from distance_matrix
          note that the keys of the dict are serial, corresponding to the
          index of the cluster names, not their values

    Note: pyprooff.similar.pairwise_distance_matrix is a good adjunct to this if
          you want to use arbitrary distance functions. Otherwise scipy (euclidean, etc.) or
          sklearn (cosine distance) are best.
    """
    # determine dimensions of distance matrix D
    D = distance_matrix  # legacy variable name
    m, n = D.shape

    # randomly initialize an array of k medoid indices
    M = np.sort(np.random.choice(n, k))

    # create a copy of the array of medoid indices
    Mnew = np.copy(M)

    # initialize a dictionary to represent clusters
    C = {}
    for t in range(tmax):
        # determine clusters, i. e. arrays of data indices
        J = np.argmin(D[:,M], axis=1)
        for kappa in range(k):
            C[kappa] = np.where(J==kappa)[0]
        # update cluster medoids
        for kappa in range(k):
            J = np.mean(D[np.ix_(C[kappa],C[kappa])],axis=1)
            j = np.argmin(J)
            Mnew[kappa] = C[kappa][j]
        np.sort(Mnew)
        # check for convergence
        if np.array_equal(M, Mnew):
            break
        M = np.copy(Mnew)
    else:
        # final update of cluster memberships
        J = np.argmin(D[:,M], axis=1)
        for kappa in range(k):
            C[kappa] = np.where(J==kappa)[0]

    # return results
    return M, C