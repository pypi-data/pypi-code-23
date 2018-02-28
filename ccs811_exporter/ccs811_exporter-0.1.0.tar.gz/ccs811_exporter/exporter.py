import logging
from prometheus_client import Counter, Gauge
from time import sleep

_LOG_MESSAGE_FORMAT = "   ".join(["temp: {temp:.2f} C",
                                  "eco2: {eco2:}ppm",
                                  "tvoc: {tvoc:}ppb"])
_METRICS = {
    # Gauges
    'eco2': ('ccs811_eco2_ppm', "Current CCS811 eCO2 level"),
    'temp': ('ccs811_temperature_celsius', "Current CCS811 temperature"),
    'tvoc': ('ccs811_tvoc_ppb', "Current CCS811 TVOC level"),
    
    # Counters
    'io_errors': ('ccs811_io_errors_total', "Total CCS811 I/O errors"),
    'io_reads': ('ccs811_io_reads_total', "Total CCS811 I/O reads")
}
_WAIT_DELAY = 0.1

logger = logging.getLogger(__name__)


def _gauge(metric, labels=None):
    """Initialize and return a Gauge object"""
    if labels is None:
        labels = {}
    label_keys = list(labels.keys())
    label_values = [labels[k] for k in label_keys]
    gauge = Gauge(*metric, label_keys)
    if len(label_values):
        gauge = gauge.labels(*label_values)
    return gauge


def _counter(metric, labels=None):
    """Initialize and return a Gauge object"""
    if labels is None:
        labels = {}
    label_keys = list(labels.keys())
    label_values = [labels[k] for k in label_keys]
    counter = Counter(*metric, label_keys)
    if len(label_values):
        counter = counter.labels(*label_values)
    return counter


class CCS811Exporter:
    """Collects and exports metrics for a single CCS811 sensor"""
    def __init__(self, ccs811, metrics=_METRICS, labels=None):
        self.ccs811 = ccs811
        self.temp = None
        self.eco2 = None
        self.tvoc = None
        self.eco2_gauge = _gauge(metrics['eco2'], labels)
        self.temp_gauge = _gauge(metrics['temp'], labels)
        self.tvoc_gauge = _gauge(metrics['tvoc'], labels)
        self.ioread_counter = _counter(metrics['io_reads'], labels)
        self.ioerror_counter = _counter(metrics['io_errors'], labels)

    def wait(self):
        """Wait for the CCS811 to become available"""
        self.ioread_counter.inc()
        try:
            while not self.ccs811.available():
                sleep(_WAIT_DELAY)
                pass
            return True
        except IOError:
            logger.error("IOError raised when determining CCS811 availability")
            self.ioerror_counter.inc()
        return False

    def calibrate(self, temp, humidity):
        """Update CCS811 with external temperature and humidity data"""
        pass

    def measure(self):
        """Read CCS811 measurements"""
        # if not self.wait():
        #     return
        
        self.ioread_counter.inc()
        try:
            self.temp = self.ccs811.calculateTemperature()
            result = self.ccs811.readData()
        except IOError:
            logger.error("IOError raised while reading CCS811 data")
            self.ioerror_counter.inc()
            return
        
        if result != 0:
            logger.error("CCS811 returned {} when reading data".format(result))
            return
        
        self.eco2 = self.ccs811.geteCO2()
        self.tvoc = self.ccs811.getTVOC()
        logger.info(_LOG_MESSAGE_FORMAT
                    .format(temp=self.temp,
                            eco2=self.eco2,
                            tvoc=self.tvoc))

    def export(self):
        """Export CCS811 metrics to Prometheus"""
        self.temp_gauge.set(self.temp)
        self.eco2_gauge.set(self.eco2)
        self.tvoc_gauge.set(self.tvoc)
