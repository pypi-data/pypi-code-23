import arrow
import requests


import urllib2

class SimpleDataCollector():
    '''This one does nto allow conversion to Panda Dataframes!'''
    DATA_URL = 'https://data.chaienergy.net/data/{uid}/{stream_type}/?{params}'

    def __init__(self, uid, stream_type):
        uid = urllib2.quote(uid)
        self.uid = uid
        self.stream_type = stream_type

    def get_data(self, starttime = None, endtime = None, 
                 deltatime=None,
                 health = False,
                 stats= False,
                 interval = None,
                 show_interval = None,
                 aggregate = None,
                 timezone = None,
                 compress = None):
        
        params = self.format_params(starttime, endtime, deltatime, health, stats, interval, show_interval, aggregate, timezone, compress=compress)

        url = self.DATA_URL.format(uid = self.uid, stream_type = self.stream_type, params = params)

        meta = self.send_query(url = url)
        data = meta.pop('data')
        
        if len(data) == 0:
            return [], None # we override it to not error out!
            raise ValueError('No data was found!')

        return data, meta

    def format_params(self, starttime = None, endtime = None, 
                deltatime = None,
                 health = False,
                 stats= False,
                 interval = None,
                 show_interval = None,
                 aggregate = 'hour',
                 timezone = None,
                 compress = None):
        params = {}
        
        if deltatime is not None and starttime is None and endtime is None:
            starttime = arrow.utcnow().timestamp - int(deltatime)
            endtime   = arrow.utcnow().timestamp
        
        if starttime is not None:
            params['starttime'] = arrow.get(starttime).timestamp 
            
        if endtime is not None:
            params['endtime'] = arrow.get(endtime).timestamp 
        
        
        
        
        params['health'] = str(health).lower()
        params['stats'] = str(stats).lower()
        
        if interval != None:
            params['interval'] = str(int(interval))
            
        if show_interval != None:
            params['show_interval'] = 'true'
        
        if aggregate != None:
            params['aggregate'] = aggregate

        if timezone != None:
            params['timezone'] = timezone
            
        if compress != None:
            params['compress'] = int(compress)
        
        params['show_data'] = 'true'
        params['format'] = 'json'
    
    
        mystr = ''
        for i, v in params.iteritems():
            mystr += i + '=' + str(v) +'&'
    
        return mystr
    
    def send_query(self, url):
        response = requests.get(url = url)
        if response.status_code != 200:
            raise ValueError('There was a problem fetching the data: ' + url)
        
        return response.json()
if __name__ == '__main__':
#     dc = DataCollector(uid = '1520 PRINCETON ST #1 SANTA MONICA CA 90404', stream_type = 3)
    dc = DataCollector(uid = 'SCE_62GT4UZIX', stream_type = 3)
    d, f = dc.get_data(starttime = 1470517200, endtime = 1472432400, convert_to_df = True, aggregate = 'hour')
    
    print(d)
    print(f)
    

    