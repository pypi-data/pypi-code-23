import os

# Files prefixes
import pkg_resources

PREFIX_RAW = "radio"
PREFIX_MERGE = "merge"
PREFIX_AVERAGE = "avg"
PREFIX_IMAGE = "img"
PREFIX_CONN_GOOD = "link-good"
PREFIX_CONN_UNBALANCED = "link-unbanlanced"
PREFIX_CONN_BAD = "link-bad"
PREFIX_STAB_GOOD = "stab-good"
PREFIX_STAB_UNBALANCED = "stab-unbalanced"
PREFIX_STAB_BAD = "stab-bad"

# Format strings
FORMAT_STRING = "{0}.{1}"
FORMAT_STRING_CH_TX = "{0}-ch{1:d}-tx{2:g}.{3}"
FORMAT_STRING_CH_TXNONE = "{0}-ch{1:d}-tx.{2}"
FORMAT_STRING_CH = "{0}-ch{1}.{2}"
FORMAT_STRING_TX = "{0}-tx{1:g}.{2}"
NOMINAL_CONFIG_FILE = os.path.join(os.path.dirname(__file__), "nominal_config.yaml")
METRIC_CHOICES = ['connectivity', 'pdr', 'rssi', 'lqi']
FIRMWARE_PATH = os.path.join('firmwares', 'radio_test_m3.elf')

###############################################################################
# APPLICATION CONFIGURATION

# Topology file for M3 nodes coordinates
# Received socket timeout in second



TOPOLOGY_RESOURCES_CLUSTER = os.path.join('topology', 'resources', '%s', 'cluster_m3.json')
TOPOLOGY_CLUSTER = pkg_resources.resource_filename('iotlab_radio_test',
                                                   TOPOLOGY_RESOURCES_CLUSTER)
TOPOLOGY_IOTLAB = os.path.join('topology', 'iotlab.json')
TOPOLOGY = pkg_resources.resource_filename('iotlab_radio_test', TOPOLOGY_IOTLAB)
SOCKET_TIMEOUT = 2

# Logs dirs and subdirs
LOG_DIR = "experiments"
RAW_DIR = "raw"
PARSED_DIR = "parsed"
IMAGE_DIR = "image"

SERIAL_AGGREGATOR = 'serial_aggregator'
