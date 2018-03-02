import json
import math
import sys
from operator import itemgetter

MAX_LONGITUDE = 180.0
MIN_LONGITUDE = -180.0
MAX_LATITUDE = 90.0
MIN_LATITUDE = -90.0
EARTH_RADIUS_KM = 6371.0

DEFAULT_MAX_DISTANCE_KM = 100.0
DEFAULT_OFFICE_COORDINATES = {"latitude": 53.339428, 'longitude': -6.257664}


def create(inputfile, office_coordinates=None, max_distance_km=None):
    '''
    Function which takes file of json encoded customer data, and returns a
    list of customers which live within a certain distance of the companies
    office.

    inputfile: file of json encoded customer information, e.g.:
    {"latitude": 53.3381985, 'longitude': -6.2592576,
     "user_id": 0, "name": "Intercom Office"}

    office_coordinates (optional): dict containing location of the companies
    office. default: {"latitude": 53.3381985, 'longitude': -6.2592576}

    max_distance_km (optional): the maximum distance in kilometres an employee
    can be from the office and still be invited to the party. Must
    be greater than zero. default: 100.0

    returns: list of customer dicts, in acsending order by user_id
    '''

    # checks parameters are valid
    office_coordinates, max_distance_km = check_optional_parameters(
                                            office_coordinates,
                                            max_distance_km)

    # reads in data file, parses each line, and stores in customer list
    customers = read_customer_data_file(inputfile)

    # finds customers within max_distance
    guests = get_guests_within_distance(customers, office_coordinates,
                                        max_distance_km)

    # returns guest list sorted by user id
    return sorted(guests, key=itemgetter('user_id'))


def check_optional_parameters(office_coordinates, max_distance_km):
    '''
    This function checks the optional arguments, raises exception if invalid
    '''

    if office_coordinates is not None:
        coordinates_valid = check_if_coordinates_valid(office_coordinates)
        if not coordinates_valid:
            raise ValueError('office_coordinates argument invalid,\n' +
                             'Should be a dict containing latitude and ' +
                             'longitude values in range:\n' +
                             '(-180.0 <= longitude <= 180.0),' +
                             '(-90.0 <= latitude <= 90.0)')
    else:
        office_coordinates = DEFAULT_OFFICE_COORDINATES

    if max_distance_km is not None:
        distance_valid = check_if_distance_valid(max_distance_km)
        if not distance_valid:
            raise ValueError('max_distance_km must be an int or' +
                             'a float greater than zero')
    else:
        max_distance_km = DEFAULT_MAX_DISTANCE_KM

    return office_coordinates, max_distance_km


def read_customer_data_file(inputfile):
    '''
    This function reads in data file and returns list
    of customer dicts
    '''

    customers = []

    with open(inputfile) as data_file:
        for line in data_file.readlines():
            try:
                customer = json.loads(line)

            # ignores any lines of data which are invalid json
            except json.JSONDecodeError as e:
                print("{} on line: {}".format(e.msg, line), file=sys.stderr)
                continue

            coordinates_valid = check_if_coordinates_valid(customer)

            # ignores json object which does not contain valid coordinates
            if coordinates_valid:
                customer['latitude'] = float(customer['latitude'])
                customer['longitude'] = float(customer['longitude'])
                customers.append(customer)
            else:
                print("Invalid coordinates on line: {}".format(line),
                      file=sys.stderr)

    return customers


def get_guests_within_distance(customers, office_coordinates, max_distance_km):
    '''
    This function checks customer list and returns list of those
    within max distance of the office
    '''

    guests = []

    for customer in customers:
        distance = great_circle_distance_km(office_coordinates, customer)

        if distance <= max_distance_km:
            # stores distance in customer object, to be used by test suite
            customer['distance'] = distance
            guests.append(customer)

    return guests


def great_circle_distance_km(c1, c2):
    '''
    This function takes in two dicts containing latitude and longitude values
    and returns the distance between them in kilometres.

    c1,c2: dict containing values for longitude and latitude in decimal degrees

    This is reproduced from the spherical law of cosines based algorithm given
    in the wikipedia entry:
    https://en.wikipedia.org/wiki/Great-circle_distance?section=1#Formulas

    Due to the Earth not being a perfect sphere,
    this formula is correct within about 0.5%
    '''

    c1_lat_radians = math.radians(c1["latitude"])
    c2_lat_radians = math.radians(c2["latitude"])
    c1_lon_radians = math.radians(c1["longitude"])
    c2_lon_radians = math.radians(c2["longitude"])

    sin_lat_product = math.sin(c1_lat_radians) * math.sin(c2_lat_radians)
    cos_lat_product = math.cos(c1_lat_radians) * math.cos(c2_lat_radians)

    absoulte_diff_longitude = math.fabs(c1_lon_radians - c2_lon_radians)
    cos_abs_diff = math.cos(absoulte_diff_longitude)

    central_angle = math.acos(sin_lat_product + cos_lat_product * cos_abs_diff)
    return EARTH_RADIUS_KM * central_angle


def check_if_coordinates_valid(coordinates):
    '''
    Function to check if coordinates are valid.
    coordinates: dict containing a latitude and longitude value.
    Longitude range:  -180.0 -> 180.0 (inclusive)
    Latitude range:  -90.0 -> 90.0 (inclusive)
    '''

    # checks if longitude is valid
    if 'longitude' in coordinates:
        try:
            longitude = float(coordinates['longitude'])
        except:
            return False

        if longitude >= MIN_LONGITUDE and longitude <= MAX_LONGITUDE:
            pass
        else:
            return False
    else:
        return False

    # checks if latitude is valid
    if 'latitude' in coordinates:
        try:
            latitude = float(coordinates['latitude'])
        except:
            return False

        if latitude >= MIN_LATITUDE and latitude <= MAX_LATITUDE:
            pass
        else:
            return False
    else:
        return False

    return True


def check_if_distance_valid(max_distance_km):
    '''
    Function to check if the max_distance_km is valid
    max_distance_km: distance in kilometers
    '''

    if isinstance(max_distance_km, float) or isinstance(max_distance_km, int):
        if max_distance_km > 0.0:
            return True
    return False
