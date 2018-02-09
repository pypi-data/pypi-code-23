import os
import sys

import pytempus
from pytempus import *

# symbols from this file + symbols from pytempus
__all__ = ['load_plugin', 'load_graph', 'request'] + \
          ['Base',
           'Cost',
           'IsochroneValue',
           'MMEdge',
           'MMVertex',
           'Multimodal',
           'POI',
           'Plugin',
           'PluginFactory',
           'PluginRequest',
           'Point2D',
           'Point3D',
           'ProgressionCallback',
           'PublicTransport',
           'Request',
           'ResultElement',
           'Road',
           'Roadmap',
           'RoadmapIterator',
           'RoutingData',
           'TextProgression',
           'TransportMode',
           'TransportModeEngine',
           'TransportModeId',
           'TransportModeRouteType',
           'TransportModeSpeedRule',
           'TransportModeTollRule',
           'TransportModeTrafficRule',
           'cost_name',
           'cost_unit',
           'distance',
           'distance2',
           'edge',
           'get_total_costs',
           'init',
           'load_routing_data']

if sys.platform.startswith('linux'):
    TEMPUS_PLUGINS_DIR = os.getenv('TEMPUS_PLUGINS_DIR', '/usr/local/lib/tempus')
    TEMPUS_PLUGIN_PREFIX = os.getenv('TEMPUS_PLUGIN_PREFIX', 'lib')
    TEMPUS_PLUGIN_SUFFIX = os.getenv('TEMPUS_PLUGIN_SUFFIX', '.so')
elif sys.platform == 'win32':
    TEMPUS_PLUGINS_DIR = os.getenv('TEMPUS_PLUGINS_DIR', 'C:\\OSGEO4W64\\apps\\tempus\\bin')
    TEMPUS_PLUGIN_PREFIX = os.getenv('TEMPUS_PLUGIN_PREFIX', '')
    TEMPUS_PLUGIN_SUFFIX = os.getenv('TEMPUS_PLUGIN_SUFFIX', '.dll')

def load_plugin(options, plugin_name=None, plugin_path=None):
    if plugin_name is None and plugin_path is None:
        raise RuntimeError("You should provide either a plugin name or a plugin path")
    if isinstance(options, str):
        # str => treated as db options
        options = {'db/options': options}
    
    pr = pytempus.TextProgression(50)
    if plugin_name is not None:
        return pytempus.PluginFactory.instance().create_plugin( \
            os.path.join(TEMPUS_PLUGINS_DIR, \
                         TEMPUS_PLUGIN_PREFIX + plugin_name + TEMPUS_PLUGIN_SUFFIX), \
            pr, options)
    if plugin_path is not None:
        return pytempus.PluginFactory.instance().create_plugin( \
                                                              plugin_path,
                                                              pr, options)

def load_graph(options, graph_type="multimodal_graph"):
    pr = pytempus.TextProgression(50)
    return pytempus.load_routing_data(graph_type, pr, options)

class ResultWrapper:
    def __init__(self, plugin_request, results):
        self.results_ = results
        self.metrics = plugin_request.metrics()

    def __getitem__(self, key):
        return self.results_[key]

    def __len__(self):
        return len(self.results_)

def request(
        plugin,
        plugin_options=None,
        origin=None,
        steps=None,
        destination=None,
        allowed_transport_modes=None,  # at least pedestrian
        criteria=None,  # list of optimizing criteria
        parking_location=None,
        networks=None  # public transport network id
        ):
    req = pytempus.Request()
    req.origin = origin
    if destination is not None:
        req.destination = destination

    if steps:
        for step in steps[:-1]:
            req.add_intermediary_step(step)
        req.set_destination_step(steps[-1])

    for mode in allowed_transport_modes:
        req.add_allowed_mode(mode)
    for criterion in criteria:
        req.add_criterion(criterion)
    r = plugin.request(plugin_options)

    return ResultWrapper(r, r.process(req))
