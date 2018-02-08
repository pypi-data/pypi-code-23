"""airports.py provides an example Steno3D project of airports"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np

from .base import BaseExample, exampleproperty
from ..point import Mesh0D, Point
from ..project import Project

DEG2RAD = np.pi/180
FT2KM = 12*2.54/100/1000
RADIUS = 6371


class Airports(BaseExample):
    """Class containing components of airport project. Components can be
    viewed individually or copied into new resources or projects with
    get_resources() and get_project(), respectively.
    """

    @exampleproperty
    def filenames(self):
        """airport files"""
        return ['airports.dat', 'latitude.npy', 'longitude.npy',
                'altitude.npy', 'license.txt']

    @exampleproperty
    def datafile(self):
        """full path to airport data file"""
        return Airports.fetch_data(filename='airports.dat',
                                   download_if_missing=False,
                                   verbose=False)

    @exampleproperty
    def latitude(self):
        """Airport lat, degrees, from openflights.org"""
        return np.load(Airports.fetch_data(filename='latitude.npy',
                                           download_if_missing=False,
                                           verbose=False))

    @exampleproperty
    def longitude(self):
        """Airport lon, degrees, from openflights.org"""
        return np.load(Airports.fetch_data(filename='longitude.npy',
                                           download_if_missing=False,
                                           verbose=False))

    @exampleproperty
    def altitude(self):
        """Airport alt, km, from openflights.org"""
        return np.load(Airports.fetch_data(filename='altitude.npy',
                                           download_if_missing=False,
                                           verbose=False))

    @classmethod
    def get_project(self):
        """return airport points project"""
        proj = Project(
            title='Airport',
            description='Project with airport points'
        )
        Point(
            project=proj,
            mesh=Mesh0D(
                vertices=np.c_[self.geo_to_xyz(self.latitude,
                                               self.longitude,
                                               self.altitude)]
            ),
            title='Airport Points'
        )
        return proj

    @staticmethod
    def geo_to_xyz(lat, lon, alt):
        """function geo_to_xyz

        Inputs:
            lat: latitude, degrees
            lon: longitude, degrees
            alt: altitude, km

        Outputs:
            x, y, z: spatial coordiantes relative to the center of the earth

        Note:
            This function assumes a shpherical earth
        """

        lat *= DEG2RAD
        lon *= DEG2RAD
        x = (RADIUS + alt)*np.cos(lat)*np.cos(lon)
        y = (RADIUS + alt)*np.cos(lat)*np.sin(lon)
        z = (RADIUS + alt)*np.sin(lat)

        return x, y, z

    @staticmethod
    def read_airports_data(filename):
        """Extract latitude, longitude, and altitude from file"""
        lat = []  # Latitude
        lon = []  # Longitude
        alt = []  # Altitude
        with open(filename) as f:
            for line in f:
                data = line.rstrip().split(',')
                lat.append(float(data[6])*DEG2RAD)
                lon.append(float(data[7])*DEG2RAD)
                alt.append(float(data[8])*FT2KM)
        return np.array(lat), np.array(lon), np.array(alt)
