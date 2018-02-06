# generalized framework for learning NMFs based on GLMs

# uses the alternating least squares algorithm, except least squares is
# replaced by iteratively weighted least squares.

import numpy as np
from scipy import linalg, sparse

def irls(data, M, W, link, dlink, dist_var, max_iters=100):
    """
    Solves for W using IRLS

    Args:
        data: genes x cells
        M: genes x k
        W: k x cells
        link: function
        dlink: derivative of link function
        dist_var: variance function for the distribution

    Returns:
        W_new: updated W
    """
    pass
