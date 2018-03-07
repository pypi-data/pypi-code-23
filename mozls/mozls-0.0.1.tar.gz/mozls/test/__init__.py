from math import radians, sin, cos, sqrt, atan2


def get_distance(point_a, point_b):
    R = 6373.0

    lat1 = radians(point_a[0])
    lon1 = radians(point_a[1])
    lat2 = radians(point_b[0])
    lon2 = radians(point_b[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance * 1000
