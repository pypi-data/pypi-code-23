import numpy as np

def length(data):
    """
    Method for calculating the length of a given curve by the vertices

    Parameters
    ----------
    data: numpy array
        Numpy array of the vertices of shape (N,2)

    Returns
    -------
    length: int
        Length of the distance vectors added up

    """
    da = np.array(data)
    le = np.zeros_like(da)
    le = data-np.roll(data,-1,axis=0)
    return np.sum(np.sqrt(np.sum(le**2,axis=1)))

def center_mass(data):
    """
    Method for calculating the center of mass (CM)

    Parameters
    ----------
    data: numpy array
        Numpy array of the vertices of shape (N,2)

    Returns
    -------
    cm: touple
        Touple of coordinates of the CM
    """
    n,_ = data.shape
    cm = np.sum(data,axis=0)/np.float(n)
    return cm

def bounding_box(data,scale=1./4.):
    """
    Calculation of the diameter of the bounding box.

    The bounding box is the box that fits the entire curve.
    It does not need to be a square, which is accounted for in both directions.
    The resulting diameter is scaled by a factor and returned.

    Parameters
    ----------
    data: numpy array
        Vertices from which the diameter is calculated. Shape is (n,2)
    scale: double, optional
       Factor by which the diameter is scaled. Default is 1/4. 

    Returns
    -------
    double
        Diameter of the bounding box.
    """
    xmax = np.max(data[:,0])
    xmin = np.min(data[:,0])
    ymax = np.max(data[:,1])
    ymin = np.min(data[:,1])
    return ((xmax-xmin)+(ymax-ymin))/2.*scale
