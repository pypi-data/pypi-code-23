#!/usr/bin/python

# Haversine formula example in Python
# Author: Wayne Dyck

import math

def distance(origin, destination):
  lat1, lon1 = origin
  lat2, lon2 = destination
  radius = 6371000 # m

  dlat = math.radians(lat2-lat1)
  dlon = math.radians(lon2-lon1)
  a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
      * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
  c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
  d = radius * c

  return d


# TODO - Improve method - faster, better result (lat_distance and lon_distance lower)
def latLonFromCentLatLon(centlat, centlon, nnxp,  nnyp, deltax, deltay):

    dist_y = nnyp * deltay
    dist_x = nnxp * deltax

    lat_distance = 0

    while lat_distance < 90:
        lat_distance += 0.05
        lat_up = centlat + lat_distance
        lat_down = centlat - lat_distance

        lon_distance = 0
        while lon_distance < 90:
            lon_distance += 0.05
            lon_left = centlon - lon_distance
            lon_right = centlon + lon_distance

            lon_dist = distance((lat_up, lon_left), (lat_up, lon_right))
            lat_dist = distance((lat_up, lon_left), (lat_down, lon_left))

            if lat_dist >= dist_y and lon_dist >= dist_x:
                return lat_up, lat_down, lon_left, lon_right

