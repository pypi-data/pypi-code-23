#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: djio.geometry
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Working with geometries?  Need help?  Here it is!
"""

from . import hashing
from .errors import DjioException
from abc import ABCMeta, abstractmethod, abstractstaticmethod
from collections import namedtuple
from CaseInsensitiveDict import CaseInsensitiveDict
from enum import Enum, IntFlag
from osgeo import ogr
from geoalchemy2.types import WKBElement, WKTElement
from geoalchemy2.shape import to_shape as to_shapely
from geoalchemy2.shape import from_shape as from_shapely
import math
from measurement.measures import Area, Distance
import numpy as np
import re
import shapely.errors
from shapely.geometry import box, Point as ShapelyPoint, LineString, LinearRing, Polygon as ShapelyPolygon
from shapely.geometry.base import BaseGeometry
from shapely.wkb import dumps as dumps_wkb
from shapely.wkb import loads as loads_wkb
from shapely.wkt import dumps as dumps_wkt
from shapely.wkt import loads as loads_wkt
from typing import Any, Dict, Callable, Iterable, List, Optional, Set, Tuple, Type


class SpatialReferenceException(DjioException):
    """
    Raised when something goes wrong with a spatial reference.
    """


class GeometryException(DjioException):
    """
    Raised when something goes wrong with a geometry.
    """


PointTuple = namedtuple('PointTuple', ['x', 'y', 'z', 'srid'])  #: a lightweight tuple that represents a point

LatLonTuple = namedtuple('LatLonTuple', ['latitude', 'longitude'])  #: a lightweight tuple that represents a location


class LateralSides(Enum):
    """
    This is a simple enumeration that identifies the lateral side of line (left or right).
    """
    LEFT = 'left'  #: the left side of the line
    RIGHT = 'right'  #: the right side of the line


class SpatialReference(object):
    """
    A spatial reference system (SRS) or coordinate reference system (CRS) is a coordinate-based local, regional or
    global system used to locate geographical entities. A spatial reference system defines a specific map projection,
    as well as transformations between different spatial reference systems.

    .. seealso::

        https://en.wikipedia.org/wiki/Spatial_reference_system
    """
    _instances = {}  #: the instances of spatial reference that have been created
    _metric_linear_unit_names: Set[str] = {'meter', 'metre'}  #: metric linear distance unit names
    _preferred_utm_srids: Dict[int, int] = {
        zone: int('269{zone}'.format(zone=zone if zone > 9 else '0{zone}'.format(zone=zone))) for zone in range(1, 23)
    }  #: a mapping of preferred SRIDs for supported UTM zones
    # Add the known oddballs to the preferred UTM SRIDs dictionary.
    _preferred_utm_srids[59] = 3372
    _preferred_utm_srids[60] = 3373

    def __init__(self, srid: int):
        """

        :param srid: the well-known spatial reference ID
        """
        # To coordinate __init__ with __new__, we're using a flag attribute that indicates to this instance that
        # even if __init__ is being called a second time, there's nothing more to do.
        if not hasattr(self, '_init'):
            self._init = True  # Mark this instance as "initialized".
            self._srid: int = srid  #: the spatial reference well-known ID
            # Keep a handy reference to OGR spatial reference.
            self._ogr_srs = self._get_ogr_sr(self._srid)
            self._is_metric = SpatialReference._ogr_is_metric(self._ogr_srs)
            # Is this a known UTM zone?
            self._is_utm: bool = self._srid in SpatialReference._preferred_utm_srids.values()
            # We'll momentarily assume that there is no UTM zone associated with this spatial reference.
            self._utm_zone: Optional[int] = None  #: the UTM zone associated with this spatial reference
            # But now let's see if we find that the SRID appears in the dictionary of known UTM zones...
            zones_for_srid = [
                zone for zone in SpatialReference._preferred_utm_srids.keys()
                if SpatialReference._preferred_utm_srids[zone] == self._srid
            ]
            # If we got at least
            if len(zones_for_srid) != 0:
                self._utm_zone = zones_for_srid[0]
            # TODO: Check for multiples and log a warning, or raise an exception (?)
            # If we didn't find the UTM zone in the dictionary, there's a possibility that the OGR spatial reference
            # has some advice.
            if self._utm_zone is None:
                _ogr_srs_utm_zone = self._ogr_srs.GetUTMZone()
                self._utm_zone = _ogr_srs_utm_zone if _ogr_srs_utm_zone != 0 else None

    def __new__(cls, srid: int):
        # If this spatial reference has already been created...
        if srid in SpatialReference._instances:
            # ...use the current instance.
            return SpatialReference._instances[srid]
        else:  # Otherwise, create a new instance.
            new_sr = super(SpatialReference, cls).__new__(cls)
            # Save it in the cache.
            SpatialReference._instances[srid] = new_sr
            # That's that.
            return new_sr

    @property
    def srid(self) -> int:
        """
        Get the spatial reference's well-known ID (srid).

        :return: the well-known spatial reference ID
        """
        return self._srid

    @property
    def is_metric(self) -> bool:
        """
        Is this a projected spatial reference system that measures linear units in single meters?

        :return: `true` if this is a projected spatial reference system that measures linear units in single meters
        """
        return self._is_metric

    @property
    def ogr_sr(self) -> ogr.osr.SpatialReference:
        """
        Get the OGR spatial reference.

        :return:  the OGR spatial reference
        """
        return self._ogr_srs

    @property
    def is_geographic(self) -> bool:
        """
        Is this spatial reference geographic?

        :return: `true` if this is a geographic spatial reference, otherwise `false`
        """
        return self._ogr_srs.IsGeographic() == 1

    @property
    def is_projected(self) -> bool:
        """
        Is this spatial reference projected?

        :return: `true` if this is a projected spatial reference, otherwise `false`
        """
        return self._ogr_srs.IsProjected() == 1

    @property
    def utm_zone(self) -> int or None:
        """
        Get the UTM (Universal Trans-Mercator) zone associated with this spatial reference.
        :return: the associated UTM zone
        """
        return self._utm_zone

    @property
    def is_utm(self) -> bool:
        return self._is_utm

    def is_same_as(self, other: 'SpatialReference' or int) -> bool:
        """
        Test a spatial reference or SRID to see if it represents this spatial reference.
        :param other: the other spatial reference (or SRID)
        :return: ``True`` if the other parameter represents the same spatial reference, otherwise ``False``
        """
        if other == self:  # Let's do the quickest test first!
            return True
        elif isinstance(other, SpatialReference):
            return other.srid == self.srid
        else:
            return other == self.srid

    @staticmethod
    def _ogr_is_metric(ogr_sr: ogr.osr.SpatialReference) -> bool:
        # If the coordinate system isn't projected...
        if ogr_sr.IsProjected() != 1:
            # ...it's not metric.
            return False
        # If the linear unit isn't one...
        if ogr_sr.GetLinearUnits() != 1.0:
            # ...it's not metric.
            return False
        # Get the linear unit name.
        linear_units_name: str = ogr_sr.GetLinearUnitsName()
        # If no linear unit name is supplied...
        if linear_units_name is None:
            # ...we can't claim this to be a "metric" spatial reference.
            return False
        # If we got this far, our final determination is based on whether or not we see the linear unit name in
        # set of names that mean "meter".
        return linear_units_name.lower() in SpatialReference._metric_linear_unit_names

    @staticmethod
    def from_srid(srid: int) -> 'SpatialReference':
        # If this spatial reference has already been created...
        if srid in SpatialReference._instances:
            # ...use the current instance.
            return SpatialReference._instances[srid]
        else:  # Otherwise, create a new instance.
            new_sr = SpatialReference(srid=srid)
            # Save it in the cache.
            SpatialReference._instances[srid] = new_sr
            # That's that.
            return new_sr

    @staticmethod
    def _get_ogr_sr(srid: int) -> ogr.osr.SpatialReference:
        """
        Get an OGR spatial reference from its spatial reference ID (srid).

        :param srid: the spatial reference ID
        :return: the OGR spatial reference.
        """
        # Create the OGR spatial reference.
        ogr_sr = ogr.osr.SpatialReference()
        # Let's assume the SRID is defined by the EPSG.
        # (Note: If we need to support others, this is the place to do it.)
        ogr_sr.ImportFromEPSG(srid)
        # That's that.
        return ogr_sr

    @staticmethod
    def get_utm_from_longitude(longitude: float) -> 'SpatialReference':
        """
        Get the UTM (Universal Trans-Mercator) spatial reference for a given longitude.
        :param longitude: the longitude
        :return: the UTM spatial reference
        :raises SpatialReferenceException: if the UTM zone has no supported spatial reference
        """
        zone = int(math.floor(longitude + 180) / 6) + 1
        return SpatialReference.get_utm_for_zone(zone=zone)

    @staticmethod
    def get_utm_for_zone(zone: int) -> 'SpatialReference':
        """
        Get the UTM (Universal Trans-Mercator) spatial reference for a given zone.
        :param zone: the UTM zone
        :return: the UTM spatial reference
        :raises SpatialReferenceException: if the UTM zone has no supported spatial reference
        """
        srid = None  # We're going to try to fetch the preferred UTM srid.
        try:
            srid = SpatialReference._preferred_utm_srids[zone]
        except KeyError:
            raise SpatialReferenceException('Unsupported UTM zone: {zone}.'.format(zone=zone))
        # Still here? Great.  That means that we do have a preferred spatial reference for this zone.
        try:
            # Let's start by trying to return an instance from the cache.
            return SpatialReference._instances[srid]
        except KeyError:
            # If we missed in the cache, that's OK.  We'll create the new one now.
            return SpatialReference.from_srid(srid=srid)


class GeometryType(IntFlag):
    """
    These are the supported geometric data types.
    """
    UNKNOWN: int = 0  #: The geometry type is unknown.
    POINT: int = 1  #: a point geometry
    POLYLINE: int = 2  #: a polyline geometry
    POLYGON: int = 4  #: a polygon geometry


_shapely_geom_type_map: Dict[str, GeometryType] = {
    'point': GeometryType.POINT,
    'linestring': GeometryType.POLYLINE,
    'linearring': GeometryType.POLYLINE,
    'polygon': GeometryType.POLYGON
}  #: a mapping Shapely geometry types strings to Djio geometry types

_shapely_geom_dimensions_map: Dict[str, int] = {
    'point': 0,
    'linestring': 1,
    'linearring': 1,
    'polygon': 2
}  #: a mapping Shapely geometry types strings to their respective dimensionalities

_geometry_factory_functions: Dict[GeometryType, Callable[[BaseGeometry, SpatialReference], 'Geometry']] = {

}  #: a hash of GeometryTypes to functions that can create that type from a base geometry


class Geometry(object):
    """
    This is the common base class for all of the geometry types.
    """
    __metaclass__ = ABCMeta

    # This is a regex that matches an EWKT string, capturing the spatial reference ID (SRID) in a group called 'srid'
    # and the rest of the well-known text (WKT) in a group called 'wkt'.
    _ewkt_re = re.compile(
        r"srid=(?P<srid>\d+)\s*;\s*(?P<wkt>.*)",
        flags=re.IGNORECASE)  #: a regex that matches extended WKT (EWKT)

    # This is the function we use to hash geometries.
    _djiohash: Callable = hashing.djiohash_v1

    def __init__(self,
                 shapely_geometry: BaseGeometry,
                 spatial_reference: SpatialReference or int = None):
        """

        :param shapely_geometry: a Shapely geometry
        :param spatial_reference: the geometry's spatial reference
        """
        # Keep that reference to the Shapely geometry.
        self._shapely_geometry: BaseGeometry = shapely_geometry
        # Let's figure out what the spatial reference is.  (It might be an instance of SpatialReference, or it might
        # be the SRID.)
        self._spatial_reference: SpatialReference = (spatial_reference
                                                     if isinstance(spatial_reference, SpatialReference)
                                                     else SpatialReference.from_srid(srid=spatial_reference))
        self._caches: Dict[str, Any] = {}  #: a repository for cached and lazily-initialized objects

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get this geometry's type.

        :return: the geometry's type
        """
        try:
            return _shapely_geom_type_map[self._shapely_geometry.geom_type.lower()]
        except KeyError:
            return GeometryType.UNKNOWN

    @property
    def dimensions(self) -> int:
        """
        How many dimensions does this geometry occupy?  For example: a point is zero-dimensional (0); a line is
        one-dimensional (1); and a polygon is two-dimensional (2).
        :return: the dimensionality of the geometry
        """
        try:
            return self._caches['dimensions']
        except KeyError:
            # Retrieve the dimensions from the dictionary of known dimensions for Shapely gometry
            # types.
            dimensions = _shapely_geom_dimensions_map[self.shapely_geometry.geom_type.lower()]
            self._caches['dimensions'] = dimensions  # Cache it for next time.
            return dimensions

    @abstractmethod
    def get_point_tuples(self) -> Iterable[PointTuple]:
        """
        Get an ordered iteration of all the coordinates in the geometry as point tuples.
        :return: an enumeration of point tuples
        """
        raise NotImplementedError('The method is not implemented.')

    @property
    def shapely_geometry(self) -> BaseGeometry:
        """
        Get the Shapely geometry underlying this geometry object.

        :return: the Shapely geometry
        """
        return self._shapely_geometry

    @property
    def envelope(self) -> 'Envelope':
        """
        Get the envelope (bounding box) of the geometry.

        :return: the geometry's envelope
        """
        # If we've already generated the envelope once...
        try:
            # ...just return it.
            return self._caches['envelope']
        except KeyError:
            # Otherwise, it looks like we need to create it now.
            bounds = self.shapely_geometry.bounds
            envelope = Envelope(min_x=bounds[0],
                                min_y=bounds[1],
                                max_x=bounds[2],
                                max_y=bounds[3],
                                spatial_reference=self.spatial_reference)
            # Cache it for next time.
            self._caches['envelope'] = envelope
            # Now we can give it to the caller.
            return envelope

    @property
    def representative_point(self) -> 'Point':
        try:
            # First, let's see if we've cached the point.
            return self._caches['representative_point']
        except KeyError:
            # OK.  This is the first time it's been requested, so let's create it.
            rp = Point(self.shapely_geometry.representative_point(), spatial_reference=self.spatial_reference)
            # Add it to the cache for next time.
            self._caches['representative_point'] = rp
            # That's that.
            return rp

    @abstractmethod
    def iter_coords(self) -> Iterable[Tuple[float, float] or Tuple[float, float, float]]:
        """
        Retrieve the coordinates that define this geometry as a flattened, ordered iteration.
        :return: and ordered iteration of tuples that describe the geometry's coordinates
        """
        raise NotImplementedError('The method has not been implemented.')

    @property
    def spatial_reference(self) -> SpatialReference:
        """
        Get the geometry's spatial reference.

        :return: the geometry's spatial reference
        """
        return self._spatial_reference

    @property
    def to_ogr(self) -> ogr.Geometry:
        """
        Get the OGR geometry equivalent of this geometry.

        :return: the OGR geometry equivalent
        """
        # Create a new OGR geometry.  (We don't want one from the cache because we don't know what the caller will
        # do to it once we send it back.)
        return self._get_ogr_geometry(from_cache=False)

    def djiohash(self):
        """
        Get this geometry's hash value.

        :return: the hash value
        """
        return Geometry._djiohash(
            geometry_type_code=self.geometry_type,
            srid=self.spatial_reference.srid,
            coordinates=self.iter_coords())

    def _get_ogr_geometry(self, from_cache: bool = True) -> ogr.Geometry:
        """
        Subclasses can use this method to get the OGR geometry equivalent.

        :param from_cache: Return the cached OGR geometry (if it's available).
        :return: the OGR geometry equivalent
        """
        # If we have already created the OGR geometry once, just return it again.
        if from_cache:
            try:
                return self._caches['ogr_geometry']
            except KeyError:
                pass  # This is OK.  It's just a cache miss.
        # Perform the WKB->OGR Geometry conversion.
        ogr_geometry: ogr.Geometry = ogr.CreateGeometryFromWkb(self._shapely_geometry.wkb)
        # Assign the spatial reference.
        ogr_geometry.AssignSpatialReference(self._spatial_reference.ogr_sr)
        # Save it for next time.
        self._caches['ogr_geometry'] = ogr_geometry
        # That's that!
        return ogr_geometry

    def project(self,
                preferred_spatial_reference: SpatialReference or int = None,
                fallback_spatial_reference: SpatialReference or int or None = 3857) -> 'Geometry':
        return Projector.get_instance().project(geometry=self,
                                                preferred_spatial_reference=preferred_spatial_reference,
                                                fallback_spatial_reference=fallback_spatial_reference)

    def transform_to_utm(self) -> 'Geometry':
        # If this geometry is already in a known UTM projection...
        if self.spatial_reference.is_utm:
            # ...just return it.
            return self
        elif self.spatial_reference.utm_zone is not None:
            # OK, so we're not already in a UTM projection.  But it seems as though our spatial reference is
            # associated with a UTM zone.
            utm_sr: SpatialReference = SpatialReference.get_utm_for_zone(self.spatial_reference.utm_zone)
            # Now we can just transform to this spatial reference.
            return self.transform(spatial_reference=utm_sr)
        else:  # Looks like we have more work to do.
            # We need the envelope's representative point.
            rp: Point = self.envelope.representative_point
            # Use the longitude of the representative point to fetch the corresponding UTM zone.
            utm_sr: SpatialReference = SpatialReference.get_utm_from_longitude(rp.to_latlon_tuple().longitude)
            # Now we can transform accordingly.
            return self.transform(spatial_reference=utm_sr)

    def transform(self, spatial_reference: SpatialReference or int) -> 'Geometry':
        """
        Create a new geometry based on this geometry but in another spatial reference.

        :param spatial_reference: the target spatial reference
        :return: the new transformed geometry
        """
        # Retrieve (or create) the dictionary of cached transforms.
        cached_transforms: Dict[int, Geometry] = None  # We're just declaring it here.
        # If we've already created the cache...
        try:
            # ...we should use it.
            cached_transforms = self._caches['transforms']
        except KeyError:
            # Otherwise, create one...
            cached_transforms = {}
            # ...and add it to the caches.
            self._caches['transforms'] = cached_transforms
        # Figure out the target spatial reference.
        sr: SpatialReference = (
            spatial_reference if isinstance(spatial_reference, SpatialReference)
            else SpatialReference.from_srid(srid=spatial_reference)
        )
        # If this geometry is already in the target spatial reference...
        if self.spatial_reference.srid == sr.srid:
            # ...no transformation is necessary.
            return self
        # If we've already transformed for this spatial reference once...
        if sr.srid in cached_transforms:
            # ...just return the previous product.
            return cached_transforms[sr.srid]
        else:
            # We need the OGR geometry.
            ogr_geometry = self._get_ogr_geometry(from_cache=True)
            # Transform the OGR geometry to the new coordinate system...
            ogr_geometry.TransformTo(sr.ogr_sr)
            # ...and build the new djio geometry from it.
            transformed_geometry: Geometry = Geometry.from_ogr(ogr_geom=ogr_geometry)
            # Cache the shapely geometry in case somebody comes calling again.
            cached_transforms[sr.srid] = transformed_geometry
            # Now we can return it.
            return transformed_geometry

    def to_gml(self, version: int or str = 3) -> str:
        """
        Export the geometry to GML.

        :param version: the desired GML version
        :return: the GML representation of the geometry
        """
        _ogr = self._get_ogr_geometry(from_cache=True)
        return _ogr.ExportToGML(options=[
            'FORMAT=GML{version}'.format(version=version)
        ])

    @abstractmethod
    def flip_coordinates(self) -> 'Geometry':
        """
        Create a geometry based on this one, but with the X and Y axis reversed.

        :return: a new :py:class:`Geometry` with reversed ordinals.
        """
        raise NotImplementedError('The subclass must implement this method.')

    @staticmethod
    def from_shapely(shapely_geometry: BaseGeometry,
                     spatial_reference: SpatialReference or int) -> 'Geometry':
        """
        Create a new geometry based on a Shapely :py:class:`BaseGeometry`.

        :param shapely_geometry: the Shapely base geometry
        :param spatial_reference: the spatial reference (or spatial reference ID)
        :return: the new geometry
        :seealso:  :py:class:`Point`
        :seealso: :py:class:`Polyline`
        :seealso: :py:class:`Polygon`
        """
        # Get Shapely's version of the geometry type.  (Note that the keys in the dictionary are all lower-cased.)
        geometry_type: GeometryType = _shapely_geom_type_map[shapely_geometry.geom_type.lower()]
        # With this information, we can use the registered function to create the djio geometry.
        return _geometry_factory_functions[geometry_type](shapely_geometry, spatial_reference)

    @staticmethod
    def from_ogr(ogr_geom: ogr.Geometry, spatial_reference: SpatialReference or int = None) -> 'Geometry':
        # Grab the spatial reference from the arguments.
        _sr = spatial_reference
        # If the caller didn't provide one...
        if _sr is None:
            # ...dig it out of the geometry's spatial reference.
            ogr_srs: ogr.osr.SpatialReference = ogr_geom.GetSpatialReference()
            # Now, if the geometry didn't bring it's own spatial reference, we have a problem
            if ogr_srs is None:
                raise GeometryException('The geometry has no spatial reference, and no SRID was supplied.')
            _sr = int(ogr_srs.GetAttrValue('AUTHORITY', 1))
        return Geometry.from_wkb(wkb=ogr_geom.ExportToWkb(), spatial_reference=_sr)

    @staticmethod
    def from_ewkt(ewkt: str) -> 'Geometry':
        """
        Create a geometry from EWKT, a PostGIS-specific format that includes the spatial reference system identifier an
        up to four (4) ordinate values (XYZM).  For example: SRID=4326;POINT(-44.3 60.1) to locate a longitude/latitude
        coordinate using the WGS 84 reference coordinate system.

        :param ewkt: the extended well-known text (EWKT)
        :return: the geometry
        """
        # Let's see if we can match the format so we can separate the SRID from the rest of the WKT.
        ewkt_match = Geometry._ewkt_re.search(ewkt)
        if not ewkt_match:
            raise GeometryException('The EWKT is not properly formatted.')  # TODO: Add more information?
        # We have a match!  Let's go get the pieces.
        srid = int(ewkt_match.group('srid'))  # Grab the SRID.
        wkt = ewkt_match.group('wkt')  # Get the WKT.
        # Now we have enough information to create a Shapely geometry plus the SRID, so...
        return Geometry.from_wkt(wkt=wkt, spatial_reference=srid)

    @staticmethod
    def from_wkt(wkt: str, spatial_reference: SpatialReference or int) -> 'Geometry':
        _shapely = loads_wkt(wkt)
        return Geometry.from_shapely(shapely_geometry=_shapely, spatial_reference=spatial_reference)

    @staticmethod
    def from_wkb(wkb: str, spatial_reference: SpatialReference or int) -> 'Geometry':
        # https://geoalchemy-2.readthedocs.io/en/0.2.6/_modules/geoalchemy2/shape.html#to_shape
        _shapely = loads_wkb(wkb)
        return Geometry.from_shapely(shapely_geometry=_shapely, spatial_reference=spatial_reference)

    @staticmethod
    def from_gml(gml: str) -> 'Geometry':
        raise NotImplementedError('Coming soon...')

    @staticmethod
    def from_geoalchemy2(spatial_element: WKBElement or WKTElement,
                         spatial_reference: SpatialReference or int) -> 'Geometry':
        shapely_geometry = to_shapely(spatial_element)
        return Geometry.from_shapely(shapely_geometry=shapely_geometry, spatial_reference=spatial_reference)


