"""
Chan's Convex Hull O(n log h)
https://en.wikipedia.org/wiki/Chan%27s_algorithm
"""
from functools import reduce
import sys
from scipy.spatial import distance
if sys.version_info.major == 3:
    xrange = range

TURN_LEFT, TURN_RIGHT, TURN_NONE = (1, -1, 0)
import math
def cmp_to_symbol(val, other_val):
    '''returns the symbol representing the relationship between two values'''
    return '=><'[(val > other_val) - (val < other_val)]

def turn(p, q, r):
    """Returns -1, 0, 1 if p,q,r forms a right, straight, or left turn."""
    a = (q[0] - p[0])*(r[1] - p[1]) - (r[0] - p[0])*(q[1] - p[1])
    b = 0
    return (a>b) - (a<b)

def _keep_left(hull, r):
    while len(hull) > 1 and turn(hull[-2], hull[-1], r) != TURN_LEFT:
        hull.pop()
    return (not len(hull) or hull[-1] != r) and hull.append(r) or hull

def _graham_scan(points):
    """Returns points on convex hull of an array of points in CCW order."""
    points.sort()
    lh = reduce(_keep_left, points, [])
    uh = reduce(_keep_left, reversed(points), [])
    return lh.extend(uh[i] for i in xrange(1, len(uh) - 1)) or lh

def _rtangent(hull, p):
    """Return the index of the point in hull that the right tangent line from p
    to hull touches.
    """
    l, r = 0, len(hull)
    l_prev = turn(p, hull[0], hull[-1])
    l_next = turn(p, hull[0], hull[(l + 1) % r])
    while l < r:
        c = (l + r) // 2
        c_prev = turn(p, hull[c], hull[(c - 1) % len(hull)])
        c_next = turn(p, hull[c], hull[(c + 1) % len(hull)])
        c_side = turn(p, hull[l], hull[c])
        if c_prev != TURN_RIGHT and c_next != TURN_RIGHT:
            return c
        elif c_side == TURN_LEFT and (l_next == TURN_RIGHT or
                                      l_prev == l_next) or \
             c_side == TURN_RIGHT and c_prev == TURN_RIGHT:
            r = c               # Tangent touches left chain
        else:
            l = c + 1           # Tangent touches right chain
            l_prev = -c_next    # Switch sides
            l_next = turn(p, hull[l], hull[(l + 1) % len(hull)])
    return l

def _min_hull_pt_pair(hulls):
    """Returns the hull, point index pair that is minimal."""
    h, p = 0, 0
    for i in xrange(len(hulls)):
        j = min(xrange(len(hulls[i])), key=lambda j: hulls[i][j])
        if hulls[i][j] < hulls[h][p]:
            h, p = i, j
    return (h, p)

def _next_hull_pt_pair(hulls, pair):
    """
    Returns the (hull, point) index pair of the next point in the convex
    hull.
    """
    p = hulls[pair[0]][pair[1]]
    next = (pair[0], (pair[1] + 1) % len(hulls[pair[0]]))
    for h in (i for i in xrange(len(hulls)) if i != pair[0]):
        s = _rtangent(hulls[h], p)
        q, r = hulls[next[0]][next[1]], hulls[h][s]
        t = turn(p, q, r)
        if t == TURN_RIGHT or \
           t == TURN_NONE and \
           distance.euclidean(p,r) > distance.euclidean(p,q):
            next = (h, s)
    return next

#def _dist(a,b):
    #"""calculates the euclidean distance"""


def convex_hull(pts):
    """Returns the points on the convex hull of pts in CCW order."""
    for m in (1 << (1 << t) for t in xrange(len(pts))):
        hulls = [_graham_scan(pts[i:i + m]) for i in xrange(0, len(pts), m)]
        hull = [_min_hull_pt_pair(hulls)]
        for throw_away in xrange(m):
            p = _next_hull_pt_pair(hulls, hull[-1])
            if p == hull[0]:
                return [hulls[h][i] for h, i in hull]
            hull.append(p)
    return hull

if __name__ == "__main__":
    import arcpy
    fc = r"C:\temp\scratch.gdb\capitals_demo"
    geoms = []
    with arcpy.da.SearchCursor(fc, ['SHAPE@']) as rows:
        for row in rows:
            geoms.append(row[0].__geo_interface__['coordinates'])
            del row
        del rows
    hull = convex_hull(geoms)
    geojson_polygon = {
        "type": "Polygon",
        "coordinates": [hull]}
    polygon = arcpy.AsShape(geojson_polygon).projectAs(arcpy.SpatialReference(4326))
    print(arcpy.CopyFeatures_management(polygon, r"d:\scratch.gdb\polygon_hull")[0])
    print()
