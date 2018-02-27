"""

References
----------
Boleda, G., M. Baroni, N. The Pham, L. McNally. 2013. Intensionality was only alleged: On adjective-noun
composition in distributional semantics. Proceedings of IWCS 2013, Potsdam, Germany, pages 35-46.


"""
import scipy.spatial.distance
import scipy.optimize
import numpy as np
import scipy.sparse


# compositions functions.
def compose_weighted_additive(u, v, a, b):
    return a * u + b * v


def compose_full_additive(u, v, A, B):
    return A.dot(u) + B.dot(v)


def compose_dilation(u, v, lambda_):
    return (lambda_ - 1) * u.dot(v.T) * u + u.dot(u.T) * v


def compose_multiplicative(u, v):
    if scipy.sparse.issparse(u):
        return u.multiply(v)
    else:
        return u * v


def compose_lexical(U, v):
    return U.dot(v)


def compose(representation, adj=None, noun=None, model='weighted_additive', parameters=None):
    if model == 'weighted_additive':
        return compose_weighted_additive(representation[adj], representation[noun],
                                         *parameters)
    if model == 'dilation':
        return compose_dilation(representation[adj], representation[noun], parameters)

    if model == 'full_additive':
        return compose_full_additive(representation[adj], representation[noun],
                                     *parameters)

    if model == 'multiplicative':
        return compose_multiplicative(representation[adj], representation[noun])


def _learn(representation, adj_nouns, compose_model, init_values, sep=' '):
    def residual(parameters, observed, adjectives, nouns):
        return [scipy.spatial.distance.euclidean(o, compose_model(u, v, *parameters))
                for o, u, v in zip(observed, adjectives, nouns)]

    if isinstance(adj_nouns[0], str):
        x = representation.matrix[[representation.words.index(an.split(sep)[0]) for an in adj_nouns]]
        y = representation.matrix[[representation.words.index(an.split(sep)[1]) for an in adj_nouns]]

        observed_vectors = representation.matrix[[representation.words.index(an) for an in adj_nouns]]
    else:
        x = representation.matrix[[representation.words.index(an[0]) for an in adj_nouns]]
        y = representation.matrix[[representation.words.index(an[1]) for an in adj_nouns]]

        observed_vectors = representation.matrix[[representation.words.index(an) for an in adj_nouns]]

    try:
        x = x.A
        y = y.A
        observed_vectors = observed_vectors.A
    except AttributeError:
        pass

    result = scipy.optimize.least_squares(residual, init_values, args=(observed_vectors, x, y))

    return result.x


def learn_weighted_additive(representation, adj_nouns, sep=' '):
    return _learn(representation, adj_nouns, compose_weighted_additive, [0.5, 0.5], sep=sep)


def learn_dilation(representation, adj_nouns, sep=' '):
    return _learn(representation, adj_nouns, compose_dilation, [0.5], sep=sep)[0]


def learn_full_additive(representation, adj_nouns, sep=' '):
    N = representation.shape[1]

    def params_to_matrices(parameters):
        return parameters[:N ** 2].reshape(N, N), parameters[N ** 2:].reshape(N, N)

    def residual(parameters, observed, adjectives, nouns):
        A, B = params_to_matrices(parameters)
        return [scipy.spatial.distance.euclidean(o, compose_full_additive(u, v, A, B))
                for o, u, v in zip(observed, adjectives, nouns)]


    if isinstance(adj_nouns[0], str):
        x = representation.matrix[[representation.words.index(an.split(sep)[0]) for an in adj_nouns]]
        y = representation.matrix[[representation.words.index(an.split(sep)[1]) for an in adj_nouns]]

        observed_vectors = representation.matrix[[representation.words.index(an) for an in adj_nouns]]
    else:
        x = representation.matrix[[representation.words.index(an[0]) for an in adj_nouns]]
        y = representation.matrix[[representation.words.index(an[1]) for an in adj_nouns]]

        observed_vectors = representation.matrix[[representation.words.index(an) for an in adj_nouns]]

    try:
        x = x.A
        y = y.A
        observed_vectors = observed_vectors.A
    except AttributeError:
        pass

    init = np.concatenate([np.eye(N).flatten(), np.eye(N).flatten()])
    result = scipy.optimize.least_squares(residual, init, args=(observed_vectors, x, y))

    A, B = params_to_matrices(result.x)
    # representation.composition_parameters['A'] = A
    # representation.composition_parameters['B'] = B
    return A, B


def learn_lexical(representation, adj_nouns, sep=' ', opt_args=None):
    N = representation.shape[1]

    def params_to_matrices(parameters):
        return parameters.reshape(N, N)

    def residual(parameters, observed, nouns):
        U = params_to_matrices(parameters)
        return [scipy.spatial.distance.euclidean(o, compose_lexical(U, v))
                for o, v in zip(observed, nouns)]

    an_per_adjectives = {}

    if isinstance(adj_nouns[0], str):
        for an in adj_nouns:
            adj, noun = an.split(sep)
            if adj not in an_per_adjectives:
                an_per_adjectives[adj] = []
            an_per_adjectives[adj].append(an)
    else:
        for an in adj_nouns:
            adj, noun = an
            if adj not in an_per_adjectives:
                an_per_adjectives[adj] = []
            an_per_adjectives[adj].append(an)


    if len(an_per_adjectives) == 1:
        # only one adjective
        if isinstance(adj_nouns[0], str):
            y = representation.matrix[[representation.words.index(an.split(sep)[1]) for an in adj_nouns]]

            observed_vectors = representation.matrix[[representation.words.index(an) for an in adj_nouns]]
        else:
            y = representation.matrix[[representation.words.index(an[1]) for an in adj_nouns]]

            observed_vectors = representation.matrix[[representation.words.index(an) for an in adj_nouns]]

        #init = np.eye(N).flatten()
        # result = scipy.optimize.least_squares(residual, init, args=(observed_vectors, y), **opt_args)
        result = np.linalg.lstsq(y, observed_vectors)

        return params_to_matrices(result[0].T)#.x)

    else:
        result_per_adj = {}
        for adj, adj_ans in an_per_adjectives.items():
            if isinstance(adj_nouns[0], str):
                y = representation.matrix[[representation.words.index(an.split(sep)[1]) for an in adj_ans]]
                observed_vectors = representation.matrix[[representation.words.index(an) for an in adj_ans]]
            else:
                y = representation.matrix[[representation.words.index(an[1]) for an in adj_ans]]
                observed_vectors = representation.matrix[[representation.words.index(an) for an in adj_ans]]

            # init = np.eye(N).flatten()
            # result = scipy.optimize.least_squares(residual, init, args=(observed_vectors, y))
            # result_per_adj[adj] = params_to_matrices(result.x)

            result = np.linalg.lstsq(y, observed_vectors)
            result_per_adj[adj] = params_to_matrices(result[0].T)

        return result_per_adj