def _register_geometry_factory(geometry_type: GeometryType,
                               factory_function: Callable[[BaseGeometry, SpatialReference], Geometry]):
    """
    Register a geometry factory function.

    :param geometry_type: the enumerated geometry type
    :param factory_function: the factory function
    """
    _geometry_factory_functions[geometry_type] = factory_function


class Point(Geometry):
    """
    In modern mathematics, a point refers usually to an element of some set called a space.  More specifically, in
    Euclidean geometry, a point is a primitive notion upon which the geometry is built, meaning that a point cannot be
    defined in terms of previously defined objects. That is, a point is defined only by some properties, called axioms,
    that it must satisfy. In particular, the geometric points do not have any length, area, volume or any other
    dimensional attribute. A common interpretation is that the concept of a point is meant to capture the notion of a
    unique location in Euclidean space.
    """

    def __init__(self,
                 shapely_geometry: ShapelyPoint,
                 spatial_reference: SpatialReference or int = None):
        """

        :param shapely_geometry: a Shapely geometry
        :param spatial_reference: the geometry's spatial reference
        """
        # Redefine the shapely geometry (mostly to help out the IDEs).
        self._shapely_geometry: ShapelyPoint = None
        super().__init__(shapely_geometry=shapely_geometry, spatial_reference=spatial_reference)

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get the geometry type.

        :return:  :py:attr:`GeometryType.POINT`
        """
        return GeometryType.POINT

    @property
    def x(self) -> float:
        """
        Get the X coordinate.

        :return: the X coordinate
        """
        # noinspection PyUnresolvedReferences
        return self._shapely_geometry.x

    @property
    def y(self) -> float:
        """
        Get the Y coordinate.

        :return: the Y coordinate
        """
        # noinspection PyUnresolvedReferences
        return self._shapely_geometry.y

    @property
    def z(self) -> float or None:
        """
        Get the Z coordinate.

        :return: the Z coordinate
        """
        # noinspection PyUnresolvedReferences
        try:
            return self._shapely_geometry.z
        except shapely.errors.DimensionError:
            return None

    @property
    def dimensions(self) -> int:
        """
        A point is zero-dimensional (0)
        :return: zero (0)
        """
        return 0

    def flip_coordinates(self) -> 'Point':
        """
        Create a point based on this one, but with the X and Y axis reversed.

        :return: a new :py:class:`Geometry` with reversed ordinals.
        """
        _shapely: ShapelyPoint = ShapelyPoint(self._shapely_geometry.y, self._shapely_geometry.x)
        return Point(shapely_geometry=_shapely, spatial_reference=self.spatial_reference)

    def to_point_tuple(self) -> PointTuple:
        """
        Get a lightweight tuple representation of this point.

        :return: the tuple representation of the point
        """
        # If we've been here before...
        try:
            # ...return the same result as last time.
            return self._caches['point_tuple']
        except KeyError:
            # Otherwise, create a point tuple.
            point_tuple = PointTuple(x=self.x, y=self.y, z=self.z, srid=self.spatial_reference.srid)
            # Save it for next time.
            self._caches['point_tuple'] = point_tuple
            # Now give it back to the caller.
            return point_tuple

    def iter_coords(self) -> Iterable[Tuple[float, float] or Tuple[float, float, float]]:
        """
        Retrieve the coordinates that define this geometry.  For a :py:class:`Point`, the iteration shall contain a
        single set of coordinates.
        :return: an iteration containing a single tuple containing this point's coordinates
        """
        try:
            return self._caches['iter_coords']
        except KeyError:
            _tuples = [(self.x, self.y, self.z) if self.z is not None else (self.x, self.y)]
            self._caches['iter_coords'] = _tuples
            return _tuples

    def to_latlon_tuple(self) -> LatLonTuple:
        """
        Get a lightweight latitude/longitude tuple representation of this point.

        :return: the latitude/longitude tuple representation of this point
        """
        # If we've been here before...
        try:
            # ...return the same result as last time.
            return self._caches['latlon_tuple']
        except KeyError:  # Otherwise, we need to create it.
            # We can use this point's coordinates directly if it's already in WGS84, otherwise we need to project it
            # first.
            p = self if self.spatial_reference.srid == 4326 else self.transform(spatial_reference=4326)
            # Create the tuple.
            latlon_tuple = LatLonTuple(latitude=p.y, longitude=p.x)
            # Save it for next time.
            self._caches['latlon_tuple'] = latlon_tuple
            # Now give it back to the caller.
            return latlon_tuple

    @staticmethod
    def from_point_tuple(point_tuple: PointTuple) -> 'Point':
        """
        Create a point from a point tuple.

        :param point_tuple: the point tuple
        :return: the new point
        """
        p = Point.from_coordinates(x=point_tuple.x, y=point_tuple.y, spatial_reference=point_tuple.srid)
        # Go ahead and set the cached tuple property (since we have it right here).
        p._lazy_point_tuple = tuple
        # That's that.
        return p

    @staticmethod
    def from_latlon_tuple(latlon_tuple: LatLonTuple) -> 'Point':
        """
        Create a point from a latitude/longitude tuple.

        :param latlon_tuple: the latitude/longitude tuple
        :return: the new point
        """
        # TODO: 3D (Note that z=0.0 is hard-coded.)
        pt: PointTuple = PointTuple(x=latlon_tuple.longitude, y=latlon_tuple.latitude, z=0.0, srid=4326)
        return Point.from_point_tuple(pt)

    @staticmethod
    def from_lat_lon(latitude: float, longitude: float) -> 'Point':
        """
        Create a geometry from a set of latitude, longitude coordinates.

        :param latitude: the latitude
        :param longitude: the longitude
        :return: :py:class:`Point`
        """
        _shapely = ShapelyPoint(longitude, latitude)
        p = Point(shapely_geometry=_shapely, spatial_reference=4326)
        return p

    @staticmethod
    def from_coordinates(x: float,
                         y: float,
                         spatial_reference: SpatialReference or int,
                         z: Optional[float] = None):
        """
        Create a point from its coordinates.

        :param x: the X coordinate
        :param y: the Y coordinate
        :param spatial_reference: the spatial reference (or spatial reference ID)
        :param z: the Z coordinate
        :return: the new :py:class:`Point`
        """
        _shapely = ShapelyPoint(x, y, z) if z is not None else ShapelyPoint(x, y)
        return Point(shapely_geometry=_shapely, spatial_reference=spatial_reference)

    @staticmethod
    def from_shapely(shapely: ShapelyPoint,
                     srid: int) -> 'Point':
        """
        Create a new point based on a Shapely point.

        :param shapely: the Shapely point
        :param srid: the spatial reference ID
        :return: the new geometry
        :seealso:  :py:func:`Geometry.from_shapely`
        """
        return Point(shapely_geometry=shapely, spatial_reference=srid)

    # TODO: Start adding Point-specific methods and properties.


# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POINT, Point)


class Polyline(Geometry):
    """
    In geometry, a polygonal chain is a connected series of line segments. More formally, a polygonal chain P is a curve
    specified by a sequence of points (A1 , A2, ... , An ) called its vertices. The curve itself consists of the line
    segments connecting the consecutive vertices. A polygonal chain may also be called a polygonal curve, polygonal
    path,  polyline,  piecewise linear curve, broken line or, in geographic information systems (that's us), a
    linestring or linear ring.
    """

    def __init__(self,
                 shapely_geometry: LineString or LinearRing,
                 spatial_reference: SpatialReference or int = None):
        super().__init__(shapely_geometry=shapely_geometry, spatial_reference=spatial_reference)

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get the geometry type.

        :return:  :py:attr:`GeometryType.POLYLINE`
        """
        return GeometryType.POLYLINE

    @property
    def dimensions(self) -> int:
        """
        A polyline is one-dimensional (1)
        :return: one (1)
        """
        return 1

    def iter_coords(self) -> Iterable[Tuple[float, float] or Tuple[float, float, float]]:
        """
        Retrieve the coordinates that define this line.
        :return: an iteration containing the polyline's coordinates
        """
        try:
            return self._caches['iter_coords']
        except KeyError:
            _tuples = list(self._shapely_geometry.coords)  # TODO: This needs to be tested.  It may be necessary to do more transformation.
            self._caches['iter_coords'] = _tuples
            return _tuples

    # TODO: Start adding Polyline-specific methods and properties.


# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POLYLINE, Polyline)


class Polygon(Geometry):
    """
    In elementary geometry, a polygon is a plane figure that is bounded by a finite chain of straight line segments
    closing in a loop to form a closed polygonal chain or circuit. These segments are called its edges or sides, and the
    points where two edges meet are the polygon's vertices (singular: vertex) or corners. The interior of the polygon is
    sometimes called its body.
    """

    def __init__(self,
                 shapely_geometry: ShapelyPolygon,
                 spatial_reference: SpatialReference or int = None):
        """

        :param shapely_geometry: a Shapely geometry
        :param spatial_reference: the geometry's spatial reference
        """
        # Redefine the shapely geometry (mostly to help out the IDEs).
        self._shapely_geometry: ShapelyPolygon = None
        super().__init__(shapely_geometry=shapely_geometry, spatial_reference=spatial_reference)

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get the geometry type.

        :return:  :py:attr:`GeometryType.POLYGON`
        """
        return GeometryType.POLYGON

    @property
    def dimensions(self) -> int:
        """
        A polygon is two-dimensional (2).
        :return: two (2)
        """
        return 2

    def iter_coords(self) -> Iterable[Tuple[float, float] or Tuple[float, float, float]]:
        """
        Retrieve the polygon's coordinates as a flattened enumeration.
        :return: an iteration containing the polyline's coordinates
        """
        # For more information, have a look at this:
        # https://stackoverflow.com/questions/21824157/how-to-extract-interior-polygon-coordinates-using-shapely
        try:
            return self._caches['iter_coords']
        except KeyError:
            _tuples = list(self._shapely_geometry.exterior.coords[:])  # TODO: This needs to be tested.  It may be necessary to do more transformation.
            for interior in self._shapely_geometry.interiors:
                _tuples.extend(interior.coords[:])
            self._caches['iter_coords'] = _tuples
            return _tuples

    def get_area(self, spatial_reference: Optional[SpatialReference or int] = None) -> Area:
        # TODO: This method is *ripe* for refactoring!
        sr = spatial_reference
        if sr is None:
            sr = SpatialReference.from_srid(3857)  # TODO: We can apply a more sophisticated mechanism here.
        elif not isinstance(spatial_reference, SpatialReference):
            sr = SpatialReference.from_srid(srid=spatial_reference)
        # Do a sanity check:  If the spatial reference isn't projected and measured in meters...
        if not sr.is_metric:
            raise GeometryException('The requested spatial reference is not projected, or is not metric.')
        # At this point, we know we're dealing with a metric projected coordinate system, so...
        if sr.srid == self.spatial_reference.srid:
            # ...we can just create the area.
            return Area(sq_m=self.shapely_geometry.area)
        else:
            # Otherwise, we need to transform the geometry to the target spatial reference, then get the area.
            return Area(sq_m=self.transform(spatial_reference).shapely_geometry.area)

    # TODO: Start adding Polygon-specific methods and properties.


# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POLYGON, Polygon)


class Envelope(Polygon):
    """
    An envelope represents the minimum bounding rectangle (minimum x and y values, along with maximum x and y values)
    defined by coordinate pairs of a geometry. All coordinates for the geometry fall within the envelope.
    """

    def __init__(self,
                 min_x: float,
                 min_y: float,
                 max_x: float,
                 max_y: float,
                 spatial_reference: SpatialReference or int):
        """

        :param min_x: the minimum X coordinate
        :param min_y: the minimum Y coordinate
        :param max_x: the maximum X coordinate
        :param max_y: the maximum Y coordinate
        :param spatial_reference: the spatial reference (or spatial reference ID) in which the coordinates are expressed
        """
        # Construct a Shapely polygon using the box() function, and let the parent take it from here.
        super().__init__(shapely_geometry=box(minx=min_x, miny=min_y, maxx=max_x, maxy=max_y),
                         spatial_reference=spatial_reference)


class Projector(object):
    """
    Use a projector to get a projected version of a geographic geometry, or to re-project a projected geometry.
    """
    _instance: 'Projector' = None  #: the shared projector instance

    @staticmethod
    def set_instance(projector: 'Projector'):
        """
        Set the shared projector instance.
        :param projector: the shared projector
        """
        Projector._instance = projector

    @staticmethod
    def get_instance() -> 'Projector':
        """
        Get the shared projector instance.
        :return: the shared projector instance
        """
        return Projector._instance

    @staticmethod
    def project(geometry: Geometry,
                preferred_spatial_reference: SpatialReference or int = None,
                fallback_spatial_reference: SpatialReference or int = 3857) -> Geometry:
        """
        Project a geometry.
        :param geometry: the original geometry
        :param preferred_spatial_reference: the preferred spatial reference (If no preferred spatial reference is
        supplied, the projector will attempt to select an appropriate metric projection.)
        :param fallback_spatial_reference: the fallback spatial reference (if your preferred spatial reference isn't
        available)
        :return: the projected geometry
        """
        # Do a sanity check on the original geometry.
        if geometry is None:
            raise TypeError("The 'geometry' argument cannot be None.")
        # Before we do any additional work, let's see if we can simply meet the request by returning the original
        # geometry.
        if (geometry.spatial_reference.is_projected  # If it's already projected...
                and geometry.spatial_reference.is_metric  # ...and metric...
                and preferred_spatial_reference is None):  # ...and no other spatial reference is preferred...
            # ...we can just return the original geometry
            return geometry

        # Figure out the fallback spatial reference.  (We may need it shortly.)
        _fallback_sr: SpatialReference = None
        # If a fallback spatial reference was supplied...
        if fallback_spatial_reference is not None:
            # ...let's make sure it is actually a spatial reference.
            _fallback_sr = (
                fallback_spatial_reference if isinstance(fallback_spatial_reference, SpatialReference)
                else SpatialReference(fallback_spatial_reference)
            )

        # If no spatial reference is preferred...
        if preferred_spatial_reference is None:
            try:
                # Try to apply default logic.
                return geometry.transform_to_utm()
            except (GeometryException, SpatialReferenceException):
                # Didn't work eh?  Well, let's check the fallback spatial reference to make sure it meets the
                # criteria.
                if not fallback_spatial_reference.is_projected:  # Not projected?
                    raise SpatialReferenceException(
                        'No preferred spatial reference was supplied and the fallback is not projected.'
                    )
                elif not fallback_spatial_reference.is_metric:  # Not metric?
                    raise SpatialReferenceException(
                        'No preferred spatial reference was supplied and the fallback is not metric.'
                    )
                else:
                    # It looks like we can use the fallback.
                    return geometry.transform(spatial_reference=fallback_spatial_reference)
        else:
            # Create a variable to hold whatever we determine the target spatial reference will be.
            _pref_sr: SpatialReference = None

            # If a preferred spatial reference was supplied...
            if preferred_spatial_reference is not None:
                # ...let's make sure it is actually a spatial reference.
                _pref_sr = (
                    preferred_spatial_reference if isinstance(preferred_spatial_reference, SpatialReference)
                    else SpatialReference(preferred_spatial_reference)
                )
            # Before doing more work, let's check: Is the preferred spatial reference the same as the geometry's
            # current spatial reference, and if so...
            if preferred_spatial_reference.srid == geometry.spatial_reference.srid:
                return geometry
            else:
                try:
                    # Try to perform the transformation to the preferred spatial reference.
                    return geometry.transform(spatial_reference=preferred_spatial_reference)
                except (GeometryException, SpatialReferenceException):
                    # Didn't work eh?  Well, let's check the fallback spatial reference to make sure it meets the
                    # criteria.
                    if not fallback_spatial_reference.is_projected:  # Not projected?
                        raise SpatialReferenceException(
                            'No preferred spatial reference was supplied and the fallback is not projected.'
                        )
                    elif not fallback_spatial_reference.is_metric:  # Not metric?
                        raise SpatialReferenceException(
                            'No preferred spatial reference was supplied and the fallback is not metric.'
                        )
                    else:
                        # It looks like we can use the fallback.
                        return geometry.transform(spatial_reference=fallback_spatial_reference)


# Set the default projector instance.
Projector.set_instance(Projector())


# TODO: Break proto-geometries out into another module!


class ProtoGeometry(object):
    """
    Use a proto-geometry build up a new geometry from individual coordinates.
    """

    def __init__(self,
                 spatial_reference: SpatialReference or int = 4326,
                 projector: Projector = None):
        self._projector = projector if projector is not None else Projector.get_instance()
        self._spatial_reference = (
            spatial_reference if isinstance(spatial_reference, SpatialReference)
            else SpatialReference(srid=spatial_reference)
        )  # the proto-geometry's spatial reference
        self._exterior: List[PointTuple] = []  #: the exterior points
        self._interiors: List['ProtoGeometry'] = []  #: the interior rings  #TODO: Deal with interiors.

    def clear(self):
        """
        Clear the current contents.
        """
        self._exterior = []
        self._interiors = []

    def add(self, p: Point or PointTuple or LatLonTuple):
        """
        Add a point to the prototype's exterior
        :param p: the new coordinate you want to add
        """
        pt: PointTuple = self._conform(p)
        tup = (pt.x, pt.y, pt.z) if pt.z is not None else (pt.x, pt.y)
        self._exterior.append(tup)

    def _conform(self, p: Point or PointTuple or LatLonTuple) -> PointTuple:
        """
        Make sure a given point, point tuple, or lat/lon tuple conforms to the other point tuples in this
        proto-geometry.
        :param p: the original coordinate
        :return: either the original coordinate, or a new :py:class:`PointTuple` that conforms to this geometry
        """
        # Check the simplest case before we do anything else.
        if isinstance(p, PointTuple) and self._spatial_reference.is_same_as(p.srid):
            return p
        # OK. One way or the other, we're going to have to take the original value and convert it to a Point.
        pt: Point = None
        if isinstance(p, PointTuple):
            pt = Point.from_point_tuple(p)
        elif isinstance(p, LatLonTuple):
            pt = Point.from_latlon_tuple(p)
        elif isinstance(p, Point):
            pt = p
        else:
            # What?  None of the conditions above matched?!
            raise TypeError("Unsupported type: {type}.".format(type=type(p)))
        # If our Point is already in the correct spatial reference...
        if self._spatial_reference.is_same_as(pt.spatial_reference):
            return pt.to_point_tuple()
        else:
            # Otherwise we need to project it first.
            pt_proj: Point = pt.project(self._spatial_reference)
            # Now we can return it.
            return pt_proj.to_point_tuple()

    def to_polyline(self) -> Polyline:
        """
        Create a :py:class:`Polyline` from the contents of this proto-geometry.
        :return: the :py:class:`Polyline`
        """
        if len(self._exterior) == 0:
            raise GeometryException('The collection is empty.')
        _shapely = LineString(self._exterior)
        # noinspection PyTypeChecker
        return Geometry.from_shapely(shapely_geometry=_shapely, spatial_reference=self._spatial_reference)

    def to_polygon(self) -> Polygon:
        """
        Create a :py:class:`Polygon` from the contents of this proto-geometry.
        :return: the :py:class:`Polygon`
        """
        if len(self._exterior) == 0:
            raise GeometryException('The collection is empty.')
        _shapely = ShapelyPolygon(self._exterior)
        # noinspection PyTypeChecker
        return Geometry.from_shapely(shapely_geometry=_shapely, spatial_reference=self._spatial_reference)

