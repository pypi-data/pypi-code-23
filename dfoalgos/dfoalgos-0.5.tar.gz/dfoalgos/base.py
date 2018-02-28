"""
Basic infrastructure for DFO methods.
"""

import math


INFINITY = float("inf")


def create_standard_basis(dimension, scale_factor=1.0):
    """Create an orthogonal, maximal, positive basis."""
    assert dimension >= 1
    assert scale_factor > 0.0
    pattern = []
    for i in range(dimension):
        for offset in (scale_factor, -scale_factor):
            vector = [0.0] * dimension
            vector[i] = offset
            pattern.append(vector)
    return pattern



def create_std_basis_simplex(position, size_param=1.0):
    """Create a simplex based on the standard basis of Euclidean space.

    Parameters
    ----------
    position : iterable
        The position being used as location vector for the simplex. In this
        construction, `position` is the vertex in the simplex closest to
        the origin.
    size_param : float, optional
        The length of the basis vectors.

    Returns
    -------
    simplex : list of list
        A list containing ``len(position) + 1`` points.

    """
    assert len(position) > 0
    assert size_param > 0.0
    simplex = [list(position)]
    for i in range(len(position)):
        point = list(position)
        point[i] += size_param
        simplex.append(point)
    return simplex



def create_han_simplex(position, size_param=None):
    """Create a simplex by the method of Lixing Han.

    The resulting simplex is tilted and regular.

    Parameters
    ----------
    position : iterable
        The position being used as location vector for the simplex. In this
        construction, `position` is not a vertex in the simplex.
    size_param : float, optional
        1/sqrt(2) * side length for all edges of the simplex.

    Returns
    -------
    simplex : list of list
        A list containing ``len(position) + 1`` points.

    """
    dim = len(position)
    assert size_param is None or size_param > 0.0
    assert dim > 0
    simplex = []
    if size_param is None:
        size_param = min(max(max(abs(x) for x in position), 1.0), 10.0)
    # construct the initial simplex
    for i in range(dim):
        point = list(position)
        point[i] += size_param
        simplex.append(point)
    point = list(position)
    dim_factor = (1.0 - math.sqrt(dim + 1)) / dim
    for i in range(dim):
        point[i] += size_param * dim_factor
    simplex.append(point)
    return simplex



def create_upright_regular_simplex(position, size_param=1.0):
    """Create a regular simplex.

    This simplex is a regular pyramid standing on its base. The base is a
    (n - 1)-dimensional regular simplex. The last dimension is only sampled
    at two values. The apex is above the centroid of the base.

    Parameters
    ----------
    position : iterable
        The position being used as location vector for the simplex. In this
        construction, `position` is the centroid of the simplex.
    size_param : float, optional
        The side length of all edges of the simplex.

    Returns
    -------
    simplex : list of list
        A list containing ``len(position) + 1`` points.

    """
    dim = len(position)
    assert dim > 0
    assert size_param > 0.0
    sqrt = math.sqrt
    # assume some distance between vertices
    distance = 1.0
    dist_squared = distance ** 2
    # begin with simplex in one dimension
    simplex = [[-0.5 * distance], [0.5 * distance]]
    current_dim = 1
    while current_dim < dim:
        center = center_of_mass(simplex)
        diff_vector = [center[i] - simplex[0][i] for i in range(current_dim)]
        dist_squared_center_to_corner = math.fsum(x * x for x in diff_vector)
        pyramid_height = sqrt(dist_squared - dist_squared_center_to_corner)
        for vector in simplex:
            vector.append(0.0)
        center.append(pyramid_height)
        simplex.append(center)
        current_dim += 1
    final_center = center_of_mass(simplex)
    simplex = scale(simplex, final_center, size_param)
    # shift to final offset vector
    for vector in simplex:
        for i in range(dim):
            vector[i] -= final_center[i]
            vector[i] += position[i]
    return simplex



def create_tilted_regular_simplex(position, size_param=None):
    """Create a simplex by the method of Ravi Varadhan.

    This construction method was originally proposed by [Spendley1962]_.
    The scaling heuristic is taken from the function :func:`nmk` in the
    R package dfoptim (see `<https://cran.r-project.org/package=dfoptim>`_).
    The resulting simplex is regular and `position` becomes the "lower
    left" corner of the simplex.

    Parameters
    ----------
    position : iterable
        The position being used as location vector for the simplex. In this
        construction, `position` is the vertex in the simplex closest to
        the origin.
    size_param : float, optional
        The side length of all edges of the simplex.

    Returns
    -------
    simplex : list of list
        A list containing ``len(position) + 1`` points.

    """
    dim = len(position)
    assert dim > 0
    assert size_param is None or size_param > 0.0
    simplex = [list(position)]
    if size_param is None:
        size_param = max(1.0, math.sqrt(math.fsum(x ** 2 for x in position)))
    alpha1 = size_param / (dim * math.sqrt(2)) * (math.sqrt(dim + 1) + dim - 1)
    alpha2 = size_param / (dim * math.sqrt(2)) * (math.sqrt(dim + 1) - 1)
    for i in range(dim):
        point = list(position)
        for j in range(dim):
            point[j] += alpha2
        point[i] = position[i] + alpha1
        simplex.append(point)
    return simplex



