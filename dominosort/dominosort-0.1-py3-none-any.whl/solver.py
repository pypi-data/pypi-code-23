from collections import deque
import itertools as it
import warnings

import numpy as np
import scipy.optimize as optimize
from scipy.sparse import csgraph

from .utils import alias


class Solver:
    @classmethod
    def loss(cls, items, metric):
        """
        Compute the loss that corresponds to a given order of items.
        (For details about parameters see `Solver.sort`.)
        
        Parameters
        ----------
        items : sequence of 2-sequences
        metric : dominosort.metrics.Metric
        
        See Also
        --------
        Solver.sort : For details about parameters.
        """
        return sum(metric.eval(x[1], y[0]) for x, y in zip(items[:-1], items[1:]))

    @classmethod
    def sort(cls, items, metric, verbose=False, **kwargs):
        """
        Sort `items` with respect to `metric` such that the result has minimal loss according to
        `Solver.loss`.
        
        Parameters
        ----------
        items : sequence of 2-sequences
            The sequence to be sorted. Each item must be represented by two values
            (``item[0], item[1]``) which in turn must be compatible with the given metric.
            E.g.: ``[(0.1, 0.3), (0.2, 0.6), (0.4, 0.5), ...]``.
        metric : dominosort.metrics.Metric
            The metric to be used for computing differences between items' heads and tails.
            ``difference = metric(x[1], y[0])`` for two items `x`, `y`.
        verbose : bool, default=True
        **kwargs
            Additional arguments for the `scipy.optimize.linprog` solver. Those arguments are
            passed as the ``options`` keyword argument.
            
        Returns
        -------
        sorted : list
            The sorted items.
            
        Raises
        ------
        UserWarning
            Issues a warning via `warnings.warn` if no optimal sort order could be determined.
            This can be the case if for example the number of iterations for the underlying
            solver is too small. The warning contains as a message the most recent message
            from the solver. In this case the given `items` are returned.
        """
        raise NotImplementedError


