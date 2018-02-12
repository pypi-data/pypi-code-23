from xbos import get_client
from xbos.services.pundat import DataClient, timestamp, make_dataframe
from xbos.services.hod import HodClientHTTP

import brick

c = get_client()
dc = DataClient(c)

uri = "ciee/devices/venstar/s.venstar/OpenSpace/i.xbos.thermostat"

brick.get_thermostat_triples(dc, uri)
