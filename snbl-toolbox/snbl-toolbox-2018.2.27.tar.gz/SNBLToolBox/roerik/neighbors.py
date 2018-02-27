#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import numpy as np
from scipy.linalg import cholesky


__all__ = ['neighbors']


PILATUS_X, PILATUS_Y = 1475, 1679
PIXEL = np.linalg.inv(cholesky(np.array((
    (1., 0., 0.),
    (0., 172e-3 ** 2, 0.),
    (0., 0., 172e-3 ** 2)
))))


def rx(a):
    """Rotational matrix along x"""
    return np.array((
        (1, 0, 0),
        (0, math.cos(a), math.sin(a)),
        (0, -math.sin(a), math.cos(a)),
    ))


def ry(a):
    """Rotational matrix along y"""
    return np.array((
        (math.cos(a), 0, -math.sin(a)),
        (0, 1, 0),
        (math.sin(a), 0, math.cos(a)),
    ))


def rz(a):
    """Rotational matrix along z"""
    return np.array((
        (math.cos(a), math.sin(a), 0),
        (-math.sin(a), math.cos(a), 0),
        (0, 0, 1),
    ))


def rotation1(alpha, beta, omega, kappa, phi):
    t1 = np.dot(np.dot(ry(beta), rz(-phi)), ry(-beta))
    t2 = np.dot(np.dot(ry(alpha), rz(-kappa)), ry(-alpha))
    return np.dot(np.dot(t1, t2), rz(-omega))


def rotation2(alpha, beta, omega, kappa, phi):
    s1 = np.dot(np.dot(ry(beta), rz(phi)), ry(-beta))
    s2 = np.dot(np.dot(ry(alpha), rz(kappa)), ry(-alpha))
    return np.dot(np.dot(rz(omega), s2), s1)


def ifix(v):
    return int(math.ceil(v) if v < 0 else math.floor(v))


def t1(x, y, z):
    h1 = (z - x) / y
    h2 = -(z + x) / y
    return ifix(min(h1, h2)), ifix(max(h1, h2)) + 1


def t2(x, y):
    if x >= 0 and y >= 0:
        return 1
    elif x < 0 and y < 0:
        return 2
    else:
        return 3


def t3(x, y, i):
    ip, im = ifix(x), ifix(y)
    _id = abs(ip - im)
    if _id:
        k0 = 1
        k1 = min(ip, im) + (1 if i == 1 else 0)
        k2 = k1 + _id - (0 if i == 3 else 1)
    else:
        k0 = 1 if i == 3 else 0
        k1 = k2 = 0
    return k1, k2 + 1, k0


def tanaka1(b, vecb, radius, delta):
    alpha = b[2, 2] * vecb[2]
    beta = b[2, 2]
    rp = radius + delta
    return t1(alpha, beta, rp)


def tanaka2(b, vecb, radius, delta, l):
    rp, rm = [i ** 2 for i in (radius + delta, radius - delta)]
    r1 = (b[2, 2] * vecb[2] + b[2, 2] * l) ** 2
    r3p = 0 if r1 >= rp else math.sqrt(rp - r1)
    if r1 < rm:
        r3m = math.sqrt(rm - r1)
        ir3 = 1
    else:
        r3m = ir3 = 0
    alpha = b[1, 1] * vecb[1] + b[1, 2] * (vecb[2] + l)
    beta = b[1, 1]
    return (r3p, r3m, ir3), t1(alpha, beta, r3p)