# noinspection PyTypeChecker
@alias('BnB')
class BranchAndBound(Solver):
    """
    This solver combines the branch and bound method with the simplex algorithm.
    
    A particular order of items is represented by the links amongst these items. "A links to B"
    means that B follows A in the resulting order. The simplex algorithm is used to determine the
    links while branch and bound is used to impose the integer condition on the links' values.
    `scipy.optimize.linprog` is used for the simplex algorithm.
    """

    class Conditions:
        """
        Represents the conditions for the simplex algorithm (`scipy.optimize.linprog`).
        """

        def __init__(self, N):
            """
            Parameters
            ----------
            N : int
                The number of items to be sorted.
            """
            self.N = N
            self.A_eq = None
            self.b_eq = None
            self.A_ub = None
            self.b_ub = None
            self.bounds = (0, 1)

        def __and__(self, other):
            """
            Impose two sets of conditions simultaneously.
            
            Parameters
            ----------
            other : Conditions
            
            Returns
            -------
            both : Conditions
                Representing the conditions in both `self` and `other`.
            """
            new = type(self)(self.N)
            if self.A_eq is not None or other.A_eq is not None:
                new.A_eq = np.concatenate([x for x in (self.A_eq, other.A_eq) if x is not None])
            if self.b_eq is not None or other.b_eq is not None:
                new.b_eq = np.concatenate([x for x in (self.b_eq, other.b_eq) if x is not None])
            if self.A_ub is not None or other.A_ub is not None:
                new.A_ub = np.concatenate([x for x in (self.A_ub, other.A_ub) if x is not None])
            if self.b_ub is not None or other.b_ub is not None:
                new.b_ub = np.concatenate([x for x in (self.b_ub, other.b_ub) if x is not None])
            return new

        def __type_hinting__(self, A_eq: np.ndarray, b_eq: np.ndarray, A_ub: np.ndarray,
                             b_ub: np.ndarray):
            self.A_eq = A_eq
            self.b_eq = b_eq
            self.A_ub = A_ub
            self.b_ub = b_ub

        def ban_cycle(self, path):
            """
            Add a condition that bans a specific cycle.
            
            The simplex algorithm might come up with solutions that contain cycles amongst the
            items, while the final solution should be a sequence of items (no cycle). For that
            reason, whenever a cycle occurs, it has to be banned "on-line".
            
            Parameters
            ----------
            path : tuple[tuple], list[tuple]
                The 2d-indices of links that are part of the cycle.
                E.g.: ``[(0, 1), (1, 2), (2, 0)]`` denotes the cycle ``0 -> 1 -> 2 -> 0``.
                
            Returns
            -------
            None
                The condition is appended in-place.
            """
            A_ub_cycle = np.zeros((1, self.N ** 2), dtype=int)
            for index in it.product(path, repeat=2):
                A_ub_cycle[0, index[0] * self.N + index[1]] = 1
            b_ub_cycle = np.asarray([len(path) - 1])
            self.A_ub = np.concatenate((self.A_ub, A_ub_cycle), axis=0)
            self.b_ub = np.concatenate((self.b_ub, b_ub_cycle), axis=0)

        @classmethod
        def general(cls, N):
            """
            Generate the general conditions for the simplex algorithm.
            
            This involves the following constraints:
            
                * Exactly `N-1` links in the resulting solution.
                * No item can be connected to itself.
                * Each item can connect to at most one other item.
                * Each items can be connected to at most one other item.
                
            These correspond to a sequential solution such as ``1 -> 3 -> 2 -> 0`` for example.
            The integer-links conditions are applied on-line via branch and bound
            (see `Condition.branch`).
            
            Parameters
            ----------
            N : int
                The number of items to be sorted.
                
            Returns
            -------
            conditions : Conditions
            
            See Also
            --------
            Conditions.branch : Integer conditions applied on-line via branch and bound.
            """
            A_eq = np.concatenate((
                # Exactly N-1 connections.
                np.ones(N ** 2, dtype=int)[None, :],
                # No item can be connected to itself.
                np.diag([1] * N).flatten()[None, :]
            ), axis=0)
            b_eq = np.asarray([N - 1, 0], dtype=int)

            # Each item can connect to at most one other item (rows).
            A_ub_1 = np.zeros((N, N ** 2), dtype=int)
            for j in range(N):
                A_ub_1[j, j * N:j * N + N] = 1

            # Each item can be connected to at most one other item (columns).
            A_ub_2 = np.zeros((N, N ** 2), dtype=int)
            for j in range(N):
                A_ub_2[j, j::N] = 1

            A_ub = np.concatenate((A_ub_1, A_ub_2), axis=0)
            b_ub = np.ones((2 * N,), dtype=int)

            self = cls(N)
            self.A_eq = A_eq
            self.b_eq = b_eq
            self.A_ub = A_ub
            self.b_ub = b_ub
            return self

        @classmethod
        def branch(cls, N, index, value):
            """
            Generate the integer condition for a specific link.
            
            Parameters
            ----------
            N : int
                The number of items to be sorted.
            index : int
                The 1d-index (flat index) denoting the link upon which the condition shall be
                imposed. E.g. for constraining the link ``(2, 1)`` with a total of ``N = 5`` items
                the corresponding index is ``2*5 + 1 = 11``.
            value : int
                The integer value for the link to be imposed. ``0`` means not connected while
                ``1`` means connected.
                
            Returns
            -------
            conditions : Conditions
            
            See Also
            --------
            Conditions.general : General conditions besides the integer conditions.
            """
            self = cls(N)
            self.A_eq = np.zeros(N ** 2, dtype=int)[None, :]
            self.A_eq[0, index] = 1
            self.b_eq = np.asarray([value], dtype=int)
            self.A_ub = None
            self.b_ub = None
            return self

    @classmethod
    def sort(cls, items, metric, verbose=False, **kwargs):
        items = list(items)
        N = len(items)

        distances = np.fromiter(map(
            lambda x: metric.eval(x[0][1], x[1][0]),
            it.product(items, repeat=2)
        ), dtype=float)
        conditions = cls.Conditions.general(N)

        # Save the best path together with the corresponding loss.
        # Initially we put `None` to indicate that no solution has been found yet.
        # (Raise an exception if no solution could be found.)
        solutions = deque([(None, cls.loss(items, metric))], maxlen=1)
        results = deque(maxlen=1)

        def _retrace(graph, start):
            """
            Retrace a path (possibly cyclic) within the given graph starting at the given item.
            
            Because each item has at most one connection the path is unambiguous.
            
            Parameters
            ----------
            graph : (N, N) np.ndarray
                The links among the N items to be sorted.
            start : int
                The index of the last item in the path. The retracing starts at the path's tail.
                
            Returns
            -------
            path : list[int]
                The indices of all items that are part of the path.
            """
            path = [start]
            while True:
                if np.sum(graph[:, path[-1]]) == 0:  # End of path.
                    break
                pre = np.argwhere(graph[:, path[-1]] == 1).ravel()[0]
                if pre in path:  # Cycle.
                    break
                path.append(pre)
            return path

        def _branch(branch_conditions, index=None, value=None, depth=0):
            """
            Evaluates a branch within the set of all possible solutions. A branch corresponds to
            a specific link being set to either zero or one.
            
            Parameters
            ----------
            branch_conditions : BranchAndBound.Conditions
                The integer constraints that are imposed within the current branch. This excludes
                the constraint that will be applied as a result of the current branching.
            index : 2-tuple
                The 2d-index of the link to be constrained. See `BranchAndBound.Conditions.branch`.
                If None no constraint will be imposed.
            value : int
                Either 0 (not connected) or 1 (connected).
            depth : int
                The depth within the tree-like set of all solutions. Each link being constrained
                increases the depth by 1.
                
            Returns
            -------
            None
                Appends any solutions to the nonlocal `solutions`.
            """
            nonlocal conditions, distances, results, solutions

            if verbose:
                print('New branch: {}/{} (depth), index={}, value={}'
                      .format(depth, N, index, value))

            if index is not None:
                branch_conditions = branch_conditions & cls.Conditions.branch(N, index, value)
            all_conditions = conditions & branch_conditions

            while True:
                result = optimize.linprog(
                    distances,
                    A_ub=all_conditions.A_ub,
                    b_ub=all_conditions.b_ub,
                    A_eq=all_conditions.A_eq,
                    b_eq=all_conditions.b_eq,
                    bounds=all_conditions.bounds,
                    options=kwargs
                )
                results.append(result)
                if not result.success:
                    if verbose:
                        print('[{}/{}, {}, {}] No solution found: {}'
                              .format(depth, N, index, value, result.message))
                    return

                links = result.x.astype(int).reshape(N, N)
                if links.sum() < N-1:  # Non-integer links -> branch.
                    if depth == (N**2 - N):  # All constraints applied, no solution in this branch.
                        if verbose:
                            print('[{}/{}, {}, {}] End of branch'.format(depth, N, index, value))
                        return
                    non_int_index = np.argwhere(np.ceil(result.x) != np.floor(result.x)).ravel()[0]
                    _branch(branch_conditions, non_int_index, 0, depth + 1)
                    _branch(branch_conditions, non_int_index, 1, depth + 1)
                    return

                dist = csgraph.shortest_path(links)
                cycles = dist + dist.T
                np.fill_diagonal(cycles, np.inf)  # Items cannot connect to themselves.
                if np.sum(cycles != np.inf) == 0:  # No cycle -> this is a valid solution.
                    path = _retrace(links, np.argwhere(links.sum(axis=1) == 0).ravel()[0])
                    loss = cls.loss([items[i] for i in reversed(path)], metric)
                    if verbose:
                        print('[{}/{}, {}, {}] Solution found (loss: {}; ref.loss: {})'
                              .format(depth, N, index, value, loss, solutions[-1][1]))
                    if loss < solutions[-1][1]:
                        solutions.append((path, loss))
                    return

                smallest_cycle_length = cycles.min()
                # Start at any of the cycle's vertices (if there are multiple cycles with the same
                # length then this will pick any of them which is fine as other cycles can be
                # addressed in subsequent iterations of the procedure).
                path = _retrace(links, np.argwhere(cycles == smallest_cycle_length).ravel()[0])
                if verbose:
                    print('[{}/{}, {}, {}] Ban cycle: {}'.format(depth, N, index, value, path))
                conditions.ban_cycle(path)
                all_conditions.ban_cycle(path)

        _branch(cls.Conditions(N))
        if solutions[-1][0] is None:
            warnings.warn('Unable to determine optimal sort order: {}'.format(results[-1].message))
            return items
        return [items[i] for i in reversed(solutions[-1][0])]

    sort.__doc__ = Solver.sort.__doc__
