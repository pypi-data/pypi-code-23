# coding: utf-8
from ModestMaps.Core import Coordinate
from ModestMaps.Geo import Location


def generate_coordinates(layer, geometry, zooms, padding=0):
    """ Generate a stream of (offset, count, coordinate) tuples for seeding.

        Flood-fill coordinates based on two corners, a list of zooms and padding.
    """
    # start with a simple total of all the coordinates we will need.
    if not layer:
        raise ValueError('layer argument is required')

    if not geometry:
        raise ValueError('geometry argument is required')

    if not zooms:
        zooms = range(1, 22)

    count = 0
    bounds = geometry_to_bounds(geometry)
    ul = layer.projection.locationCoordinate(bounds['nw'])
    lr = layer.projection.locationCoordinate(bounds['se'])
    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)

        rows = lr_.row + 1 - ul_.row
        cols = lr_.column + 1 - ul_.column

        count += int(rows * cols)

    # now generate the actual coordinates.
    # offset starts at zero
    offset = 0

    for zoom in zooms:
        ul_ = ul.zoomTo(zoom).container().left(padding).up(padding)
        lr_ = lr.zoomTo(zoom).container().right(padding).down(padding)

        for row in range(int(ul_.row), int(lr_.row + 1)):
            for column in range(int(ul_.column), int(lr_.column + 1)):
                coord = Coordinate(row, column, zoom)

                yield (offset, count, coord)

                offset += 1


def geometry_to_bounds(geometry):

    """
    converts a django geometry to an envelope,
    and then converts this to TileStache's
    bounds
    """
    if not geometry:
        raise ValueError('geometry is required')

    if geometry.empty:
        raise ValueError('empty geometries cannot be converted')

    envelope = geometry.envelope
    if not envelope:
        raise ValueError('this geometry does not have an envelope and its invalid')

    # this is an envelope, so for sure we have 5 coordinates
    dic = {
        'south': envelope.coords[0][0][1],
        'west': envelope.coords[0][0][0],
        'north': envelope.coords[0][2][1],
        'east': envelope.coords[0][2][0]
    }
    northwest = Location(dic['north'], dic['west'])
    southeast = Location(dic['south'], dic['east'])

    return {
        'nw': northwest,
        'se': southeast
    }