def create_pfeffer_simplex(position, size_param=0.05):
    """Create a simplex according to the rule of Lawrence E. Pfeffer.

    This construction method is the default in Matlab's :func:`fminsearch`
    and SciPy's :func:`scipy.optimize.fmin`. According to [Fan2002]_, p. 73,
    this approach was proposed by Lawrence E. Pfeffer at Stanford.

    Parameters
    ----------
    position : iterable
        The position being used as location vector for the simplex. In this
        construction, `position` is the vertex in the simplex closest to
        the origin.
    size_param : float, optional
        For each coordinate, a fraction of itself is added to it. This value
        is the fraction.

    Returns
    -------
    simplex : list of list
        A list containing ``len(position) + 1`` points.

    References
    ----------
    .. [Fan2002] Ellen Fan (2002). Global optimization of Lennard-Jones
        atomic clusters. Master's thesis, McMaster University.
        http://www.cas.mcmaster.ca/~oplab/thesis/faneMS.pdf

    """
    assert len(position) > 0
    assert size_param > 0.0
    nonzero_delta = size_param
    zero_delta = 0.00025
    simplex = [list(position)]
    for i in range(len(position)):
        point = list(position)
        if point[i] != 0.0:
            point[i] *= (1.0 + nonzero_delta)
        else:
            point[i] = zero_delta
        simplex.append(point)
    return simplex



def create_nash_simplex(position, size_param=0.1):
    """Create a simplex according to the rule of John C. Nash.

    This construction method is described in [Nash1990]_, pp. 168-178. It
    is also the default in the Nelder-Mead implementation of the statistical
    programming language R, which can be called through the function
    :func:`optim` of the R standard library.

    Parameters
    ----------
    position : iterable
        The position being used as location vector for the simplex. In this
        construction, `position` is the vertex in the simplex closest to
        the origin.
    size_param : float, optional
        For each coordinate, a fraction of the maximal absolute value in
        `position` is added to it. This value is the fraction.

    Returns
    -------
    simplex : list of list
        A list containing ``len(position) + 1`` points.

    References
    ----------
    .. [Nash1990] John C. Nash (1990). Compact Numerical Methods for
        Computers: Linear Algebra and Function Minimisation, second edition,
        Taylor & Francis.

    """
    assert len(position) > 0
    assert size_param > 0.0
    max_abs = max(abs(p) for p in position)
    if max_abs == 0.0:
        max_abs = 1.0
    simplex = [list(position)]
    for i in range(len(position)):
        point = list(position)
        point[i] += size_param * max_abs
        simplex.append(point)
    return simplex



def displace(point1, point2, factor):
    """Displace `point1` by ``factor * (point1 - point2)``.

    Parameters
    ----------
    point1 : iterable
        The position vector.
    point2 : iterable
        The second vector necessary to calculate the displacement vector.
    factor : float
        The scale factor.

    Returns
    -------
    new_point : list
        The displaced point.

    """
    dim = len(point1)
    new_point = [None] * dim
    coeff1 = 1.0 + factor
    for i in range(dim):
        new_point[i] = coeff1 * point1[i] - factor * point2[i]
    return new_point



def reflect(points, fixed_point):
    """Reflect points across a fixed point."""
    reflected_points = []
    for point in points:
        new_point = [2.0 * f - p for p, f in zip(point, fixed_point)]
        reflected_points.append(new_point)
    return reflected_points



def translate(points, vector):
    """Translate points by given vector."""
    translated_points = []
    for point in points:
        new_point = [p + v for p, v in zip(point, vector)]
        translated_points.append(new_point)
    return translated_points



def center_of_mass(points):
    """Calculate the center of mass of the given points."""
    # shortcuts
    fsum = math.fsum
    num_points = len(points)
    dim = len(points[0])
    center = [0.0] * dim
    for i in range(dim):
        center[i] = fsum(point[i] for point in points)
        center[i] /= num_points
    return center



def scale(points, fixed_point, factor):
    """Scale a point cloud by a given factor.

    Parameters
    ----------
    points : iterable of iterable
        The points to scale.
    fixed_point : iterable
        The fixed point of the transformation.
    factor : float
        The scale factor.

    Returns
    -------
    scaled_points : list of list
        List containing scaled points.

    """
    scaled_points = []
    for point in points:
        new_point = displace(point, fixed_point, -1.0 + factor)
        scaled_points.append(new_point)
    return scaled_points