def tanaka3(b, vecb, r3, k, l):
    hklgen = []
    r3p, r3m, ir3 = [i ** 2 for i in r3]
    r1 = (b[1, 1] * vecb[1] + b[1, 2] * (vecb[2] + l) + b[1, 1] * k) ** 2
    r2p = 0 if r1 >= r3p else math.sqrt(r3p - r1)
    if r1 >= r3m:
        r2m = ir2 = 0
    else:
        ir2 = 1
        r2m = math.sqrt(r3m - r1)
    beta = b[0, 0]
    alpha = beta * vecb[0] + b[0, 1] * (vecb[1] + k) + b[0, 2] * (vecb[2] + l)
    if ir2:
        h11p = (r2p - alpha) / beta
        h11m = (r2m - alpha) / beta
        h12p = -(r2p + alpha) / beta
        h12m = -(r2m + alpha) / beta
        l1 = t2(h11p, h11m)
        l2 = t2(h12p, h12m)
        i = t3(h11p, h11m, l1)
        j = t3(h12p, h12m, l2)
        if i[2]:
            for h in range(i[0], i[1]):
                hklgen.append((h, k, l))
        if j[2]:
            for h in range(j[0], j[1]):
                hklgen.append((h, k, l))
    else:
        h11p = (r2p - alpha) / beta
        h12p = -(r2p + alpha) / beta
        l1 = t2(h11p, h12p)
        i = t3(h11p, h12p, l1)
        if i[2]:
            for h in range(i[0], i[1]):
                hklgen.append((h, k, l))
    return hklgen


def reflections(b, vecb, radius, halfdelta):
    lmin, lmax = tanaka1(b, vecb, radius, halfdelta)
    for l in range(lmin, lmax):
        r3, klimit = tanaka2(b, vecb, radius, halfdelta, l)
        for k in range(klimit[0], klimit[1]):
            hkl = tanaka3(b, vecb, r3, k, l)
            if hkl:
                for i in hkl:
                    if i != (0, 0, 0):
                        yield i


def neighbors(u, wavelength, delta, alpha, beta, omega, kappa, phi, phix, phiy, x0, y0, d0):
    if not wavelength:
        return None
    alpha, beta, omega, kappa, phi, phix, phiy = [math.radians(i) for i in (alpha, beta, omega, kappa, phi, phix, phiy)]
    halfdelta = delta / 2.
    radius = 1. / wavelength
    awl = np.array((-radius, 0., 0.))
    ubm = u / wavelength
    t = rotation1(alpha, beta, omega, kappa, phi)
    s = rotation2(alpha, beta, omega, kappa, phi)
    vecb = np.dot(np.dot(np.linalg.inv(ubm), t), awl)
    u = np.dot(ry(phiy), rx(phix)).transpose()
    b = cholesky(np.dot(ubm.transpose(), ubm))
    pixelu = np.dot(PIXEL, u)
    subm = np.dot(s, ubm)
    result = []
    for reflection in reflections(b, vecb, radius, halfdelta):
        xyz = np.dot(subm, reflection)
        ubmh = np.dot(ubm, reflection)
        x = 2 * math.asin(xyz[0] / math.sqrt(np.dot(ubmh, ubmh)))
        y = math.atan2(-xyz[2], xyz[1])
        sh = np.array((-math.cos(x), math.sin(x) * math.cos(y), -math.sin(x) * math.sin(y)))
        p = np.dot(pixelu, sh)
        if p[0] < 0:
            p *= -d0 / p[0]
            x, y = [int(math.floor(i)) for i in (p[2] + x0, p[1] + y0)]
            if 0 <= x <= PILATUS_X and 0 <= y <= PILATUS_Y:
                ext = np.linalg.norm(awl + xyz) - radius
                result.append((reflection, (y, x), ext))
    return result


def test():
    wavelength = 0.68894
    U = np.array((
        (0.022579481, -0.066943125, -0.044049163),
        (-0.010769909, 0.11496317, -0.029219808),
        (0.16529107, 0.10117289, 0.0041047721))
    )
    alpha = 50.0
    beta = 0.0
    phix = 0.01914
    phiy = 0.02620
    d0 = 145.94578
    y0, x0 = 537.45944, 744.55962
    omega, kappa, phi = 0, 0., 19.6990
    delta = 0.003
    return neighbors(U, wavelength, delta, alpha, beta, omega, kappa, phi, phix, phiy, x0, y0, d0)


if __name__ == '__main__':
    n = test()
    # import pprint
    # pprint.pprint(n)
