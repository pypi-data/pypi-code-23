import typing
from typing import List, NewType, NamedTuple
from datetime import datetime
import pytz
import tzlocal


class Unit:
    """ defines a unit of measure, "km/h or degress C """

    @property
    def symbol(self) -> str:
        return self._symbol

    def __init__(self, sym: str):
        self._symbol = sym

    def __str__(self):
        return self.symbol

    @staticmethod
    def degree_symbol():
        """ return a degrees utf-8 character """
        return u'\N{DEGREE SIGN}'


Measurement = NamedTuple("Measurement",
                    [('value', float),
                     ('unit', Unit)])


GeoPoint = NamedTuple('GeoPoint',
                      [('lat', float),
                       ('lon', float)])


Parameter = NamedTuple('Parameter',
                       [('name', str),
                        ('description', str)])


Vector = NamedTuple('Vector',
                    [('magnitude', Measurement),
                     ('direction', Measurement)])


class SolarTimes:
    """ sunrise and sunset times """

    @property
    def sunrise(self) -> datetime:
        return self._sunrise

    @sunrise.setter
    def sunrise(self, new_value: datetime):
        self._sunrise = new_value

    @property
    def sunset(self) -> datetime:
        return self._sunset

    @sunset.setter
    def sunset(self, new_value: datetime):
        self._sunset = new_value

    @staticmethod
    def utc_to_localdatetime(timestamp: float) -> datetime:
        utc = datetime.utcfromtimestamp(timestamp)
        ltz = tzlocal.get_localzone()
        return utc.replace(tzinfo=pytz.utc).astimezone(ltz)
        
    def __init__(self, rise: datetime, set: datetime):
        self._sunrise = rise
        self._sunset = set


class Location:
    """ geographical weather area """

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_value: str):
        self._name = new_value

    @property
    def country(self) -> str:
        return self._country

    @country.setter
    def country(self, new_value: str):
        self._country = new_value

    @property
    def geo_location(self) -> GeoPoint:
        return self._geo

    @geo_location.setter
    def geo_location(self, geo: GeoPoint):
        self._geo = geo

    @property
    def solar(self) -> SolarTimes:
        return self._solar
        
    @solar.setter
    def solar(self, new_value: SolarTimes):
        self._solar = new_value

    def __init__(self, id: int):
        self.id = id

    def string_times(self) -> (datetime, datetime):
        rise = datetime.strftime(self.solar.sunrise, '%-I:%M%p')
        set = datetime.strftime(self.solar.sunset, '%-I:%M%p')
        return (rise, set)

    def __str__(self):
        str = "{0}, {1}\n".format(self.name, self.country)
        str += "lat: {0} lon: {1}\n".format(
            self.geo_location.lat, self.geo_location.lon)
        (rise, set) = self.string_times()
        str += "sunrise: {}\nsunset: {}".format(rise, set)
        return str


class ClimateCondition:
    """
    represents all the atttributes we care to display
    as weather
    """

    @property
    def temperature(self) -> Measurement:
        return self._temp

    @temperature.setter
    def temperature(self, new_value: Measurement):
        self._temp = new_value

    @property
    def humidity(self) -> Measurement:
        return self._humidity

    @humidity.setter
    def humidity(self, new_value: Measurement):
        self._humidity = new_value

    @property
    def wind(self) -> Vector:
        return self._wind

    @wind.setter
    def wind(self, new_value: Vector):
        self._wind = new_value

    @property
    def conditions(self) -> List[Parameter]:
        return self._conditions

    @conditions.setter
    def conditions(self, new_value: List[Parameter]):
        self._conditions = new_value

    def kelvin_to_farenheight(self, k: Measurement) -> Measurement:
        val = (k.value - 273.15) * 1.8 + 32.0
        return Measurement(val, Unit(Unit.degree_symbol()+"F"))

    def msec_to_mph(self, msec: Measurement) -> Measurement:
        val = msec.value * 2.236936
        return Measurement(val, Unit("mph"))

    def display_temp(self) -> str:
        tfar = self.kelvin_to_farenheight(self.temperature)
        str = "{0:.1f}{1}".format(tfar.value, tfar.unit)
        return str

    def __str__(self):
        str = "Temperature: {0}\n".format(self.display_temp())
        str += "Wind Speed:\n"
        mph = self.msec_to_mph(self.wind.magnitude)
        str += "\t{0:.1f}{1} at {2}{3}\n".format(mph.value, mph.unit,
            self.wind.direction.value, self.wind.direction.unit)
        str += "Conditions:\n\t"
        str += ",".join([p.description for p in self.conditions])
        return str


class WeatherForecast:
    """
    models a weather forecast. a forecast is basically
    just a series of climate conditions for a location on
    a specific date
    """
    @property
    def location(self) -> Location:
        return self._location

    @location.setter
    def location(self, new_value):
        self._location = new_value

    @property
    def current(self) -> ClimateCondition:
        return self._cur_condition

    @current.setter
    def current(self, new_value: ClimateCondition):
        self._cur_condition = new_value

    def __init__(self, location: Location):
        self.location = location

    def display(self, temp_only: bool=False):
        """ print myself """
        if temp_only:
            print("{0}: {1}\n".format(
                self.location.name, self.current.display_temp()))
            return
        print("{0}\n".format(self.location))
        print("{0}\n".format(self.current))

