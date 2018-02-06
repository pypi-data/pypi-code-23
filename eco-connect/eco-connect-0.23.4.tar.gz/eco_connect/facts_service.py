from collections import namedtuple
from operator import attrgetter

import pandas as pd


from eco_connect.src.base_request import BaseRequest
from eco_connect.src.request_parser import RequestParser
from eco_connect.src.errors import RequestParserError


class FactsService(BaseRequest):
    """A class to connect to Ecorithm's facts-service api
    (https://facts.prod.ecorithm.com/api/v1/).

        **Args**:

        **Kwargs**:
           **environment_name** (str): Api environment. Supported environments
           ('Prod', 'Qa')

                *Example*: 'prod'

           **version** (str): Api version. Supported versions: ('v1')

                *Example*: 'v1'
    """

    def __init__(self, environment_name='prod', version='v1'):
        self.env = self._validate_env(environment_name=environment_name)
        if environment_name == 'dev':
            self.hostname = 'http://127.0.0.1:5000/api/v1/'
        else:
            self.hostname = (f'https://facts.{self.env}.'
                             f'ecorithm.com/api/{version}/')
        super().__init__()

    def get_facts(self,
                  building_id,
                  start_date,
                  end_date,
                  start_hour='00:00',
                  end_hour='23:55',
                  equipment_names=[],
                  equipment_types=[],
                  excluded_days=[],
                  excluded_dates=[],
                  point_classes=[],
                  eco_point_ids=[],
                  display_names=[],
                  native_names=[],
                  point_class_expression=[],
                  native_name_expression=[],
                  display_name_expression=[],
                  result_format='pandas'):
        """Return the sensor facts for a building.

        API documentation: http://facts.prod.ecorithm.com/api/v1/#/Facts/Facts_get

        **Args**:

           **building_id** (str):  Building id to get facts for.

                *Example*: 1

           **start_date** (str):  Start date to return facts for.

                *Example*: '2017-12-20 00:00'

           **end_date** (str):  End date to return facts for.

                *Example*: '2017-12-21 23:55'

        **Kwargs**:

           **start_hour** (str): Start hour to filter facts for.

                *Example*: '08:00'

           **end_hour** (str): End hour to filter facts for.

                *Example*: '17:00'

           **excluded_days** (list): Specific days to filter data for.
           Monday=1, Sunday=7

                *Example*: [6, 7]  (Filters Saturday / Sunday)

           **excluded_dates** (list): Specific dates to filter data for.

                *Example*: ['2017-12-20', '2017-12-25']

           **equipment_names** (list):  List of equipment names to filter facts
           for.

                *Example*: ['VAV_01', 'VAV_02']

           **equipment_types** (list):  List of equipment types to filter facts
           for.

                *Example*: ['VAV', 'AHU']

           **point_classes** (list):  List of point_classes to filter facts
           for.

                *Example*: ['SpaceAirTemperature', 'CoolingCoilUnitFeedback']

           **eco_point_ids** (list):  List of eco_point_ids to filter facts
           for.

                *Example*: [1, 2, 3]

           **display_names** (list):  List of display_names to filter facts
           for.

                *Example*: ['SpaceTemp', 'AirFlow']

           **native_names** (list):  List of native_names to filter facts
           for.

                *Example*: ['name-1', 'name-2']

           **point_class_expression** (list):  List of equipment / equipment type +
           point class regex expressions to filter facts. Equipment / equipment
           type and point class regex expressions are space delimited.
           for.

                *Example*: ['VAV.* SpaceAirTemperature', 'AHU Space.*']

           **native_name_expression** (list):  List of native-name regex
           expressions to filter facts.

                *Example*: ['nam.*', 'nati-.*']

           **display_name_expression** (list): List of equipment / equipment type +
           display name regex expressions to filter facts. Equipment /
           equipment type and point class regex expressions are space
           delimited.

                *Example*: ['VAV.* SpaceAirTemperature', 'AHU Space.*']

           **result_format** (str): Output format type. (Pandas, tuple, csv,
           json)

                *Example*: 'pandas'



        **Returns**:
           (DataFrame or list or csv or json depending on the requested
           result format).

        *DataFrame Example*::

            index     fact_time       fact_value  eco_point_id  display_name   native_name          point_class         equipment_name  equipment_type
            =====  ================   ==========  ============  ============   ===========  ==========================  ==============  ==============
            0      2017-12-20 00:00       1            192       'SpaceTemp'     'name-1'    'SpaceAirTemperature'         'VAV-01'        'VAV'
            1      2017-12-21 00:00       2            304       'CoolingCoil'   'name-2'    'CoolingCoilUnitFeedback'     'AHU-01'        'AHU'


        *Json Example*::

            {
              "data": [
                {
                  "87238": {
                    "data": {
                      "2017-08-01 00:00": 67.5,
                      "2017-08-01 00:05": 68.5
                    },
                    "meta": {
                      "display_name": "SpaceTemp",
                      "eco_point_id": 85743,
                      "native_name": "UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T",
                      "equipment": "VAV-301",
                      "equipment_type": "VAV",
                      "point_class": "SpaceAirTemperature"
                    }
                  },
                  "87239": {
                    "data": {
                      "2017-08-01 00:00": 0,
                      "2017-08-01 00:05": 100
                    },
                    "meta": {
                      "display_name": "Cooling",
                      "eco_point_id": 87239,
                      "native_name": "UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.CV",
                      "equipment": "VAV_301",
                      "equipment_type": "VAV",
                      "point_class": "CoolingCoilUnitFeedback"
                    }
                  }
                }
              ]
            }


        *Csv Example*::

                ',fact_time,fact_value,point_class,display_name,native_name,
                equipment_type,equipment_name,eco_point_id


                0,2017-12-20 00:05,70.1923,SpaceAirTemperature,SpaceTemp,
                UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T,VAV,VAV_301,85743,


                2017-12-20 00:05,76.08,SpaceAirTemperatureSetPointWhenCooling,
                SpaceTempSetPoint_ActualCooling,
                UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET,VAV,VAV_301,
                85744,

                2017-12-20 00:05,70.08,
                SpaceAirTemperatureSetPointWhenHeating,
                SpaceTempSetPoint_ActualHeating,
                UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.AHTG-SET,VAV,VAV_301,85745'


        *Tuple Example*::

            [response_tuple(fact_time='2017-12-20 00:05', fact_value=70.1923,
                            point_class='SpaceAirTemperature', display_name='SpaceTemp',
                            native_name='UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T',
                            equipment_type='VAV', equipment_name='VAV_301', eco_point_id=85743),
             response_tuple(fact_time='2017-12-20 00:05', fact_value=76.08,
                            point_class='SpaceAirTemperatureSetPointWhenCooling',
                            display_name='SpaceTempSetPoint_ActualCooling',
                            native_name='UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET',
                            equipment_type='VAV', equipment_name='VAV_301', eco_point_id=85744)]

        .. note::
           And invalid api request will return back the raw api response.

           *Example*:
            {"message": {"NoData": "No data found for the provided filters.
            This building has data from '2017-12-20 00:00'
            to '2017-12-21 00:00'"}}


    **Example Usage:**

    >>> from eco_connect import FactsService
    >>> facts_service = FactsService()
    >>> facts_service.get_facts(building_id=26,
                                start_date='2017-12-20 00:00',
                                end_date='2017-12-21 00:00',
                                result_format='json')
        {
          "data": [
            {
              "87238": {
                "data": {
                  "2017-08-01 00:00": 67.5,
                  "2017-08-01 00:05": 68.5
                },
                "meta": {
                  "display_name": "SpaceTemp",
                  "eco_point_id": 85743,
                  "native_name": "UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T",
                  "equipment": "VAV-301",
                  "equipment_type": "VAV",
                  "point_class": "SpaceAirTemperature"
                }
              },
              "87239": {
                "data": {
                  "2017-08-01 00:00": 0,
                  "2017-08-01 00:05": 100
                },
                "meta": {
                  "display_name": "Cooling",
                  "eco_point_id": 87239,
                  "native_name": "UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.CV",
                  "equipment": "VAV_301",
                  "equipment_type": "VAV",
                  "point_class": "CoolingCoilUnitFeedback"
                }
              }
            }
          ]
        }

        """

        url = self.hostname + f'building/{building_id}/facts'

        data = {
            'start_date': start_date,
            'end_date': end_date,
            'start_hour': start_hour,
            'end_hour': end_hour,
            'excluded_dates': excluded_dates,
            'excluded_days': excluded_days,
            'eco_point_ids': eco_point_ids,
            'equipment_names': equipment_names,
            'equipment_types': equipment_types,
            'point_classes': point_classes,
            'display_names': display_names,
            'native_names': native_names,
            'point_class_expression': point_class_expression,
            'display_name_expression': display_name_expression,
            'native_name_expression': native_name_expression}

        if result_format.lower() == 'pandas':
            parser_args = {'data_key': 'data'}
            fact_parser = self._pandas_fact_parser
        elif result_format.lower() == 'json':
            fact_parser = RequestParser.json_parser
            parser_args = {}
        elif result_format.lower() == 'tuple':
            fact_parser = self._tuple_fact_parser
            parser_args = {'data_key': 'data'}
        elif result_format.lower() == 'csv':
            fact_parser = self._csv_fact_parser
            parser_args = {'data_key': 'data'}
        else:
            raise ValueError(f'{result_format} is not valid!')

        response = self.post(url, data=data)

        return self._format_response(response, fact_parser, parser_args)

    def _tuple_fact_parser(self, response, data_key='data'):
        try:
            result = response.json()
        except (ValueError):
            raise RequestParserError('Unable to parse the response.',
                                     response.text)

        result = result[data_key]

        tuple_names = ['fact_time', 'fact_value'] +\
            list(list(result.values())[0]['meta'].keys())

        response_tuple = namedtuple('response_tuple', tuple_names)
        parsed_result = []
        for dpoint_id, data in result.items():
            meta = data['meta']
            fact_data = data['data']
            for fact_time, fact_value in fact_data.items():
                row = {'fact_time': fact_time, 'fact_value': fact_value}
                row.update(meta)
                parsed_result.append(response_tuple(**row))
        return sorted(parsed_result, key=attrgetter('eco_point_id'))

    def _pandas_fact_parser(self, response, data_key='data'):
        tuple_response = self._tuple_fact_parser(response, data_key)
        return pd.DataFrame(tuple_response)

    def _csv_fact_parser(self, response, data_key='data'):
        result_df = self._pandas_fact_parser(response, data_key)
        return result_df.to_csv()

    def put_facts(self, building_id, data=pd.DataFrame(columns=['fact_time',
                                                                'fact_value',
                                                                'native_name']
                                                       )):
        """Insert facts for a building.

        API documentation: http://facts.prod.ecorithm.com/api/v1/#/Facts/put

        **Args**:

           **building_id** (str):  Building id to get facts for.

                *Example*: 1

           **data** (DataFrame): DataFrame with data to upload.

                *Example*::

                    index     fact_time       fact_value   native-name
                    =====  ================   ==========  =============
                    0      2017-12-20 00:00       1       native-name-1
                    1      2017-12-21 00:00       2       native-name-2


        .. note::
           If errors are present, a `message` key
           will be returned.

           *Example*:
            {
            'message': {'field_errors': ['native-name-1']}
            }


    **Example Usage:**

    >>> from eco_connect import FactsService
    >>> import pandas as pd
    >>> facts_service = FactsService()
    >>> data = pd.DataFrame(data=[['2017-12-20 00:00', 1, 'native-name-1'],
                                  ['2017-12-21 00:00', 2, 'native-name-2']],
                            columns=['fact_time', 'fact_value', 'native_name'])
    >>> fs.put_facts(building_id=26, data=data)
        {'data': {'building_id': 26,
                  'max_process_timestamp': '2017-12-21 00:00',
                  'min_process_timestamp': '2017-12-21 00:00',
                  'records_stored': 1},
         'message': {'field_errors': ['native-name-1']}}
"""

        url = self.hostname + f'building/{building_id}/facts'
        col_1 = data.columns[0]
        col_2 = data.columns[1]
        col_3 = data.columns[2]
        input_data = [{col_1: row[0], col_2: row[1], col_3: row[2]}
                      for row in data.values]

        response = self.put(url, data=input_data, encode_type='json')
        parser = self._get_parser(result_format='json')
        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_avg_facts(self,
                      building_id,
                      start_date,
                      end_date,
                      start_hour='00:00',
                      end_hour='23:55',
                      period='day',
                      equipment_names=[],
                      equipment_types=[],
                      excluded_days=[],
                      excluded_dates=[],
                      point_classes=[],
                      eco_point_ids=[],
                      display_names=[],
                      native_names=[],
                      point_class_expression=[],
                      native_name_expression=[],
                      display_name_expression=[],
                      result_format='pandas'):
        """Return the average sensor facts for a building.

        API documentation: http://facts.prod.ecorithm.com/api/v1/#/Facts/get_avg

        **Args**:

           **building_id** (str):  Building id to get facts for.

                *Example*: 1

           **start_date** (str):  Start date to return facts for.

                *Example*: '2017-12-20 00:00'

           **end_date** (str):  End date to return facts for.

                *Example*: '2017-12-21 23:55'

        **Kwargs**:

           **start_hour** (str): Start hour to filter facts for.

                *Example*: '08:00'

           **end_hour** (str): End hour to filter facts for.

                *Example*: '17:00'

           **excluded_days** (list): Specific days to filter data for.
           Monday=1, Sunday=7

                *Example*: [6, 7]  (Filters Saturday / Sunday)

           **excluded_dates** (list): Specific dates to filter data for.

                *Example*: ['2017-12-20', '2017-12-25']

           **equipment_names** (list):  List of equipment names to filter facts
           for.

                *Example*: ['VAV_01', 'VAV_02']

           **equipment_types** (list):  List of equipment types to filter facts
           for.

                *Example*: ['VAV', 'AHU']

           **point_classes** (list):  List of point_classes to filter facts
           for.

                *Example*: ['SpaceAirTemperature', 'CoolingCoilUnitFeedback']

           **eco_point_ids** (list):  List of eco_point_ids to filter facts
           for.

                *Example*: [1, 2, 3]

           **display_names** (list):  List of display_names to filter facts
           for.

                *Example*: ['SpaceTemp', 'AirFlow']

           **native_names** (list):  List of native_names to filter facts
           for.

                *Example*: ['name-1', 'name-2']

           **point_class_expression** (list):  List of equipment / equipment type +
           point class regex expressions to filter facts. Equipment / equipment
           type and point class regex expressions are space delimited.
           for.

                *Example*: ['VAV.* SpaceAirTemperature', 'AHU Space.*']

           **native_name_expression** (list):  List of native-name regex
           expressions to filter facts.

                *Example*: ['nam.*', 'nati-.*']

           **display_name_expression** (list): List of equipment / equipment type +
           display name regex expressions to filter facts. Equipment /
           equipment type and point class regex expressions are space
           delimited.

                *Example*: ['VAV.* SpaceAirTemperature', 'AHU Space.*']

           **period** (string): Aggregate period to average on. Supports the
           following aggregates [minute, hour, day, week, month, year]

                *Example*: 'hour'

                *Default*: 'day'

           **result_format** (str): Output format type. (Pandas, tuple, csv,
           json)

                *Example*: 'pandas'



        **Returns**:
           (DataFrame or list or csv or json depending on the requested
           result format).

        *DataFrame Example*::

            index     fact_time       fact_value  eco_point_id  display_name   native_name          point_class         equipment_name  equipment_type
            =====  ================   ==========  ============  ============   ===========  ==========================  ==============  ==============
            0      2017-12-20 00:00       1            192       'SpaceTemp'     'name-1'    'SpaceAirTemperature'         'VAV-01'        'VAV'
            1      2017-12-21 00:00       2            304       'CoolingCoil'   'name-2'    'CoolingCoilUnitFeedback'     'AHU-01'        'AHU'


        *Json Example*::

            {
              "data": [
                {
                  "87238": {
                    "data": {
                      "2017-08-01 00:00": 67.5,
                      "2017-08-01 00:05": 68.5
                    },
                    "meta": {
                      "display_name": "SpaceTemp",
                      "eco_point_id": 85743,
                      "native_name": "UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T",
                      "equipment": "VAV-301",
                      "equipment_type": "VAV",
                      "point_class": "SpaceAirTemperature"
                    }
                  },
                  "87239": {
                    "data": {
                      "2017-08-01 00:00": 0,
                      "2017-08-01 00:05": 100
                    },
                    "meta": {
                      "display_name": "Cooling",
                      "eco_point_id": 87239,
                      "native_name": "UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.CV",
                      "equipment": "VAV_301",
                      "equipment_type": "VAV",
                      "point_class": "CoolingCoilUnitFeedback"
                    }
                  }
                }
              ]
            }


        *Csv Example*::

                ',fact_time,fact_value,point_class,display_name,native_name,
                equipment_type,equipment_name,eco_point_id


                0,2017-12-20 00:05,70.1923,SpaceAirTemperature,SpaceTemp,
                UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T,VAV,VAV_301,85743,


                2017-12-20 00:05,76.08,SpaceAirTemperatureSetPointWhenCooling,
                SpaceTempSetPoint_ActualCooling,
                UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET,VAV,VAV_301,
                85744,

                2017-12-20 00:05,70.08,
                SpaceAirTemperatureSetPointWhenHeating,
                SpaceTempSetPoint_ActualHeating,
                UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.AHTG-SET,VAV,VAV_301,85745'


        *Tuple Example*::

            [response_tuple(fact_time='2017-12-20 00:05', fact_value=70.1923,
                            point_class='SpaceAirTemperature', display_name='SpaceTemp',
                            native_name='UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T',
                            equipment_type='VAV', equipment_name='VAV_301', eco_point_id=85743),
             response_tuple(fact_time='2017-12-20 00:05', fact_value=76.08,
                            point_class='SpaceAirTemperatureSetPointWhenCooling',
                            display_name='SpaceTempSetPoint_ActualCooling',
                            native_name='UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET',
                            equipment_type='VAV', equipment_name='VAV_301', eco_point_id=85744)]

        .. note::
           And invalid api request will return back the raw api response.

           *Example*:
            {"message": {"NoData": "No data found for the provided filters.
            This building has data from '2017-12-20 00:00'
            to '2017-12-21 00:00'"}}


    **Example Usage:**

    >>> from eco_connect import FactsService
    >>> facts_service = FactsService()
    >>> facts_service.get_avg_facts(building_id=26,
                                    start_date='2017-12-20 00:00',
                                    end_date='2017-12-21 00:00',
                                    period='minute',
                                    result_format='json')
        {
          "data": [
            {
              "87238": {
                "data": {
                  "2017-08-01 00:00": 67.5,
                  "2017-08-01 00:05": 68.5
                },
                "meta": {
                  "display_name": "SpaceTemp",
                  "eco_point_id": 85743,
                  "native_name": "UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T",
                  "equipment": "VAV-301",
                  "equipment_type": "VAV",
                  "point_class": "SpaceAirTemperature"
                }
              },
              "87239": {
                "data": {
                  "2017-08-01 00:00": 0,
                  "2017-08-01 00:05": 100
                },
                "meta": {
                  "display_name": "Cooling",
                  "eco_point_id": 87239,
                  "native_name": "UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.CV",
                  "equipment": "VAV_301",
                  "equipment_type": "VAV",
                  "point_class": "CoolingCoilUnitFeedback"
                }
              }
            }
          ]
        }

        """

        url = self.hostname + f'building/{building_id}/avg-facts'
        data = {
            'start_date': start_date,
            'end_date': end_date,
            'start_hour': start_hour,
            'end_hour': end_hour,
            'excluded_days': excluded_days,
            'excluded_dates': excluded_dates,
            'period': period,
            'eco_point_ids': eco_point_ids,
            'equipment_names': equipment_names,
            'equipment_types': equipment_types,
            'point_classes': point_classes,
            'display_names': display_names,
            'native_names': native_names,
            'point_class_expression': point_class_expression,
            'display_name_expression': display_name_expression,
            'native_name_expression': native_name_expression}
        response = self.post(url, data=data)
        if result_format.lower() == 'pandas':
            parser_args = {'data_key': 'data'}
            fact_avg_parser = self._pandas_fact_parser
        elif result_format.lower() == 'json':
            fact_avg_parser = RequestParser.json_parser
            parser_args = {}
        elif result_format.lower() == 'tuple':
            fact_avg_parser = self._tuple_fact_parser
            parser_args = {'data_key': 'data'}
        elif result_format.lower() == 'csv':
            fact_avg_parser = self._csv_fact_parser
            parser_args = {'data_key': 'data'}
        else:
            raise ValueError(f'{result_format} is not valid!')

        parsed_result = self._format_response(response,
                                              parser=fact_avg_parser,
                                              parser_args=parser_args)
        return parsed_result

    def get_buildings(self, building_id=None,
                      is_active=True, result_format='pandas'):
        """Return the meta information for buildings."""
        url = self.hostname + f'buildings'
        params = {'building_id': building_id, 'is_active': is_active}
        response = self.get(url, data=params)
        parser = self._get_parser(result_format, data_key='data')

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def put_building(self, building, building_id=None, time_zone=None):
        result_format = 'json'
        url = self.hostname + f'buildings'
        payload = {'building_name': building,
                   'building_id': building_id,
                   'time_zone': time_zone}
        response = self.put(url, data=payload)
        parser = self._get_parser(result_format)
        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def delete_building(self, building_id):
        result_format = 'json'
        url = self.hostname + f'buildings'
        payload = {'building_id': building_id}
        response = self.delete(url, data=payload)
        parser = self._get_parser(result_format)
        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_point_classes(self, point_class=None,
                          is_active=True, result_format='pandas'):
        url = self.hostname + f'point-classes'
        params = {'point_class': point_class, 'is_active': is_active}
        response = self.get(url, data=params)
        parser = self._get_parser(result_format, data_key='data')

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def put_point_class(self, point_class, point_class_id=None):
        result_format = 'json'
        url = self.hostname + f'point-classes'
        payload = {'point_class_id': point_class_id,
                   'point_class': point_class}
        response = self.put(url, data=payload)
        parser = self._get_parser(result_format)
        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def delete_point_class(self, point_class):
        result_format = 'json'
        url = self.hostname + f'point-classes'
        payload = {'point_class': point_class}
        response = self.delete(url, data=payload)
        parser = self._get_parser(result_format)
        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_point_mapping(self,
                          building_id,
                          equipment_names=[],
                          equipment_types=[],
                          point_classes=[],
                          eco_point_ids=[],
                          display_names=[],
                          native_names=[],
                          point_class_expression=[],
                          native_name_expression=[],
                          display_name_expression=[],
                          is_active=True,
                          result_format='pandas'):
        """Return the point mapping for a building.

        API documentation:
        http://facts.prod.ecorithm.com/api/v1/#/Point-Mapping/point_mapping_get

        **Args**:

           **building_id** (str):  Building id to get facts for.

                *Example*: 1

        **Kwargs**:

           **equipment_names** (list):  List of equipment names to filter facts
           for.

                *Example*: ['VAV_01', 'VAV_02']

           **equipment_types** (list):  List of equipment types to filter facts
           for.

                *Example*: ['VAV', 'AHU']

           **point_classes** (list):  List of point_classes to filter facts
           for.

                *Example*: ['SpaceAirTemperature', 'CoolingCoilUnitFeedback']

           **eco_point_ids** (list):  List of eco_point_ids to filter facts
           for.

                *Example*: [1, 2, 3]

           **display_names** (list):  List of display_names to filter facts
           for.

                *Example*: ['SpaceTemp', 'AirFlow']

           **native_names** (list):  List of native_names to filter facts
           for.

                *Example*: ['name-1', 'name-2']

           **point_class_expression** (list):  List of equipment / equipment type +
           point class regex expressions to filter facts. Equipment / equipment
           type and point class regex expressions are space delimited.
           for.

                *Example*: ['VAV.* SpaceAirTemperature', 'AHU Space.*']

           **native_name_expression** (list):  List of native-name regex
           expressions to filter facts.

                *Example*: ['nam.*', 'nati-.*']

           **display_name_expression** (list): List of equipment / equipment type +
           display name regex expressions to filter facts. Equipment /
           equipment type and point class regex expressions are space
           delimited.

                *Example*: ['VAV.* SpaceAirTemperature', 'AHU Space.*']

           **is_active** (boolean):  Return the active / in-active native-names

                *Example*: True

           **result_format** (str): Output format type. (Pandas, tuple, csv,
           json)

                *Example*: 'pandas'


        **Returns**:
           (DataFrame or list or csv or json depending on the requested
           result format).

        *DataFrame Example*::

            index    eco_point_id     display_name   native_name        point_class           equipment_name   equipment_type        last_updated
            =====  ================   ============  ============  =========================   ==============  ================  =======================
            0            192          'SpaceTemp'     'name-1'    'SpaceAirTemperature'         'VAV-01'        'VAV'            "2017-12-07T19:04:18Z"

            1            304          'CoolingCoil'   'name-2'    'CoolingCoilUnitFeedback'     'AHU-01'        'AHU'            "2017-12-07T19:04:18Z"



        *Json Example*::

            {
              "data": [
                {
                  "equipment_name": "VAV_01",
                  "equipment_type": "VAV",
                  "native_name": "Native-Name-1",
                  "eco_point_id": 3,
                  "point_class": "SpaceAirTemperature",
                  "native_name_id": 1283,
                  "display_name": "SpaceTemp",
                  "last_updated": "2017-11-17T17:44:04Z"
                },
                {
                  "equipment_name": "VAV_02",
                  "equipment_type": "VAV",
                  "native_name": "Native-Name-1",
                  "eco_point_id": 4,
                  "point_class": "SpaceAirTemperature",
                  "native_name_id": 1283,
                  "display_name": "SpaceTemp",
                  "last_updated": "2017-11-17T17:44:04Z"
                }
              ]
            }

        *Csv Example*::

                'point_class,display_name,native_name,
                equipment_type,equipment_name,eco_point_id


                SpaceAirTemperature,SpaceTemp,
                UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T,VAV,VAV_301,85743,


                SpaceAirTemperatureSetPointWhenCooling,
                SpaceTempSetPoint_ActualCooling,
                UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET,VAV,VAV_301,
                85744,

                SpaceAirTemperatureSetPointWhenHeating,
                SpaceTempSetPoint_ActualHeating,
                UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.AHTG-SET,VAV,VAV_301,85745'


        *Tuple Example*::

            [response_tuple(point_class='SpaceAirTemperature', display_name='SpaceTemp',
                            native_name='UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T',
                            equipment_type='VAV', equipment_name='VAV_301', eco_point_id=85743),
             response_tuple(point_class='SpaceAirTemperatureSetPointWhenCooling',
                            display_name='SpaceTempSetPoint_ActualCooling',
                            native_name='UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET',
                            equipment_type='VAV', equipment_name='VAV_301', eco_point_id=85744)]

        .. note::
           And invalid api request will return back the raw api response.

           *Example*:
            {"message": {"NoData": "No data for provided parameters"}}


    **Example Usage:**

    >>> from eco_connect import FactsService
    >>> facts_service = FactsService()
    >>> facts_service.get_point_mapping(building_id=26,
                                        result_format='json')
            {
              "data": [
                {
                  "equipment_name": "VAV_01",
                  "equipment_type": "VAV",
                  "native_name": "Native-Name-1",
                  "eco_point_id": 3,
                  "point_class": "SpaceAirTemperature",
                  "native_name_id": 1283,
                  "display_name": "SpaceTemp",
                  "last_updated": "2017-11-17T17:44:04Z"
                },
                {
                  "equipment_name": "VAV_02",
                  "equipment_type": "VAV",
                  "native_name": "Native-Name-1",
                  "eco_point_id": 4,
                  "point_class": "SpaceAirTemperature",
                  "native_name_id": 1283,
                  "display_name": "SpaceTemp",
                  "last_updated": "2017-11-17T17:44:04Z"
                }
              ]
            }

        """
        url = self.hostname + f'building/{building_id}/point-mapping'
        data = {
            'is_active': is_active,
            'eco_point_id': ','.join(map(str, eco_point_ids)) or None,
            'equipment_name': ','.join(map(str, equipment_names)) or None,
            'equipment_type': ','.join(map(str, equipment_types)) or None,
            'point_class': ','.join(map(str, point_classes)) or None,
            'display_name': ','.join(map(str, display_names)) or None,
            'native_name': ','.join(map(str, native_names)) or None,
            'point_class_expression': ','.join(
                map(str, point_class_expression)) or None,
            'display_name_expression': ','.join(
                map(str, display_name_expression)) or None,
            'native_name_expression': ','.join(
                map(str, native_name_expression)) or None}
        response = self.get(url, data=data)
        parser = self._get_parser(result_format, data_key='data')

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def delete_point_mapping(self, building_id, eco_point_ids=[]):
        url = self.hostname + f'building/{building_id}/point-mapping'
        payload = {'eco_point_id': eco_point_ids}
        result_format = 'json'
        response = self.delete(url, data=payload, encode_type='form')
        parser = self._get_parser(result_format)
        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def put_point_mapping(self, building_id, point_mapping=pd.DataFrame()):
        url = self.hostname + f'building/{building_id}/point-mapping'
        input_data = list(point_mapping.T.to_dict().values())
        response = self.put(url, data=input_data, encode_type='json')
        parser = self._get_parser(result_format='json')
        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_equipment_types(self, equipment_type=None,
                            is_active=True, result_format='pandas'):
        url = self.hostname + f'equipment-types'
        params = {'equipment_type': equipment_type, 'is_active': is_active}
        response = self.get(url, data=params)
        parser = self._get_parser(result_format, data_key='data')

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def delete_equipment_type(self, equipment_type):
        url = self.hostname + f'equipment-types'
        result_format = 'json'
        params = {'equipment_type': equipment_type}
        response = self.delete(url, data=params, encode_type='form')
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def put_equipment_type(self, equipment_type, equipment_type_id=None):
        url = self.hostname + f'equipment-types'
        result_format = 'json'
        payload = {'equipment_type': equipment_type,
                   'equipment_type_id': equipment_type_id}
        response = self.put(url, data=payload, encode_type='form')
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_equipment(self, building_id, equipment_name=None,
                      equipment_type=None,
                      is_active=True, result_format='pandas'):
        """Return the equipments for a building.

        API documentation:
        http://facts.prod.ecorithm.com/api/v1/#/Equipment/equipment_get

        **Args**:

           **building_id** (str):  Building id to get facts for.

                *Example*: 1

        **Kwargs**:

           **equipment_name** (string):  Equipment name to filter on.

                *Example*: 'VAV_01'

           **equipment_type** (string):  equipment_type to filter on.

                *Example*: 'AHU'

           **is_active** (boolean):  Return the active / in-active native-names

                *Example*: True


           **result_format** (str): Output format type. (Pandas, tuple, csv,
           json)

                *Example*: 'pandas'


        **Returns**:
           (DataFrame or list or csv or json depending on the requested
           result format).

        *DataFrame Example*::

            index    equipment_id     equipment_type    equipment_name       last_updated
            =====  ================   ==============   ================   =====================
            0            192              'AHU'            'VAV-01'       '2017-12-07T19:04:18Z'
            1            304              'VAV'            'AHU-01'       '2017-12-07T19:04:18Z'


        *Json Example*::

            {'data': [{'equipment_id': 1092,
                       'equipment_name': 'AHU_G1',
                       'equipment_type': 'AHU',
                       'last_updated': '2017-12-07T19:04:18Z'},
                       {'equipment_id': 1093,
                        'equipment_name': 'AHU_G1_ExhaustFan',
                        'equipment_type': 'AHU',
                        'last_updated': '2017-12-07T19:04:18Z'}]
            }

        *Csv Example*::

                'equipment_id,equipment_type,equipment_name,last_updated


                1092,AHU,AHU_G1,2017-12-07T19:04:18Z


                1094,AHU,AHU_G1_ReturnFanVFD,2017-12-07T19:04:18Z


        *Tuple Example*::

            [response_tuple(equipment_id=1092, equipment_type='AHU',
                            equipment_name='AHU_G1',
                            last_updated='2017-12-07T19:04:18Z'),
             response_tuple(equipment_id=1093, equipment_type='AHU',
                            equipment_name='AHU_G1_ExhaustFan',
                            last_updated='2017-12-07T19:04:18Z')]

        .. note::
           And invalid api request will return back the raw api response.

           *Example*:
            {"message": {"NoData": "No data for provided parameters"}}


    **Example Usage:**

    >>> from eco_connect import FactsService
    >>> facts_service = FactsService()
    >>> facts_service.get_equipment(building_id=26,
                                    result_format='json')
            {'data': [{'equipment_id': 1092,
                       'equipment_name': 'AHU_G1',
                       'equipment_type': 'AHU',
                       'last_updated': '2017-12-07T19:04:18Z'},
                       {'equipment_id': 1093,
                        'equipment_name': 'AHU_G1_ExhaustFan',
                        'equipment_type': 'AHU',
                        'last_updated': '2017-12-07T19:04:18Z'}]
            }

        """
        url = self.hostname + f'building/{building_id}/equipment'
        params = {'equipment_type': equipment_type,
                  'is_active': is_active,
                  'equipment_name': equipment_name}
        response = self.get(url, data=params)
        parser = self._get_parser(result_format, data_key='data')

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def delete_equipment(self, building_id, equipments=[]):
        url = self.hostname + f'building/{building_id}/equipment'
        result_format = 'json'
        payload = {'equipment_name': equipments}
        response = self.delete(url, data=payload, encode_type='form')
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def put_equipment(self, building_id, equipments=pd.DataFrame()):
        url = self.hostname + f'building/{building_id}/equipment'
        result_format = 'json'
        input_data = list(equipments.T.to_dict().values())
        response = self.put(url, data=input_data, encode_type='json')
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_native_names(self, building_id,
                         native_name=None,
                         is_active=True, result_format='pandas'):
        """Return the native names for a building.

        API documentation:
        http://facts.prod.ecorithm.com/api/v1/#/Native-Names/native_names_get

        **Args**:

           **building_id** (str):  Building id to get facts for.

                *Example*: 1

        **Kwargs**:

           **native_name** (string):  Filter on this native_name

                *Example*: 'native-name-1'

           **is_active** (boolean):  Return the active / in-active native-names

                *Example*: True

           **result_format** (str): Output format type. (Pandas, tuple, csv,
           json)

                *Example*: 'pandas'


        **Returns**:
           (DataFrame or list or csv or json depending on the requested
           result format).

        *DataFrame Example*::

            index   native_name_id     native_name   native_name   expecting_data         origin       trend_period      last_updated
            =====  ================   ============  ============  ================   ==============  ================  ====================
            0            192          'name-1'        'name-1'          True            'CLIENT'        300 seconds    2017-12-19T20:36:36Z

            1            304          'name-2'        'name-2'          False          'ECORITHM'       300 seconds    2017-12-19T20:36:36Z



        *Json Example*::

            {'data': [{'expecting_data': True,
               'last_updated': '2017-12-19T20:36:36Z',
               'native_name': 'UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T',
               'native_name_id': 88826,
               'origin': 'CLIENT',
               'trend_period': '300 seconds',
               'trend_type': 'INTERVAL'},
              {'expecting_data': True,
               'last_updated': '2017-12-19T20:36:36Z',
               'native_name': 'UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET',
               'native_name_id': 88827,
               'origin': 'CLIENT',
               'trend_period': '300 seconds',
               'trend_type': 'INTERVAL'}
               }

        *Csv Example*::

                'native_name_id,native_name,expecting_data,
                origin,trend_type,trend_period,last_updated


                88826,UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T,
                True,CLIENT,INTERVAL,300 seconds,2017-12-19T20:36:36Z,

                88827,UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET,True,
                CLIENT,INTERVAL,300 seconds,2017-12-19T20:36:36Z'


        *Tuple Example*::

            [response_tuple(native_name_id=88826,
                            native_name='UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T',
                            expecting_data=True, origin='CLIENT',
                            trend_type='INTERVAL',
                            trend_period='300 seconds',
                            last_updated='2017-12-19T20:36:36Z'),
             response_tuple(native_name_id=88827,
                            native_name='UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET',
                            expecting_data=True, origin='CLIENT',
                            trend_type='INTERVAL',
                            trend_period='300 seconds',
                            last_updated='2017-12-19T20:36:36Z')

        .. note::
           And invalid api request will return back the raw api response.

           *Example*:
            {"message": {"NoData": "No data for provided parameters"}}


    **Example Usage:**

    >>> from eco_connect import FactsService
    >>> facts_service = FactsService()
    >>> facts_service.get_native_names(building_id=26,
                                       result_format='json')
            {'data': [{'expecting_data': True,
               'last_updated': '2017-12-19T20:36:36Z',
               'native_name': 'UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ZN-T',
               'native_name_id': 88826,
               'origin': 'CLIENT',
               'trend_period': '300 seconds',
               'trend_type': 'INTERVAL'},
              {'expecting_data': True,
               'last_updated': '2017-12-19T20:36:36Z',
               'native_name': 'UCSB/275/VAV_301/NAE11/N2-2.275-VAV-301.ACLG-SET',
               'native_name_id': 88827,
               'origin': 'CLIENT',
               'trend_period': '300 seconds',
               'trend_type': 'INTERVAL'}
               }

        """
        url = self.hostname + f'building/{building_id}/native-names'
        params = {'native_name': native_name,
                  'is_active': is_active}
        response = self.get(url, data=params)
        parser = self._get_parser(result_format, data_key='data')

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def put_native_names(self, building_id, native_names=pd.DataFrame()):
        url = self.hostname + f'building/{building_id}/native-names'
        result_format = 'json'
        input_data = list(native_names.T.to_dict().values())
        response = self.put(url, data=input_data, encode_type='json')
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def delete_native_names(self, building_id, native_names=[]):
        url = self.hostname + f'building/{building_id}/native-names'
        result_format = 'json'
        payload = {'native_name': native_names}
        response = self.delete(url, data=payload, encode_type='form')
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_native_names_history(self, building_id):
        url = self.hostname + f'building/{building_id}/native-name-history'
        result_format = 'json'
        response = self.get(url)
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_unmapped_native_names(self, building_id):
        url = self.hostname + f'building/{building_id}/unmapped-native-names'
        result_format = 'json'
        response = self.get(url)
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_etl_process_history(self, building_id, return_limit=None):
        url = self.hostname + f'building/{building_id}/etl-process-history'
        result_format = 'json'
        response = self.get(url, data={'return_limit': return_limit})
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_unstored_native_names(self, building_id):
        url = self.hostname + f'building/{building_id}/unstored-native-names'
        result_format = 'json'
        response = self.get(url)
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_last_native_name_record(self, building_id, native_name,
                                    max_time=None):
        url = self.hostname + f'building/{building_id}/last-native-name-record'
        result_format = 'json'
        response = self.get(url, data={'native_name': native_name,
                                       'max_time': max_time})
        parser = self._get_parser(result_format)

        parsed_result = self._format_response(response,
                                              **parser)
        return parsed_result

    def get_building_dqi(self, building_id, start_date, end_date,
                         dqi_aggregate='building_id', period='day',
                         native_name_expression='.*', result_format='pandas'):
        url = self.hostname + f'building/{building_id}/dqi'
        params = {'start_date': start_date,
                  'end_date': end_date,
                  'dqi_aggregate': dqi_aggregate,
                  'period': period,
                  'native_name_expression': native_name_expression}
        response = self.get(url, data=params)
        if result_format.lower() == 'pandas':
            parser_args = {'data_key': 'data'}
            dqi_parser = self._pandas_dqi_parser
        elif result_format.lower() == 'json':
            dqi_parser = RequestParser.json_parser
            parser_args = {}
        elif result_format.lower() == 'tuple':
            dqi_parser = self._tuple_dqi_parser
            parser_args = {'data_key': 'data'}
        elif result_format.lower() == 'csv':
            dqi_parser = self._csv_dqi_parser
            parser_args = {'data_key': 'data'}
        else:
            raise ValueError(f'{result_format} is not valid!')

        parsed_result = self._format_response(response,
                                              parser=dqi_parser,
                                              parser_args=parser_args)
        return parsed_result

    def _tuple_dqi_parser(self, response, data_key='data'):
        try:
            result = response.json()
        except (ValueError):
            raise RequestParserError('Unable to parse the response.',
                                     response.text)

        result = result[data_key]

        tuple_names = ['aggregate', 'timestamp', 'dqi']

        response_tuple = namedtuple('response_tuple', tuple_names)
        parsed_result = []
        for aggregate, data in result.items():
            for timestamp, dqi in data.items():
                row = {'timestamp': timestamp,
                       'dqi': dqi,
                       'aggregate': aggregate}
                parsed_result.append(response_tuple(**row))
        return sorted(parsed_result, key=attrgetter('aggregate'))

    def _pandas_dqi_parser(self, response, data_key='data'):
        parsed_tuples = self._tuple_dqi_parser(response, data_key)
        return pd.DataFrame(parsed_tuples)

    def _csv_dqi_parser(self, response, data_key='data'):
        parsed_df = self._pandas_dqi_parser(response, data_key)
        return parsed_df.to_csv(index=None)
