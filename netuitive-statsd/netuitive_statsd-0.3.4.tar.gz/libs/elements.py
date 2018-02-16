
import logging
import netuitive

from . import statsd

logger = logging.getLogger(__name__)


class Elements(object):
    """ manage list of elements
    """

    def __init__(self, hostname, element_obj):
        self.hostname = hostname
        self.element = element_obj
        self.elements = {}
        self.elements[self.hostname] = self.element

    def add(self, metricId, ts, val, metricType, sign=None, rate=None,
            tags=[], elementId=None):
        """ add an element (if needed), metrics, and samples
        """

        logger.debug('Element.add for metricId: {0}, '
                     'ts: {1},'
                     'val: {2}, '
                     'metricType:{3}, '
                     'sign: {4}, '
                     'rate: {5}, '
                     'tags: {6}, '
                     'elementId: {7}'.format(str(metricId),
                                             str(ts),
                                             str(val),
                                             str(metricType),
                                             str(sign),
                                             str(rate),
                                             str(tags),
                                             str(elementId)))

        try:
            timestamp = int(ts)

            value = float(val)

            if elementId is None:
                elementId = self.hostname

            if elementId not in self.elements:
                logger.debug('creating element:' + str(elementId))
                self.elements[elementId] = Element(
                    elementId, self.element.element.type)

            self.elements[elementId].add_sample(
                metricId, timestamp, value, metricType, sign, rate, tags)

        except Exception as e:
            logger.error(e, exc_info=True)
            raise(e)

    def delete(self, elementId):
        del self.elements[elementId]

    def delete_all(self):
        self.elements = {}
        self.element.metrics = {}
        self.elements[self.hostname] = self.element

    def clear_samples(self, elementId=None, everything=False):
        logger.debug('Element.clear_samples for ' + str(elementId))
        try:
            if elementId is None and everything is True:
                for ename in self.elements:
                    e = self.elements[ename]
                    e.clear_samples()

            else:
                e = self.elements[elementId]
                e.clear_samples()

        except Exception as e:
            logger.error(e, exc_info=True)


class Element(object):

    """
    An entity that represents an element
    """

    def __init__(self, elementId, ElementType=None):
        logger.debug('__init__ for Element')

        self.element = netuitive.Element(ElementType)
        self.elementId = elementId
        self.metrics = {}

        self.metric_types = {'c': 'COUNTER',
                             'g': 'GAUGE',
                             'ms': 'TIMER',
                             's': 'SET',
                             'h': 'HISTOGRAM'}

    def add_attribute(self, name, value):
        self.element.add_attribute(name, value)

    def add_tag(self, name, value):
        self.element.add_tag(name, value)

    def clear_samples(self):
        self.metrics.clear()
        self.element.clear_samples()

    def add_sample(self, metricId, ts, value, metricType, sign=None,
                   rate=None, tags=[]):

        logger.debug('add_sample')

        unit = ''
        sparseDataStrategy = 'None'
        metric_tags = []

        try:

            timestamp = int(ts)
            mtype = self.metric_types[metricType]

            # process tags
            for t in tags:
                # check for unit tag
                if 'un' in t:
                    unit = t['un']
                    metric_tags.append(t)
                # check for sparse data tag
                elif 'sds' in t:
                    sparseDataStrategy = t['sds']
                    metric_tags.append(t)

                # check for element type
                elif 'ty' in t:
                    self.element.type = t['ty']

                else:
                    metric_tags.append(t)

            del tags

            if metricId in self.metrics:

                if mtype not in self.metrics[metricId].orgtype:
                    otype = self.metric_types[
                        self.metrics[metricId].tags[0]['statsdType']]
                    logger.error("metric {0} changed from type {1} "
                                 "to type {2}".format(metricId, otype, mtype))

                    del self.metrics[metricId]

            if mtype == 'GAUGE':
                if metricId not in self.metrics:
                    self.metrics[metricId] = statsd.Gauge(
                        metricId, sparseDataStrategy, unit, metric_tags)

                self.metrics[metricId].add_value(value, timestamp, sign)

            if mtype == 'COUNTER':
                if metricId not in self.metrics:
                    self.metrics[metricId] = statsd.Counter(
                        metricId, sparseDataStrategy, unit, metric_tags)

                self.metrics[metricId].add_value(
                    value, timestamp, rate, sign)

            if mtype == 'HISTOGRAM' or mtype == 'TIMER':
                if metricId not in self.metrics:
                    self.metrics[metricId] = statsd.Histogram(
                        metricId, sparseDataStrategy, unit, metric_tags)

                self.metrics[metricId].add_value(
                    value, timestamp)

            if mtype == 'SET':
                if metricId not in self.metrics:
                    self.metrics[metricId] = statsd.Set(
                        metricId, sparseDataStrategy, unit, metric_tags)

                self.metrics[metricId].add_value(value, timestamp)

        except Exception as e:
            logger.error(e, exc_info=True)
            print(e)
            raise(e)

    def prepare(self):
        """
        prepare the metrics/samples for posting to the api
        """

        try:
            logger.debug('starting prepare')

            for m in self.metrics:

                metric = self.metrics[m]
                samples = metric.get_values(statsd.util.get_timestamp())
                metricType = metric.metricType
                sparseDataStrategy = metric.sparseDataStrategy
                unit = metric.unit

                tags = metric.tags

                if len(tags) == 0:
                    tags = None

                for name in samples:
                    d = samples[name]
                    mmin = None
                    mmax = None
                    mavg = None
                    msum = None
                    mcnt = None

                    timestamp = d['timestamp']
                    value = d['value']

                    if 'min' in d:
                        mmin = d['min']

                    if 'max' in d:
                        mmax = d['max']

                    if 'avg' in d:
                        mavg = d['avg']

                    if 'sum' in d:
                        msum = d['sum']

                    if 'cnt' in d:
                        mcnt = d['cnt']

                    self.element.add_sample(
                        name,
                        timestamp,
                        value,
                        metricType,
                        self.elementId,
                        sparseDataStrategy,
                        unit,
                        tags,
                        mmin,
                        mmax,
                        mavg,
                        msum,
                        mcnt,
                        ts_is_ms=True)

                    # since our results are ready for posting
                    metric.clear()

            logger.debug('finished prepare')

        except Exception as e:
            raise(e)
