from .piobject import PIObject
from .config import webapi_server
import time
import re

import pandas as pd
from dateutil import parser
from datetime import datetime
import pytz

class Point(PIObject):

    def __init__(self, path=None, persistence=None):
        if "\\" in path:
            response = self.request("points", {"path": path}, persistence)
        elif "https" in path:
            response = self.request(path,{}, persistence)
        else:
            response = self.request("points/"+path,{}, persistence)
        # assign information
        self.web_id = response["WebId"]
        self.point_type = response["PointType"]
        self.name = response["Name"]
        self.links = response["Links"]
        self.persistence = persistence

        self._attributes = {}

    @property
    def units(self):
        return self.get_attributes()['engunits']

    @property
    def description(self):
        return self.get_attributes()['descriptor'] + " - " + self.get_attributes()['exdesc']

    @property
    def attributes(self):
        return self.get_attributes()

    def get_attributes(self):
        if self._attributes != {}:
            return self._attributes

        response = self.request(self.links["Attributes"], {}, self.persistence)

        for item in response['Items']:
            self._attributes[item['Name']] = item['Value']

        return self._attributes

    def get_value(self, time="*", persistence=0):
        response = self.request(self.links["Value"], {"time": time}, persistence)

        return pd.Series([self._extract_value(response)], index=[parser.parse(response["Timestamp"])])

    def get_recorded(self, start_time="*-1H", end_time="*", max_count=1000, boundary_type='Inside', persistence=0):

        if(("*" in start_time or "*" in end_time) and persistence > 0):
            raise ValueError("Cannot use persistence with queries referring to now (*)")

        response = self.request(self.links["RecordedData"],{"startTime":start_time,"endTime":end_time, "maxCount": max_count, "boundaryType": boundary_type},persistence)
        return self._to_pandas(response)

    def get_interpolated(self, start_time="*-1H", end_time="*", interval="1m", persistence=0):

        if(("*" in start_time or "*" in end_time) and persistence > 0):
            raise ValueError("Cannot use persistence with queries referring to now (*)")

        response = self.request(self.links["InterpolatedData"],{"startTime":start_time,"endTime":end_time,"interval":interval},persistence)
        return self._to_pandas(response)

    def get_summary(self, start_time="*-1H", end_time="*", interval="1m", summary_type="range", filter_expression="", persistence=0):

        if(("*" in start_time or "*" in end_time) and persistence > 0):
            raise ValueError("Cannot use persistence with queries referring to now (*)")

        payload = {"startTime":start_time,
                 "endTime":end_time, 
                 "summaryType": summary_type, 
                 "summaryDuration": interval, 
                 "calculationBasis": "EventWeighted",
                 "filterExpression": filter_expression
                }

        response = self.request(self.links["SummaryData"],payload, 0)
        return self._to_pandas(response)

    def write_value(self, value, timestamp="*"):
        url = webapi_server + 'streams/' + self.web_id + '/value'
        payload = {
                'Timestamp': timestamp,
                'Value': value
                }
        self.post(url, payload)

    def _to_pandas(self, response):
        timestamps = []
        values = []

        p = re.compile('[-T:]')

        for value in response["Items"]:
            if "Timestamp" in value.keys():
                tme = datetime(*map(int,p.split(value["Timestamp"])[:-1]))
            else:
                tme = datetime(*map(int,p.split(value["Value"]["Timestamp"])[:-1]))
            tme = pytz.utc.localize(tme)
            timestamps.append(tme)
            values.append(self._extract_value(value))
        series = pd.Series(values,index=timestamps).tz_convert(tz="Europe/Amsterdam")
        # convert to correct timezone
        return series



    def _extract_value(self, response):
        value = response["Value"]
        if isinstance(value, dict):
            if "Name" in value.keys():
                return value["Name"]
            else:
                return value["Value"]
        else:
            return value
