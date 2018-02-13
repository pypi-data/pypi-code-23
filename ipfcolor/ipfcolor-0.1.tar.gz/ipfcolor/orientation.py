from math import sin, cos


def eu2qu(e: list, res: list):
    if isinstance(e, list) and isinstance(res, list) and len(e) == 3 and len(res) == 4:
        ee = [0.5 * element for element in e]

        c_phi = cos(ee[1])
        s_phi = sin(ee[1])
        cm = cos(ee[0] - ee[2])
        sm = sin(ee[0] - ee[2])
        cp = cos(ee[0] + ee[2])
        sp = sin(ee[0] + ee[2])

        w = c_phi * cp
        if w < 0:
            res[0] = s_phi * cm
            res[1] = s_phi * sm
            res[2] = c_phi * sp
            res[3] = -w
        else:
            res[0] = -s_phi * cm
            res[1] = -s_phi * sm
            res[2] = -c_phi * sp
            res[3] = w


def qu2om(r: list, res: list):
    if isinstance(r, list) and isinstance(res, list) and len(r) == 4 and len(res) == 9:
        qq = r[3] * r[3] - (r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
        res[0] = qq + 2.0 * r[0] * r[0]
        res[4] = qq + 2.0 * r[1] * r[1]
        res[8] = qq + 2.0 * r[2] * r[2]
        res[1] = 2.0 * (r[0] * r[1] - r[3] * r[2])
        res[5] = 2.0 * (r[1] * r[2] - r[3] * r[0])
        res[6] = 2.0 * (r[2] * r[0] - r[3] * r[1])
        res[3] = 2.0 * (r[1] * r[0] + r[3] * r[2])
        res[7] = 2.0 * (r[2] * r[1] + r[3] * r[0])
        res[2] = 2.0 * (r[0] * r[2] + r[3] * r[1])


def om2gmatrix(m: list, g: list):
    if isinstance(m, list) and isinstance(g, list) and len(m) == 9 and len(g) == 3 and len(g[0]) == 3:
        g[0][0] = m[0]
        g[0][1] = m[1]
        g[0][2] = m[2]
        g[1][0] = m[3]
        g[1][1] = m[4]
        g[1][2] = m[5]
        g[2][0] = m[6]
        g[2][1] = m[7]
        g[2][2] = m[8]
