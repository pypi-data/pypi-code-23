
import copy

import pandas as pd
import itertools as it

from timeit import default_timer as timer
from IPython.display import display, Markdown

from ._calendar import calendar as cal
from ._util import Util
from .response_rotb_compute_strategy_components import ResponseRotbComputeStrategyComponents


LIMIT_SPLIT_REQUEST = 500


class RequestRotbComputeStrategyComponents:
    """
    """

    def __init__(self,
                 dic=None,
                 date_fallback_next=True,
                 limit_split=LIMIT_SPLIT_REQUEST):
        """
        """
        dic_url = {'base_url': 'https://analytics-api.sgmarkets.com',
                   'service': '/rotb',
                   'endpoint': '/v1/compute-strategy/components'}
        self.url = Util.build_url(dic_url)

        if dic:
            for k, v in dic.items():
                if not (isinstance(v, int) or isinstance(v, str)):
                    print(
                        'param {} (={}) is not either a string or a number'.format(k, v))
                setattr(self, k, v)
        self.dic_input = None
        self.dic_api = None
        self.li_dic_api = None
        self.df_top = None
        self.df_leg = None
        
        self.date_fallback_next = date_fallback_next
        self.limit_split = limit_split

        self.leg_keys = [
            'curve',
            'expiry',
            'tenor',
            'strike',
            'nominal',
            'type',
            'settlement',
            'pricingStrategy',
            'strategyWeight',
            'customEntries',
        ]

    def _to_list(self, val):
        """
        """
        if isinstance(val, int):
            return [val]
        elif ',' not in val:
            return [val]
        else:
            li_val = val.split(',')
            li_val = [e.strip() for e in li_val]
            return li_val

    def expand(self):
        """
        """
        dic_in = copy.copy(self.__dict__)
        for key in ['dic_input',
                    'dic_api',
                    'leg_keys',
                    'df_top',
                    'df_leg',
                    'li_dic_api',
                    'url',
                    'date_fallback_next',
                    'limit_split',
                    ]:
            dic_in.pop(key)

        # build dic as a prelude to dic_api
        self.dic_input = {}
        for k, v in dic_in.items():
            if k in self.leg_keys:
                # make params in leg to list
                self.dic_input[k] = self._to_list(v)
            else:
                # top params unchanged
                self.dic_input[k] = v

        # check dates are not holidays - if holiday fallback to next/previous
        li_date = self.dic_input.get('dates', None)
        if li_date:
            func = cal.get_BD_fallback_next if self.date_fallback_next else cal.get_BD_fallback_previous
            li_date_new = []
            dic_diff = {}
            for d in li_date:
                d_new = Util.date_to_str(func(d))
                li_date_new.append(d_new)
                if d_new != d:
                    dic_diff[d] = d_new
            if dic_diff:
                msg = '**<span style="color:red;">WARNING</span> -** These dates were modified as they are holidays:\n{}'
                msg = msg.format(str(dic_diff))
                display(Markdown(msg))
            self.dic_input['dates'] = li_date

        # cartesian product of all params in leg
        items = [(k, v)
                 for k, v in self.dic_input.items() if k in self.leg_keys]
        keys = [e[0] for e in items]
        values = [e[1] for e in items]

        li_leg = [dict(zip(keys, e)) for e in it.product(*values)]

        # merge top params and params in legs expanded by cartesian product
        self.dic_api = {k: v
                        for k, v in self.dic_input.items() if not k in self.leg_keys}
        self.dic_api['swaptions'] = li_leg

        dic_top = {k: str(v)
                   for k, v in self.dic_api.items() if k != 'swaptions'}
        self.df_top = pd.DataFrame(dic_top, index=['Value']).T

        self.df_leg = pd.DataFrame(li_leg)

        # Alert on large number of requests - potential timeout
        n_leg = len(li_leg)

        li_date = self.dic_input.get('dates', None)
        if not li_date:
            try:
                li_date = Util.get_list_bday_between(self.dic_input['startDate'],
                                                     self.dic_input['endDate'])
            except Exception as e:
                msg = 'error: {}'.format(e.args[0])
                raise Exception(msg)

        n_date = len(li_date)
        n_total = n_leg * n_date

        msg = '**<span style="color:black;">INFO</span> -** Your request contains {} prices over {} dates i.e. total {} prices.'
        msg = msg.format(n_leg, n_date, n_total)
        display(Markdown(msg))

        if n_leg > self.limit_split:
            msg = '**<span style="color:red;">WARNING</span> -** Your request is probably too large. The API may timeout.\nIt is recommended to request up to ~{} prices per date.'
            msg = msg.format(self.limit_split)
            display(Markdown(msg))

        max_nb_date_per_chunk = max(1, int(1.0 * self.limit_split / n_leg))
        self.li_dic_api = self._split_input_by_dates(li_date,
                                                     max_nb_date_per_chunk,
                                                     li_leg)

    def _split_input_by_dates(self,
                              li_date,
                              chunk_size,
                              li_leg):
        """
        """
        # print('---')
        # print(li_date)
        # print(chunk_size)
        # # print(li_leg)
        # print('---')

        li_date_chunk = [li_date[i:i + chunk_size]
                         for i in range(0, len(li_date), chunk_size)]

        if len(li_date_chunk) > 1:
            msg = '**<span style="color:red;">WARNING</span> -** Your request will be split in {} chunks to avoid API timeout.'
            msg = msg.format(len(li_date_chunk))
            display(Markdown(msg))

        li_dic_api = []
        for date_chunk in li_date_chunk:
            dic_api_chunk = {k: v
                             for k, v in self.dic_input.items() if not k in self.leg_keys}

            # Special case: nominal only in first leg in weighting = DV01
            li_leg_chunk = copy.deepcopy(li_leg)
            if self.dic_input['weighting'] == 'DV01':
                for leg in li_leg_chunk[1:]:
                    # print(leg)
                    leg.pop('nominal')

            # Build dic_api_chunk
            dic_api_chunk = {k: v
                             for k, v in self.dic_input.items() if not k in self.leg_keys}
            dic_api_chunk['swaptions'] = li_leg_chunk

            # Special case dates
            if 'startDate' in dic_api_chunk:
                dic_api_chunk['startDate'] = Util.date_to_str(date_chunk[0])
            if 'endDate' in dic_api_chunk:
                dic_api_chunk['endDate'] = Util.date_to_str(date_chunk[-1])
            # if 'dates' in dic_api_chunk:
            #     print(date_chunk)
            #     # dic_api_chunk['dates'] = [Util.date_to_str(d) for d in date_chunk]
            #     dic_api_chunk['dates'] = date_chunk
            #     print(dic_api_chunk['dates'])

            li_dic_api.append(dic_api_chunk)

        return li_dic_api

    # def _repr_html_(self):
    #     """
    #     """
    #     pass

    def info(self):
        """
        """
        md = """
A RequestROTB object has the properties after the `expand()` method:
+ `url`: {}
+ `dic_input`: user input (dictionary)
+ `df_top`: parameters of the request not in a leg (dataframe)
+ `df_leg`: parameters of the request in a leg (dataframe)
    + A leg contains the following parameters: {}
    + Each param can have multiple comma separated values 
+ `li_dic_api`: data ready to be sent to the API - built from user input by `expand()` (list of dictionaries)
    + This is a list because the request may be split in several chunks
    + Legs are constructed from user input by [cartesian product](https://en.wikipedia.org/wiki/Cartesian_product)
        """.format(self.url, str(self.leg_keys))
        return Markdown(md)

    def call_api(self,
                 api,
                 debug=False):
        """
        See https://analytics-api.sgmarkets.com/rotb/swagger/ui/index#!/Swaption/Swaption_StrategyComponents
        """
        t0 = timer()
        print('calling API...')
        li_raw_response = []
        for k, dic_api in enumerate(self.li_dic_api):

            raw_response = api.post(self.url,
                                    payload=dic_api)
            if debug:
                print('chunk {} raw response\n{}'.format(k, raw_response))
            li_raw_response.append(raw_response)
            t1 = timer()
            print('chunk {}/{} done in {:.2f} s'.format(1 + k,
                                                        len(self.li_dic_api),
                                                        t1 - t0))
        if debug:
            print('*** START DEBUG ***\n{}\n*** END DEBUG ***'.format(li_raw_response))
        response = ResponseRotbComputeStrategyComponents(li_raw_data=li_raw_response,
                                                         obj_req=self)
        return response

        # return li_raw_response
