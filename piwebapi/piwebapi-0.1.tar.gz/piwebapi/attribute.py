from .piobject import PIObject
from .config import webapi_server
import pandas as pd
from dateutil import parser


class Attribute(PIObject):

    def __init__(self, path, persistence=None):

        if isinstance(path, str):
            if "https" not in path:
                response = self.request("attributes", {"path": path}, persistence)
            else:
                response = self.request(path, {}, persistence)
        else:
            response = path

        self.persistence = persistence

        self.response = response
        self.name = response["Name"]
        self.web_id = response["WebId"]
        self.links = response["Links"]
        self.description = response["Description"]
        self.units = response["DefaultUnitsName"]
        self.config_string = response["ConfigString"]

        self._children = None


    def keys(self):
        return self.children.keys()

    def __iter__(self):
        return iter(self.children)

    def items(self):
        return self.children.items()

    def iteritems(self):
        return self.children.iteritems()

    def __getitem__(self, name):

        if name not in self.children.keys():
            raise KeyError("Attribute not found")

        return self.children[name]

    def set_value(self, value):
        url = webapi_server + 'attributes/' + self.web_id + '/value'
        payload = {'Value': value}
        self.put(url, payload).text

    def set_config_string(self, configstring):
        url = webapi_server + 'attributes/' + self.web_id
        payload = {'ConfigString': configstring}
        self.patch(url, payload).text

    def add_attribute(self, name, description=None, attribute_type=None, **kwargs):
        url = webapi_server + 'attributes/' + self.web_id + '/attributes'

        payload = {
                "Name": name,
                "Description": description,
                "Type": attribute_type,
                }
        for key in kwargs:
            payload[key.title().replace("_", "")] = kwargs[key]

        self._attributes = None
        response = self.post(url, payload)
        try:
            return Attribute(path=response.headers['location'])
        except:
            raise ValueError(response.text)

    def get_summary(self, start_time="*-1H", end_time="*", duration="10m", interval="1m", summary_type="range", filter_expression="", persistence=0):

        if(("*" in start_time or "*" in end_time) and persistence > 0):
            raise ValueError("Cannot use persistence with queries referring to now (*)")

        payload = {"startTime":start_time,
                 "endTime":end_time, 
                 "summaryType": summary_type, 
                 "summaryDuration": duration, 
                 "sampleInterval": interval,
                 "sampleType": "Interval",
                 "calculationBasis": "EventWeighted",
                 #"filterExpression": filter_expression
                }

        response = self.request(self.links["SummaryData"],payload, 0)
        return self._to_pandas(response)

    @property
    def children(self):
        if not self._children:

            self._children = {}

            children = self.request(self.links["Attributes"], {}, self.persistence)
            for child in children["Items"]:
                self._children[child["Name"]] = Attribute(child)

        return self._children

    @property
    def value(self):
        response = self.request(self.links["Value"], {}, persistence=self.persistence)
        return response["Value"]

    # non-cached value, for use in softsensors
    @property
    def actual_value(self):
        response = self.request(self.links["Value"], {}, persistence=0)
        return response["Value"]


    def get_recorded(self, start_time="*-1H", end_time="*", max_count=1000, boundary_type='Inside', persistence=0):

        if(("*" in start_time or "*" in end_time) and persistence > 0):
            raise ValueError("Cannot use persistence with queries referring to now (*)")

        response = self.request(self.links["RecordedData"],{"startTime":start_time,"endTime":end_time, "maxCount": max_count, "boundaryType": boundary_type},persistence)
        return self._to_pandas(response)

    def get_value(self, time='*', persistence=0):
        response = self.request(self.links["Value"], {"time": time}, persistence)
        return pd.Series([self._extract_value(response)], index=[parser.parse(response["Timestamp"])])

    def _to_pandas(self, response):
        timestamps = []
        values = []
        for value in response["Items"]:
            if "Timestamp" in value.keys():
                time = parser.parse(value["Timestamp"])
            else:
                time = parser.parse(value["Value"]["Timestamp"])
            timestamps.append(time)
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
