import numpy as np

def gen_samples(params, dists):
    points = dict()
    for dist in dists:
        points.update(_make_dist(params, dist))
    return points

def _make_dist(p_global, p_local):
    N = p_local.get('num_samples', p_global['num_samples'])
    if p_local['type'] == 'gaussian':
        x, y = np.random.multivariate_normal(p_local['mean'], p_local['cov'], N).T
    if 'transforms' in p_local.keys():
        if type(p_local['transforms']) != 'list':
            p_local['transforms'] = [p_local['transforms']]
        for transform in p_local['transforms']:
            if transform == 'rotate':
                x, y = _rotate_points(x, y, p_local['theta'])
    return {p_local['name']: (x, y)}
