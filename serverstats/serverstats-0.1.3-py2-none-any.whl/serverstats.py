from time import sleep

import psutil
from deeputil import keeprunning
from basescript import BaseScript

def get_system_metrics():
    '''
    >>> from serverstats import get_system_metrics
    >>> 
    >>> fields = dict()
    >>> dl = get_system_metrics()
    >>> _fields = {'cpu': ['avg_load_5_min',
    ...                   'avg_load_15_min',
    ...                   'idle_percent',
    ...                   'iowait',
    ...                   'avg_load_1_min',
    ...                   'usage_percent'],
    ...           'disk': ['usage', 'total', 'free_percent', 'usage_percent', 'free'],
    ...           'ram': ['avail', 'usage_percent', 'avail_percent', 'usage', 'total', 'free'],
    ...           'swap': ['usage', 'total', 'free_percent', 'free', 'usage_percent']}
    >>> 
    >>> for key, value in dl.iteritems():
    ...     lst = list()
    ...     if type(value) is dict and key != 'network_traffic':
    ...         for t , c in value.iteritems():
    ...             lst.append(t)
    ...         fields[key] = lst
    ... 
    >>> _fields == fields
    True
    '''
    load1, load5, load15 = psutil.os.getloadavg()
    cpu_count = psutil.cpu_count()
    load_avg_15_min = (load15 / float(cpu_count) * 100)
    load_avg_5_min = (load5 / float(cpu_count) * 100)
    load_avg_1_min = (load1 / float(cpu_count) * 100)

    network_traffic_info = psutil.net_io_counters(pernic=True)
    cpu_stats = psutil.cpu_times()
    memory = psutil.virtual_memory()
    swap_mem = psutil.swap_memory()
    disk = psutil.disk_usage('/')

    if swap_mem.total == 0:
        swapmemory_free_percent = 0
    else:
        swapmemory_free_percent = (swap_mem.free / float(swap_mem.total) * 100)

    network_traffic = dict()
    for interface in network_traffic_info:
        network_traffic[interface] = {
            'sent': network_traffic_info[interface].bytes_sent,
            'received' : network_traffic_info[interface].bytes_recv
            }

    return dict(
        #load_avg info
        cpu=dict(
            usage_percent=load_avg_15_min,
            idle_percent=100.00 - load_avg_15_min,
            iowait=cpu_stats.iowait,
            avg_load_15_min=load15,
            avg_load_5_min=load_avg_5_min,
            avg_load_1_min=load_avg_1_min,
            ),

        #ram info
        ram=dict(
            total=memory.total,
            avail=memory.available,
            usage=memory.used,
            free=memory.free,
            usage_percent=memory.percent,
            avail_percent=(memory.available / float(memory.total) * 100)
            ),

        #swap memory info
        swap=dict(
            usage_percent=swap_mem.percent,
            free_percent=swapmemory_free_percent,
            total=swap_mem.total,
            usage=swap_mem.used,
            free=swap_mem.free,
            ),

        #disk info
        disk=dict(
            total=disk.total,
            usage=disk.used,
            free=disk.free,
            usage_percent=disk.percent,
            free_percent=(disk.free / float(disk.total) * 100),
            ),

        #network traffic
        network_traffic=network_traffic,
    )

class ServerStats(BaseScript):
    NAME = 'ServerStats'
    DESC = 'Collect important system metrics from a server and log them'

    def __init__(self):
        super(ServerStats, self).__init__()
        self.interval = self.args.interval

    def _log_exception(self, exp):
        self.log.exception('Error during run ', exp=exp)

    @keeprunning(on_error=_log_exception)
    def _log_system_metrics(self):
        self.log.info('system_metrics', type='metric', **get_system_metrics())
        sleep(self.interval)

    def define_args(self, parser):
        parser.add_argument('-n', '--interval', type=int, default=5, 
                            help='Seconds to wait after collection of stats')

    def run(self):
        self._log_system_metrics()

def main():
    ServerStats().start()

if __name__ == '__main__':
    main()
