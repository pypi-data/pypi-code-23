

import shapely.geometry as sg
import numpy as np

def _exterior_coords_iterator(geom):
    if isinstance(geom, sg.Point):
        yield np.asarray(geom)[None, ...]
    elif isinstance(geom, sg.Polygon):
        yield np.asarray(geom.exterior)
    elif isinstance(geom, sg.LineString):
        yield np.asarray(geom)
    elif isinstance(geom, sg.base.BaseMultipartGeometry):
        for part in geom:
            for coords in _exterior_coords_iterator(part):
                yield coords
    else:
        assert False


geoms = [
    sg.Point(0, 0),
    sg.LineString([(0, 0), (0, 1)]),
    sg.LinearRing([(0, 0), (0, 1), (0, 2)]),
    sg.MultiLineString([
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
    ]),
    sg.MultiPoint([
        (0, 0), (1, 1),
    ]),
    sg.MultiPolygon([
        sg.box(0, 0, 10, 10) - sg.box(4, 4, 6, 6),
        sg.box(15, 15, 26, 26),
    ]),
    sg.box(30, 30, 40, 40),
    sg.box(30, 30, 40, 40) - sg.box(34, 34, 36, 36),
]

geoms += [
    sg.GeometryCollection(geoms)
]

for geom in geoms:
    print('//////////////////////////////////////////////////')
    print(geom)
    coords = np.concatenate(list(_exterior_coords_iterator(geom)), axis=0)
    print(coords, coords.shape)
