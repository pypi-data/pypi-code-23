#!/usr/bin/env python
from ryanair.Dates import duration,cfg
import json
import datetime
import requests
import pandas as pd
from dateutil import parser
import os

class Ryanair():

    def __init__(self):
        self.arrivalairports = cfg['airports']['arrivalairports']
        self.departureairports = cfg['airports']['departureairports']

    def to_excel(self,df,outputfile):
        # To prevent having to rerun the script due to open excelfile. Works on Windows OS only.
        try:
            df.to_excel(outputfile, index=False)
        except PermissionError:
            solve = input('Permission Error, force close Excel? Y/N\n')
            if solve.upper() == 'Y':
                os.system('taskkill /f /im excel.exe')
                df.to_excel(outputfile, index=False)
    
    def request(self,departure, arrival, datein, dateout,returnflight=False):
        url = "https://api.ryanair.com/farefinder/3/oneWayFares?&departureAirportIataCode={0}&arrivalAirportIataCode={1}&language=en&limit=5000&market=en-gb&offset=0&outboundDepartureDateFrom={2}&outboundDepartureDateTo={3}".format(departure,arrival,datein,dateout)
        r = requests.get(url)
        j = json.loads(r.content)

        for fare in j['fares']:
            self.flightdict[fare['outbound']['departureDate']] ={
                 'Dep_country{0}'.format(self.keyword): fare['outbound']['departureAirport']['countryName'],
                 'Dep_airport{0}'.format(self.keyword): fare['outbound']['departureAirport']['name'],
                 "Origin{0}".format(self.keyword) : fare['outbound']['departureAirport']['iataCode'],
                 'Departure{0}'.format(self.keyword): parser.parse(fare['outbound']['departureDate']),
    
                 'Arrival{0}'.format(self.keyword): parser.parse(fare['outbound']['arrivalDate']),
                 'Dest_country{0}'.format(self.keyword): fare['outbound']['arrivalAirport']['countryName'],
                 'Dest_airport{0}'.format(self.keyword): fare['outbound']['arrivalAirport']['name'],
                 'Destination{0}'.format(self.keyword): fare['outbound']['arrivalAirport']['iataCode'],
    
                'Price{0}'.format(self.keyword) : fare['outbound']['price']['value']}

    def flights(self,dates,outputfile,returnflight=False):
        self.flightdict = {}

        if returnflight == True:
            print('Searching for return flights')
            self.keyword = '_Return'
            self.departureairports,self.arrivalairports = self.arrivalairports,self.departureairports
        else:
            print('Searching for departure flights')
            self.keyword = ''

        for date in dates:
            for i in range(0, len(self.departureairports)):
                for j in range(0, len(self.arrivalairports)):
                    month = '{:02d}'.format(date.month)
                    day = '{:02d}'.format(date.day)
                    self.request(self.departureairports[i], self.arrivalairports[j], '{0!s}-{1!s}-{2!s}'.format(date.year,month,day), '{0!s}-{1!s}-{2!s}'.format(date.year,month,day,returnflight))
            print('Found {0} flights so far'.format(len(self.flightdict)))
        if len(self.flightdict) == 0:
            print('No flights found')
        else:
            df = pd.DataFrame.from_dict(self.flightdict, orient='index').sort_values(by='Price{0}'.format(self.keyword), ascending=True)
            self.to_excel(df,outputfile)
            print('\n\n')
        return self.flightdict

    def roundflights(self,departureflight,returnflight,outputfile):
        print('Searching for round flights')
        combidict = {}
        for key, value in departureflight.items():
            for key2, value2 in returnflight.items():
                if value['Destination'] == value2['Origin_Return']:
                    for item in duration:
                        if (parser.parse(key).date() + datetime.timedelta(days=item)) == parser.parse(key2).date():
                            combidict[key + '__' + key2] = pd.concat(
                                [pd.DataFrame.from_dict(departureflight[key], orient='index'),
                                 pd.DataFrame.from_dict(returnflight[key2], orient='index')]).T
                            combidict[key + '__' + key2]['Retour_price'] = value2['Price_Return'] + value['Price']
                            combidict[key + '__' + key2]['Duration_of_stay'] = value2['Arrival_Return'] - value[
                                'Arrival']
                            combidict[key + '__' + key2]['Price_per_hour'] = combidict[key + '__' + key2][
                                                                                 'Retour_price'] / (((value2[
                                                                                                          'Arrival_Return'] -
                                                                                                      value[
                                                                                                          'Arrival']).days) * 24) + (
                                                                                         ((value2['Arrival_Return'] -
                                                                                           value[
                                                                                               'Arrival']).seconds) / 3600)
        if len(combidict) == 0:
            print('No round flight found, check your settings/dates')
        else:
            df = (pd.concat(combidict.values(), ignore_index=True).sort_values('Retour_price'))
            df = df.drop(columns=['Dep_country_Return', 'Dep_airport_Return', 'Dest_country_Return','Origin_Return'])


            self.to_excel(df, outputfile)
            print('Found {0} round flights!'.format(len(df)))
        return combidict