def lexicographic_sort_key(individual):
    """Sort key for lexicographic sorting with special treatment of None.

    None is replaced with infinity (the worst possible value).

    """
    try:
        key = []
        for objective in individual.objective_values:
            if objective is None:
                objective = INFINITY
            key.append(objective)
    except TypeError:
        key = individual.objective_values
        if key is None:
            key = INFINITY
    return key



class Observable(object):
    """Part of the Observer/Observable design pattern."""

    def __init__(self):
        self.observers = []


    def attach(self, observer):
        """Add observer to the list of observers.

        Parameters
        ----------
        observer : callable
            The object to be informed about changes.

        """
        if observer not in self.observers:
            self.observers.append(observer)


    def detach(self, observer):
        """Remove observer from the list of observers.

        Parameters
        ----------
        observer : callable
            The object to be informed about changes.

        """
        try:
            self.observers.remove(observer)
        except ValueError:
            pass


    def notify_observers(self):
        """Inform the observers about a potential state change."""
        for observer in self.observers:
            observer(self)



class OptimizeResult(dict):
    """ Represents the optimization result.

    Attributes
    ----------
    x : ndarray
        The solution of the optimization.
    success : bool
        Whether or not the optimizer exited successfully.
    status : int
        Termination status of the optimizer. Its value depends on the
        underlying solver. Refer to `message` for details.
    message : str
        Description of the cause of the termination.
    fun, jac, hess: ndarray
        Values of objective function, its Jacobian and its Hessian (if
        available). The Hessians may be approximations, see the documentation
        of the function in question.
    hess_inv : object
        Inverse of the objective function's Hessian; may be an approximation.
        Not available for all solvers. The type of this attribute may be
        either np.ndarray or scipy.sparse.linalg.LinearOperator.
    nfev, njev, nhev : int
        Number of evaluations of the objective functions and of its
        Jacobian and Hessian.
    nit : int
        Number of iterations performed by the optimizer.
    maxcv : float
        The maximum constraint violation.

    Notes
    -----
    There may be additional attributes not listed above depending of the
    specific solver. Since this class is essentially a subclass of dict
    with attribute accessors, one can see which attributes are available
    using the `keys()` method.
    
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)


    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


    def __repr__(self):
        if self.keys():
            m = max(map(len, list(self.keys()))) + 1
            return '\n'.join([k.rjust(m) + ': ' + repr(v)
                              for k, v in sorted(self.items())])
        else:
            return self.__class__.__name__ + "()"


    def __dir__(self):
        return list(self.keys())



def order(values, sort_key=None):
    """Return the ordering of the elements of `values`.

    The list ``[values[j] for j in order(values)]`` is a sorted version of
    `values`.

    Adapted from
    https://code.activestate.com/recipes/491268-ordering-and-ranking-for-lists/

    Parameters
    ----------
    values : list
        The list to process
    sort_key : callable, optional
        A callable to determine the ordering. Default sort key is
        ``(value is None, value)``.

    Returns
    -------
    order : list
        The indices the values would have in a sorted list.

    """
    def default_sort_key(argument):
        return argument is None, argument

    if sort_key is None:
        sort_key = default_sort_key
    decorated = [(sort_key(value), i) for i, value in enumerate(values)]
    decorated.sort()
    indices = [index for _, index in decorated]
    return indices



def rank(values, sort_key=None, ties="average"):
    """Return the ranking of the elements of `values`.

    The best obtainable rank is 1. Calls the function :func:`order`.

    Adapted from
    https://code.activestate.com/recipes/491268-ordering-and-ranking-for-lists/

    Parameters
    ----------
    values : list
        The list to process
    sort_key : callable, optional
        A callable to determine the ordering. Default sort key is
        ``(value is None, value)``.
    ties : string
        The tie-breaking criterion. Choices are: "first", "average", "min",
        and "max".

    Returns
    -------
    ranks : list
        The ranks of the values in the same order.

    """
    def default_sort_key(argument):
        return argument is None, argument

    if sort_key is None:
        sort_key = default_sort_key
    ordered_indices = order(values, sort_key)
    ranks = ordered_indices[:]
    num_values = len(ordered_indices)
    for i in range(num_values):
        ranks[ordered_indices[i]] = i + 1
    if ties == "first":
        return ranks
    elif ties not in ["first", "average", "min", "max"]:
        raise Exception("unknown tie breaking")

    prev_key = sort_key(values[ordered_indices[0]])
    blocks = [[]]
    for i in range(num_values):
        curr_key = sort_key(values[ordered_indices[i]])
        if curr_key != prev_key:
            blocks.append([])
        blocks[-1].append(i + 1)
        prev_key = curr_key

    for i, block in enumerate(blocks):
        if len(block) == 1:
            continue
        if ties == "average":
            value = sum(block) / float(len(block))
        elif ties == "min":
            value = min(block)
        elif ties == "max":
            value = max(block)
        for j in block:
            ranks[ordered_indices[j - 1]] = value
    return ranks
