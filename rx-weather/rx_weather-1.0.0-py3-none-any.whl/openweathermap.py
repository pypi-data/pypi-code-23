import funcy
import typing
from typing import Any
import requests
import rx
import pdb
from rxw.models import *


def default_unit(key: str) -> Unit:
    """
    given a json key, returns the unit for that key's
    corresponding measurement
    """
    units = {
        'temp': Unit(Unit.degree_symbol()+"C"),
        'deg': Unit(Unit.degree_symbol()),
        'speed': Unit('m/sec'),
        'presssure': Unit('hPa'),
        'humidity': Unit('%'),
        }
    return units[key] if key in units else None


class CurrentConditions:
    """ class to handle communications with OpenWeatherMap """

    host = 'api.openweathermap.org'

    def __init__(self, api_key: str):
        self.api_key = api_key

    def show_for(self, zip: str, temp_only: bool=False):
        self.rx_fetch(zip) \
                .flat_map(lambda js, _: self.parse_weather(js)) \
                .subscribe(
                    on_next=lambda w: w.display(temp_only),
                    on_error=lambda e: self._handle_error(e)        
                )

    def rx_fetch(self, zip: str) -> rx.Observable:
        """
        creates an and returns obsersable on the
        current conditions api request
        """
        url = "http://"+self.host+'/data/2.5/weather'
        
        def observable(observer):
            params = {'zip': zip, 'appid': self.api_key}
            rsp = requests.get(url, params=params)

            try:
                rsp.raise_for_status()
                observer.on_next(rsp.json())
                observer.on_completed()
            except requests.HTTPError as e:
                observer.on_error(e)
            return lambda: None

        return rx.Observable.create(observable)

    def parse_weather(self, json: dict) -> WeatherForecast:
        """ 
        extract the various weather readings from the json
        blob and return a WeatherForecast object 
        """        
        def observable(observer):
            try:
                if len(json) == 0:
                    raise(Exception('No Weather Data'))
                
                location = Location(id=json['id'])
                location.name = json['name']
                
                if 'sys' in json:
                    sys = json['sys']
                    location.country = sys['country']
                    sunrise = SolarTimes.utc_to_localdatetime(sys['sunrise'])
                    sunset = SolarTimes.utc_to_localdatetime(sys['sunset'])
                    location.solar = SolarTimes(sunrise, sunset)
                else:
                    raise Exception("Weather data invalid, missing 'sys'")
                
                weather = WeatherForecast(location)        
                if 'coord' in json:
                    lat = json['coord']['lat']
                    lon = json['coord']['lon']
                    weather.location.geo_location = GeoPoint(lat, lon)
                if 'main' not in json:
                    raise Exception("Weather data invalid, missing 'main'")
                    
                main = json['main']
                cc = ClimateCondition()
                cc.temperature = Measurement(
                    main['temp'], 
                    default_unit('temp'))
                cc.humidity = Measurement(
                    main['humidity'], 
                    default_unit('humidity'))
                if 'wind' in json:
                    wind = json['wind']
                    speed = Measurement(wind['speed'], default_unit('speed'))
                    dir = Measurement(wind['deg'], default_unit('deg'))
                    cc.wind = Vector(speed, dir)
            
                if 'weather' in json:
                    ps = json['weather']
                    params = [Parameter(p['main'], p['description']) 
                                for p in ps]
                    cc.conditions = params                                        
                    
                weather.current = cc
                
            except Exception as e:
                observer.on_error(e)
            else:
                observer.on_next(weather) 
            finally:
                return lambda: None
        return rx.Observable.create(observable)
                
    def _handle_error(self, e: Exception): 
        """ display an error message """
        if type(e) is requests.HTTPError:
            if e.response.status_code == 404:
                print("Unable to find weather at the location specified")
            else:
                print("Network error " + e.response.reason)
        else:
            print(str(e))
